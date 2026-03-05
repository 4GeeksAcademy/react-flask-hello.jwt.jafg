import React from "react";
import { Link, useNavigate } from "react-router-dom";
import useGlobalReducer from "../hooks/useGlobalReducer";

export const Navbar = () => {
    const { store, dispatch } = useGlobalReducer();
    const navigate = useNavigate();

    const handleLogout = () => {
        dispatch({ type: "logout" });
        navigate("/login");
    };

    return (
        <nav className="navbar navbar-light bg-light mb-3 p-3">
            <Link to="/">
                <span className="navbar-brand mb-0 h1"></span>
            </Link>
            <div className="ml-auto">
                
                {store.token ? (
                    <button className="btn btn-danger" onClick={handleLogout}>Cerrar Sesión</button>
                ) : (
                    <Link to="/login" className="btn btn-primary">Iniciar Sesión</Link>
                )}
            </div>
        </nav>
    );
};