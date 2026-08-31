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

          <Link to="/notifications">
            Notifications
          </Link>

          <Link to="/profile">
            Profile
          </Link>


          {/* ================================================= */}
          {/* ADMIN LINKS */}
          {/* ================================================= */}

          {user?.role === "admin" && (
            <>
              <Link to="/admin/dashboard">
                Dashboard
              </Link>

              <Link to="/admin/products">
                Admin Products
              </Link>

              <Link to="/admin/reports">
                Reports
              </Link>
            </>
          )}


          {/* ================================================= */}
          {/* LOGOUT */}
          {/* ================================================= */}

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