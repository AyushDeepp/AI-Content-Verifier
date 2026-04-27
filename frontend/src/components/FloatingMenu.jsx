import React, { useState, useEffect, useRef } from "react";
import { Link, useLocation } from "react-router-dom";
import { FaChartLine, FaFileAlt, FaImage, FaVideo, FaUserCircle, FaHome, FaBars, FaTimes } from "react-icons/fa";
import { useAuth } from "../context/AuthContext";
import "./FloatingMenu.css";

const FloatingMenu = () => {
  const [isOpen, setIsOpen] = useState(false);
  const location = useLocation();
  const { isAuthenticated } = useAuth();
  const menuRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (menuRef.current && !menuRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener("mousedown", handleClickOutside);
    } else {
      document.removeEventListener("mousedown", handleClickOutside);
    }

    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [isOpen]);

  const menuItems = [
    { path: "/", icon: FaHome, label: "Home" },
    ...(isAuthenticated ? [{ path: "/dashboard", icon: FaChartLine, label: "Dashboard" }] : []),
    { path: "/text", icon: FaFileAlt, label: "Text" },
    { path: "/image", icon: FaImage, label: "Image" },
    { path: "/video", icon: FaVideo, label: "Video" },
    ...(isAuthenticated ? [{ path: "/profile", icon: FaUserCircle, label: "Profile" }] : []),
  ];

  return (
    <div className={`floating-menu-container ${isOpen ? "open" : ""}`} ref={menuRef}>
      <div className="floating-menu-list">
        {menuItems.map((item) => (
          <Link
            key={item.path}
            to={item.path}
            className={`floating-menu-item ${location.pathname === item.path ? "active" : ""}`}
            onClick={() => setIsOpen(false)}
          >
            <item.icon className="floating-item-icon" />
            <span className="floating-item-label">{item.label}</span>
          </Link>
        ))}
      </div>

      <button 
        className="floating-menu-trigger" 
        onClick={() => setIsOpen(!isOpen)}
        aria-label="Toggle Menu"
      >
        {isOpen ? <FaTimes /> : <FaBars />}
      </button>
    </div>
  );
};

export default FloatingMenu;
