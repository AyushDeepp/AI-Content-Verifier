import React, { useState } from "react";
import { Link, useLocation } from "react-router-dom";
import {
  FaChartLine,
  FaFileAlt,
  FaImage,
  FaVideo,
  FaUserCircle,
  FaHome,
} from "react-icons/fa";
import { useAuth } from "../context/AuthContext";
import "./Sidebar.css";

const Sidebar = ({ isOpen, onClose }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const location = useLocation();
  const { isAuthenticated } = useAuth();

  const menuItems = [
    { path: "/", icon: FaHome, label: "Home" },
    ...(isAuthenticated
      ? [{ path: "/dashboard", icon: FaChartLine, label: "Dashboard" }]
      : []),
    { path: "/text", icon: FaFileAlt, label: "Text" },
    { path: "/image", icon: FaImage, label: "Image" },
    { path: "/video", icon: FaVideo, label: "Video" },
    ...(isAuthenticated
      ? [{ path: "/profile", icon: FaUserCircle, label: "Profile" }]
      : []),
  ];

  const isActive = (path) => location.pathname === path;

  // Close sidebar on mobile when clicking a link
  const handleLinkClick = () => {
    if (window.innerWidth <= 480 && onClose) {
      onClose();
    }
  };

  // Handle mouse enter/leave only on desktop
  const handleMouseEnter = () => {
    if (window.innerWidth > 480) {
      setIsExpanded(true);
    }
  };

  const handleMouseLeave = () => {
    if (window.innerWidth > 480) {
      setIsExpanded(false);
    }
  };

  return (
    <>
      {/* Overlay for mobile */}
      {isOpen && onClose && (
        <div className="sidebar-overlay" onClick={onClose} />
      )}
      <aside
        className={`sidebar ${isExpanded ? "expanded" : ""} ${
          isOpen ? "mobile-open" : ""
        }`}
        onMouseEnter={handleMouseEnter}
        onMouseLeave={handleMouseLeave}
      >
        <nav className="sidebar-nav">
          {menuItems.map((item) => {
            const IconComponent = item.icon;
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`sidebar-item ${
                  isActive(item.path) ? "active" : ""
                }`}
                title={item.label}
                onClick={handleLinkClick}
              >
                <IconComponent className="sidebar-icon" />
                <span className="sidebar-label">{item.label}</span>
              </Link>
            );
          })}
        </nav>
      </aside>
    </>
  );
};

export default Sidebar;
