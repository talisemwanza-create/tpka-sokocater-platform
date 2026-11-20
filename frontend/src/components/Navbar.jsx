import { Link, NavLink } from "react-router-dom";

function Navbar() {
  return (
    <nav className="navbar">
      <Link to="/" className="brand">
        Soko<span>Cater</span>
      </Link>

      <div className="nav-links">
        <NavLink to="/">Home</NavLink>
        <NavLink to="/caterers">Find Catering</NavLink>
        <a href="/#categories">Categories</a>
        <a href="/#about">About</a>
      </div>

      <div className="nav-actions">
        <Link to="/caterer/dashboard" className="provider-link">
          Caterer Portal
        </Link>
        <Link to="/login" className="nav-button">
          Login
        </Link>
        <Link to="/signup" className="nav-button">
          Sign Up
        </Link>
      </div>
    </nav>
  );
}

export default Navbar;