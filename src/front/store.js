export const initialStore = () => {
  return {
    message: null,
    token: localStorage.getItem("jwt-token") || null, 
    todos: [
      { id: 1, title: "Make the bed", background: null },
      { id: 2, title: "Do my homework", background: null }
    ]
  }
}

export default function storeReducer(store, action = {}) {
  switch(action.type){
    case 'set_hello':
      return { ...store, message: action.payload };
      
    case 'add_task':
      const { id,  color } = action.payload
      return { ...store, todos: store.todos.map((todo) => (todo.id === id ? { ...todo, background: color } : todo)) };

    case 'set_token':
      localStorage.setItem("jwt-token", action.payload);
      return { ...store, token: action.payload };

    case 'logout':
      localStorage.removeItem("jwt-token");
      return { ...store, token: null };

    default:
      throw Error('Unknown action.');
  }    
}