import React, { useState, useEffect } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { FaUser, FaSignOutAlt } from "react-icons/fa";
import ThemeToggle from "./ThemeToggle";
import "./Navbar.css";

const Navbar = () => {
  const { user, logout, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [isScrolled, setIsScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 20);
    };
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  const scrollToFeatures = (e) => {
    if (location.pathname === "/") {
      e.preventDefault();
      const featuresSection = document.getElementById("features");
      if (featuresSection) {
        featuresSection.scrollIntoView({ behavior: "smooth" });
      }
    }
  };

  const isActive = (path) => location.pathname === path;

  return (
    <nav className={`navbar-wrapper ${isScrolled ? "scrolled" : ""}`}>
      <div className="navbar-container">
        <div className="navbar-left">
          <Link to="/" className="navbar-logo">
            <div className="logo-box">
              <img src="/ailogo.png" alt="Credence AI Logo" className="logo-img" />
            </div>
            <span className="logo-text">Credence AI</span>
          </Link>
        </div>

        <div className="navbar-center">
          <Link to="/" className={`nav-link ${isActive("/") ? "active" : ""}`}>Home</Link>
          <Link to="/about" className={`nav-link ${isActive("/about") ? "active" : ""}`}>About</Link>
          <Link 
            to="/#features" 
            className="nav-link"
            onClick={scrollToFeatures}
          >
            Features
          </Link>
        </div>

        <div className="navbar-right">
          <ThemeToggle />
          {isAuthenticated ? (
            <div className="navbar-profile">
              <div className="profile-trigger">
                <div className="profile-avatar">
                  {user?.full_name?.charAt(0).toUpperCase() || "U"}
                </div>
                <div className="profile-dropdown">
                  <Link to="/profile" className="dropdown-item">
                    <FaUser /> <span>Profile</span>
                  </Link>
                  <button onClick={handleLogout} className="dropdown-item">
                    <FaSignOutAlt /> <span>Logout</span>
                  </button>
                </div>
              </div>
            </div>
          ) : (
            <div className="navbar-auth">
              <Link to="/login" className="nav-link-auth">Login</Link>
              <Link to="/signup" className="btn btn-primary btn-pill">Sign Up</Link>
            </div>
          )}
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
