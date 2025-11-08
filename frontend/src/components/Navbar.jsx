import React from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { useTheme } from "../context/ThemeContext";
import {
  FaShieldAlt,
  FaUser,
  FaSignOutAlt,
  FaBars,
  FaTimes,
} from "react-icons/fa";
import ThemeToggle from "./ThemeToggle";
import "./Navbar.css";

const Navbar = ({ onMenuToggle, isMenuOpen }) => {
  const { user, logout, isAuthenticated } = useAuth();
  const { theme } = useTheme();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <nav className={`navbar navbar-${theme}`}>
      <div className="navbar-container">
        <div className="navbar-left">
          <button
            className="mobile-menu-toggle"
            onClick={onMenuToggle}
            aria-label="Toggle menu"
          >
            {isMenuOpen ? <FaTimes /> : <FaBars />}
          </button>
          <Link to="/" className="navbar-logo">
            <FaShieldAlt className="logo-icon" />
            <span className="logo-text">AI Verifier</span>
          </Link>
        </div>

        <div className="navbar-right">
          <ThemeToggle />
          {isAuthenticated ? (
            <div className="navbar-profile">
              <div className="profile-menu">
                <div className="profile-avatar">
                  {user?.full_name?.charAt(0).toUpperCase() || "U"}
                </div>
                <div className="profile-dropdown">
                  <Link to="/profile" className="dropdown-item">
                    <FaUser className="dropdown-icon" />
                    Profile
                  </Link>
                  <button onClick={handleLogout} className="dropdown-item">
                    <FaSignOutAlt className="dropdown-icon" />
                    Logout
                  </button>
                </div>
              </div>
            </div>
          ) : (
            <div className="navbar-auth">
              <Link to="/login" className="auth-link">
                Login
              </Link>
              <Link to="/signup" className="auth-link primary">
                Sign Up
              </Link>
            </div>
          )}
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
