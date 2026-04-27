import React, { useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { FaChartLine, FaFileAlt, FaImage, FaVideo, FaUserCircle, FaHome } from "react-icons/fa";
import { useAuth } from "../context/AuthContext";
import "./Sidebar.css";

const Sidebar = ({ isOpen, onClose }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const location = useLocation();
  const { isAuthenticated } = useAuth();

  const menuItems = [
    { path: "/", icon: FaHome, label: "Home" },
    ...(isAuthenticated ? [{ path: "/dashboard", icon: FaChartLine, label: "Dashboard" }] : []),
    { path: "/text", icon: FaFileAlt, label: "Text" },
    { path: "/image", icon: FaImage, label: "Image" },
    { path: "/video", icon: FaVideo, label: "Video" },
    ...(isAuthenticated ? [{ path: "/profile", icon: FaUserCircle, label: "Profile" }] : []),
  ];

  return (
    <>
      {isOpen && <div className="sidebar-overlay" onClick={onClose} />}
      <aside
        className={`sidebar ${isExpanded ? "expanded" : ""} ${isOpen ? "mobile-open" : ""}`}
        onMouseEnter={() => setIsExpanded(true)}
        onMouseLeave={() => setIsExpanded(false)}
      >
        <div className="sidebar-nav">
          {menuItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className={`sidebar-item ${location.pathname === item.path ? "active" : ""}`}
              onClick={() => isOpen && onClose()}
            >
              <div className="sidebar-icon-wrapper">
                <item.icon className="sidebar-icon" />
              </div>
              <span className="sidebar-label">{item.label}</span>
            </Link>
          ))}
        </div>
      </aside>
    </>
  );
};

export default Sidebar;
