import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import Navbar from "../components/Navbar";
import Sidebar from "../components/Sidebar";
import {
  FaShieldAlt,
  FaUser,
  FaEnvelope,
  FaLock,
  FaCheckCircle,
  FaArrowRight,
} from "react-icons/fa";
import "./Signup.css";

const Signup = () => {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  const toggleSidebar = () => {
    setIsSidebarOpen(!isSidebarOpen);
  };

  const closeSidebar = () => {
    setIsSidebarOpen(false);
  };
  const [formData, setFormData] = useState({
    fullName: "",
    email: "",
    password: "",
    confirmPassword: "",
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    if (formData.password !== formData.confirmPassword) {
      setError("Passwords do not match");
      return;
    }

    if (formData.password.length < 6) {
      setError("Password must be at least 6 characters");
      return;
    }

    setLoading(true);

    const result = await register(
      formData.email,
      formData.password,
      formData.fullName
    );
    setLoading(false);

    if (result.success) {
      navigate("/dashboard");
    } else {
      setError(result.error);
    }
  };

  return (
    <>
      <Navbar onMenuToggle={toggleSidebar} isMenuOpen={isSidebarOpen} />
      <Sidebar isOpen={isSidebarOpen} onClose={closeSidebar} />
      <div className="auth-page">
        <div className="auth-container">
          <div className="auth-illustration">
            <div className="illustration-content">
              <div className="illustration-icon-wrapper">
                <FaShieldAlt className="illustration-icon" />
                <div className="icon-glow"></div>
              </div>
              <h2>Get Started</h2>
              <p>Join thousands of users verifying content authenticity</p>
              <div className="illustration-features">
                <div className="feature-item">
                  <FaCheckCircle className="feature-icon" />
                  <span>Free to Use</span>
                </div>
                <div className="feature-item">
                  <FaShieldAlt className="feature-icon" />
                  <span>Secure Platform</span>
                </div>
                <div className="feature-item">
                  <FaArrowRight className="feature-icon" />
                  <span>Quick Setup</span>
                </div>
              </div>
            </div>
          </div>

          <div className="auth-form-container">
            <div className="auth-form">
              <h1 className="auth-title">Create Account</h1>
              <p className="auth-subtitle">Sign up to get started</p>

              {error && <div className="error-message">{error}</div>}

              <form onSubmit={handleSubmit}>
                <div className="form-group">
                  <label htmlFor="fullName">
                    <FaUser className="label-icon" />
                    Full Name
                  </label>
                  <input
                    type="text"
                    id="fullName"
                    name="fullName"
                    value={formData.fullName}
                    onChange={handleChange}
                    required
                    placeholder="Enter your full name"
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="email">
                    <FaEnvelope className="label-icon" />
                    Email
                  </label>
                  <input
                    type="email"
                    id="email"
                    name="email"
                    value={formData.email}
                    onChange={handleChange}
                    required
                    placeholder="Enter your email"
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="password">
                    <FaLock className="label-icon" />
                    Password
                  </label>
                  <input
                    type="password"
                    id="password"
                    name="password"
                    value={formData.password}
                    onChange={handleChange}
                    required
                    placeholder="Create a password (min. 6 characters)"
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="confirmPassword">
                    <FaLock className="label-icon" />
                    Confirm Password
                  </label>
                  <input
                    type="password"
                    id="confirmPassword"
                    name="confirmPassword"
                    value={formData.confirmPassword}
                    onChange={handleChange}
                    required
                    placeholder="Confirm your password"
                  />
                </div>

                <button
                  type="submit"
                  className="auth-button primary"
                  disabled={loading}
                >
                  {loading ? "Creating account..." : "Sign Up"}
                </button>
              </form>

              <p className="auth-footer">
                Already have an account?{" "}
                <Link to="/login" className="auth-link">
                  Sign in
                </Link>
              </p>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default Signup;
