import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import Navbar from "../components/Navbar";
import Sidebar from "../components/Sidebar";
import { FaShieldAlt, FaEnvelope, FaLock, FaArrowRight } from "react-icons/fa";
import "./Login.css";

const Login = () => {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  const toggleSidebar = () => {
    setIsSidebarOpen(!isSidebarOpen);
  };

  const closeSidebar = () => {
    setIsSidebarOpen(false);
  };
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    const result = await login(email, password);
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
              <h2>Welcome Back</h2>
              <p>Sign in to verify AI-generated content with confidence</p>
              <div className="illustration-features">
                <div className="feature-item">
                  <FaShieldAlt className="feature-icon" />
                  <span>Secure & Private</span>
                </div>
                <div className="feature-item">
                  <FaArrowRight className="feature-icon" />
                  <span>Instant Results</span>
                </div>
              </div>
            </div>
          </div>

          <div className="auth-form-container">
            <div className="auth-form">
              <h1 className="auth-title">Welcome Back</h1>
              <p className="auth-subtitle">Sign in to continue</p>

              {error && <div className="error-message">{error}</div>}

              <form onSubmit={handleSubmit}>
                <div className="form-group">
                  <label htmlFor="email">
                    <FaEnvelope className="label-icon" />
                    Email
                  </label>
                  <input
                    type="email"
                    id="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
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
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                    placeholder="Enter your password"
                  />
                </div>

                <button
                  type="submit"
                  className="auth-button primary"
                  disabled={loading}
                >
                  {loading ? "Signing in..." : "Sign In"}
                </button>
              </form>

              <p className="auth-footer">
                Don't have an account?{" "}
                <Link to="/signup" className="auth-link">
                  Sign up
                </Link>
              </p>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default Login;
