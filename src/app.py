"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for, send_from_directory
from flask_migrate import Migrate
from flask_swagger import swagger
from api.utils import APIException, generate_sitemap
from api.models import db,User
from api.routes import api
from api.admin import setup_admin
from api.commands import setup_commands
from flask_jwt_extended import JWTManager,create_access_token,jwt_required


# from models import Person

#Configuracion de llave secre

ENV = "development" if os.getenv("FLASK_DEBUG") == "1" else "production"
static_file_dir = os.path.join(os.path.dirname(
    os.path.realpath(__file__)), '../dist/')
app = Flask(__name__)
app.url_map.strict_slashes = False
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
jwt = JWTManager(app)

# database condiguration
db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace(
        "postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db, compare_type=True)
db.init_app(app)

# add the admin
setup_admin(app)

# add the admin
setup_commands(app)

# Add all endpoints form the API with a "api" prefix
app.register_blueprint(api, url_prefix='/api')

# Handle/serialize errors like a JSON object


@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints


@app.route('/')
def sitemap():
    if ENV == "development":
        return generate_sitemap(app)
    return send_from_directory(static_file_dir, 'index.html')

# any other endpoint will try to serve it like a static file
@app.route('/<path:path>', methods=['GET'])
def serve_any_other_file(path):
    if not os.path.isfile(os.path.join(static_file_dir, path)):
        path = 'index.html'
    response = send_from_directory(static_file_dir, path)
    response.cache_control.max_age = 0  # avoid cache memory
    return response


#/////////////////////////
@app.route('/register',methods=["POST"])
def register():

    
    body=request.get_json()

    if body is None:
        return jsonify({"msg":"Body is empty"}),200
    
    email= body.get("email")
    password = body.get("password")

    if not email or not password:
        return jsonify({"msg":"Email o contrasena requerridos"}),400
    
    new_user= User(email=email,password=password,is_active=True)
    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"msg":"Usuario creado"}),201
    except Exception as e:
        return jsonify({"msg":"Error al guardar: " + str(e)}),500

   

#////////////////
@app.route('/login',methods=['POST'])
def login():
    email = request.json.get("email",None)
    password = request.json.get("password",None)

    user = User.query.filter_by(email=email,password=password).first()

    if user is None:
        return jsonify({"msg":"Incorrect email/password"}),401
    
    access_token = create_access_token(identity=str(user.id))
    return jsonify({"token": access_token,"user_id" : user.id}),200

#////////////////////////////
@app.route('/users',methods=['GET'])
@jwt_required()
def get_users():
    users=User.query.all()
    all_users=list(map(lambda user : user.serialize(),users))
    return jsonify(all_users),200


    

# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3001))
    app.run(host='0.0.0.0', port=PORT, debug=True)
