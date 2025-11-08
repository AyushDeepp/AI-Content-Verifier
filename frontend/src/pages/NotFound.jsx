import React from "react";
import { Link } from "react-router-dom";
import { FaHome, FaArrowLeft, FaExclamationTriangle } from "react-icons/fa";
import "./NotFound.css";

const NotFound = () => {
  return (
    <div className="not-found-page">
      <div className="not-found-content">
        <div className="not-found-icon">
          <FaExclamationTriangle />
        </div>
        <h1 className="not-found-title">404</h1>
        <h2 className="not-found-subtitle">Page Not Found</h2>
        <p className="not-found-message">
          Oops! The page you're looking for doesn't exist or has been moved.
        </p>
        <div className="not-found-actions">
          <Link to="/" className="not-found-button primary">
            <FaHome /> Go Home
          </Link>
          <button
            onClick={() => window.history.back()}
            className="not-found-button secondary"
          >
            <FaArrowLeft /> Go Back
          </button>
        </div>
      </div>
    </div>
  );
};

export default NotFound;
