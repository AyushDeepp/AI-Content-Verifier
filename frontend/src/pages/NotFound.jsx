import React from "react";
import { Link } from "react-router-dom";
import { FaExclamationTriangle, FaArrowLeft } from "react-icons/fa";

const NotFound = () => {
  return (
    <div className="verifier-page fade-in" style={{ textAlign: 'center', justifyContent: 'center', minHeight: '60vh' }}>
      <div className="card verifier-card">
        <FaExclamationTriangle style={{ fontSize: '3rem', color: 'var(--accent)', marginBottom: '1.5rem' }} />
        <h1 className="page-title">404 - Page Not Found</h1>
        <p className="page-subtitle">The page you are looking for doesn't exist or has been moved.</p>
        <Link to="/" className="btn btn-primary" style={{ marginTop: '1rem' }}>
          <FaArrowLeft /> Back to Home
        </Link>
      </div>
    </div>
  );
};

export default NotFound;
