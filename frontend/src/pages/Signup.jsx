import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { FaUser, FaEnvelope, FaLock } from "react-icons/fa";
import Navbar from "../components/Navbar";
import FloatingMenu from "../components/FloatingMenu";
import Footer from "../components/Footer";
import "../styles/auth.css";

const Signup = () => {
  const [formData, setFormData] = useState({ fullName: "", email: "", password: "", confirmPassword: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e) => setFormData({ ...formData, [e.target.name]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    if (formData.password !== formData.confirmPassword) return setError("Passwords do not match");
    if (formData.password.length < 6) return setError("Password must be at least 6 characters");
    setLoading(true);
    const result = await register(formData.email, formData.password, formData.fullName);
    setLoading(false);
    if (result.success) navigate("/dashboard");
    else setError(result.error);
  };

  return (
    <div className="auth-page-container">
      <Navbar />
      <FloatingMenu />
      <main className="auth-page fade-in">
        <div className="card auth-card">
          <div className="auth-header">
            <div className="auth-logo-wrapper">
              <img src="/ailogo.png" alt="Credence AI Logo" className="auth-logo-img" />
            </div>
            <h1 className="auth-title">Create Account</h1>
            <p className="auth-subtitle">Join Credence AI to start verifying your content authenticity.</p>
          </div>

          {error && <div className="error-msg">{error}</div>}

          <form onSubmit={handleSubmit} className="auth-form">
            <div className="form-group">
              <label>
                <FaUser className="form-icon-inline" /> Full Name
              </label>
              <input 
                type="text" 
                name="fullName" 
                value={formData.fullName} 
                onChange={handleChange} 
                required 
                className="form-input" 
                placeholder="John Doe" 
              />
            </div>
            <div className="form-group">
              <label>
                <FaEnvelope className="form-icon-inline" /> Email Address
              </label>
              <input 
                type="email" 
                name="email" 
                value={formData.email} 
                onChange={handleChange} 
                required 
                className="form-input" 
                placeholder="name@company.com" 
              />
            </div>
            <div className="form-group">
              <label>
                <FaLock className="form-icon-inline" /> Password
              </label>
              <input 
                type="password" 
                name="password" 
                value={formData.password} 
                onChange={handleChange} 
                required 
                className="form-input" 
                placeholder="••••••••" 
              />
            </div>
            <div className="form-group">
              <label>
                <FaLock className="form-icon-inline" /> Confirm Password
              </label>
              <input 
                type="password" 
                name="confirmPassword" 
                value={formData.confirmPassword} 
                onChange={handleChange} 
                required 
                className="form-input" 
                placeholder="••••••••" 
              />
            </div>
            <button type="submit" className="btn btn-primary auth-btn" disabled={loading}>
              {loading ? "Creating..." : "Sign Up"}
            </button>
          </form>

          <p className="auth-footer">
            Already have an account? <Link to="/login">Sign in</Link>
          </p>
        </div>
      </main>
      <Footer />
    </div>
  );
};

export default Signup;
