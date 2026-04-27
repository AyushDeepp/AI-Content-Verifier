import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { FaEnvelope, FaLock } from "react-icons/fa";
import Navbar from "../components/Navbar";
import FloatingMenu from "../components/FloatingMenu";
import Footer from "../components/Footer";
import "../styles/auth.css";

const Login = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(""); setLoading(true);
    const result = await login(email, password);
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
            <h1 className="auth-title">Welcome Back</h1>
            <p className="auth-subtitle">Log in to Credence AI to verify your content.</p>
          </div>

          {error && <div className="error-msg">{error}</div>}

          <form onSubmit={handleSubmit} className="auth-form">
            <div className="form-group">
              <label>
                <FaEnvelope className="form-icon-inline" /> Email Address
              </label>
              <input 
                type="email" 
                value={email} 
                onChange={(e) => setEmail(e.target.value)} 
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
                value={password} 
                onChange={(e) => setPassword(e.target.value)} 
                required 
                className="form-input" 
                placeholder="••••••••" 
              />
            </div>
            <button type="submit" className="btn btn-primary auth-btn" disabled={loading}>
              {loading ? "Signing in..." : "Sign In"}
            </button>
          </form>

          <p className="auth-footer">
            Don't have an account? <Link to="/signup">Create account</Link>
          </p>
        </div>
      </main>
      <Footer />
    </div>
  );
};

export default Login;
