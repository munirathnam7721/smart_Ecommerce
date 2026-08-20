import { Link, useNavigate } from "react-router-dom";
import { getCurrentUser, logout } from "../api";

function Navbar() {
  const navigate = useNavigate();
  const user = getCurrentUser();

  function handleLogout() {
    logout();
    navigate("/");
  }

  return (
    <header className="navbar">
      <div className="navbar-inner">
        <Link
          to="/products"
          className="brand"
        >
          Smart E-Commerce
        </Link>

        <nav className="nav-links">
          <Link to="/products">
            Products
          </Link>

          <Link to="/cart">
            Cart
          </Link>

          <Link to="/orders">
            Orders
          </Link>

          <Link to="/profile">
            Profile
          </Link>

          {user?.role === "admin" && (
            <Link to="/admin/products">
              Admin
            </Link>
          )}

          <button
            className="nav-button"
            onClick={handleLogout}
          >
            Logout
          </button>
        </nav>
      </div>
    </header>
  );
}

export default Navbar;