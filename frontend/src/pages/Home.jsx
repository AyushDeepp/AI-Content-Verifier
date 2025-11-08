import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import Footer from "../components/Footer";
import {
  FaFileAlt,
  FaImage,
  FaVideo,
  FaShieldAlt,
  FaBolt,
  FaLock,
  FaRobot,
  FaArrowRight,
  FaCheckCircle,
  FaGraduationCap,
  FaBuilding,
  FaNewspaper,
  FaBriefcase,
  FaChartLine,
} from "react-icons/fa";
import "./Home.css";

const Home = () => {
  const [quickText, setQuickText] = useState("");
  const navigate = useNavigate();

  const handleQuickVerify = (e) => {
    e.preventDefault();
    if (quickText.trim()) {
      // Store text in sessionStorage and navigate
      sessionStorage.setItem("quickText", quickText.trim());
      navigate("/text");
    }
  };

  return (
    <div className="home-page">
      {/* Hero Section - Side-by-side layout */}
      <section className="home-hero">
        <div className="hero-container">
        <div className="hero-content">
            <h1 className="hero-title">
              Verify AI Content with{" "}
              <span className="highlight">Confidence</span>
            </h1>
          <p className="hero-subtitle">
              Detect AI-generated text, images, and videos using advanced
              machine learning models. Get instant results with high accuracy.
          </p>
          <div className="hero-buttons">
              <Link to="/signup" className="hero-button primary">
                Get Started Free
            </Link>
            <Link to="/dashboard" className="hero-button secondary">
                View Dashboard
            </Link>
          </div>
        </div>
          <div className="hero-illustration">
            <div className="illustration-container">
              <FaShieldAlt className="illustration-icon" />
              <div className="illustration-glow"></div>
            </div>
          </div>
        </div>
      </section>

      {/* Quick Text Input Section */}
      <section className="quick-verify-section">
        <div className="quick-verify-container">
          <h2 className="quick-verify-title">
            Try it now - Paste text to verify
          </h2>
          <form onSubmit={handleQuickVerify} className="quick-verify-form">
            <textarea
              value={quickText}
              onChange={(e) => setQuickText(e.target.value)}
              placeholder="Paste or type text here to verify if it's AI-generated..."
              className="quick-text-input"
              rows="4"
            />
            <button
              type="submit"
              className="quick-verify-button"
              disabled={!quickText.trim()}
            >
              Verify Text <FaArrowRight />
            </button>
          </form>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="how-it-works-section">
        <div className="section-header">
          <h2 className="section-title">How It Works</h2>
          <p className="section-subtitle">
            Three simple steps to verify your content
          </p>
        </div>
        <div className="steps-container">
          <div className="step-card">
            <div className="step-number">1</div>
            <div className="step-icon">
              <FaFileAlt />
            </div>
            <h3 className="step-title">Upload</h3>
            <p className="step-description">
              Upload your text, image, or video content to be analyzed
            </p>
          </div>
          <div className="step-connector">
            <FaArrowRight />
          </div>
          <div className="step-card">
            <div className="step-number">2</div>
            <div className="step-icon">
              <FaRobot />
            </div>
            <h3 className="step-title">Analyze</h3>
            <p className="step-description">
              Our AI models analyze patterns and features in your content
            </p>
          </div>
          <div className="step-connector">
            <FaArrowRight />
          </div>
          <div className="step-card">
            <div className="step-number">3</div>
            <div className="step-icon">
              <FaCheckCircle />
            </div>
            <h3 className="step-title">Result</h3>
            <p className="step-description">
              Get instant results with confidence scores and detailed insights
            </p>
          </div>
      </div>
      </section>

      {/* Verification Preview Cards */}
      <section className="verification-preview-section">
        <div className="section-header">
          <h2 className="section-title">Verification Types</h2>
          <p className="section-subtitle">
            Choose the verification method that fits your needs
          </p>
        </div>
        <div className="preview-grid">
          <div className="preview-card">
            <div className="preview-icon">
              <FaFileAlt />
            </div>
            <h3 className="preview-title">Text Verification</h3>
            <p className="preview-description">
              Detect AI-generated text by analyzing linguistic patterns, style,
              and structure. Perfect for articles, essays, and documents.
            </p>
            <div className="preview-demo">
              <div className="demo-text">
                "The quick brown fox jumps over the lazy dog..."
              </div>
              <div className="demo-result">
                <span className="demo-label">Confidence:</span>
                <span className="demo-value">85%</span>
              </div>
            </div>
            <Link to="/text" className="preview-link">
              Try Text Verification <FaArrowRight />
            </Link>
          </div>

          <div className="preview-card">
            <div className="preview-icon">
              <FaImage />
            </div>
            <h3 className="preview-title">Image Verification</h3>
            <p className="preview-description">
              Identify AI-generated images using advanced computer vision
              models. Detect synthetic content in photos and graphics.
            </p>
            <div className="preview-demo">
              <div className="demo-placeholder">
                <FaImage className="demo-placeholder-icon" />
              </div>
              <div className="demo-result">
                <span className="demo-label">Confidence:</span>
                <span className="demo-value">92%</span>
              </div>
            </div>
            <Link to="/image" className="preview-link">
              Try Image Verification <FaArrowRight />
            </Link>
          </div>

          <div className="preview-card">
            <div className="preview-icon">
              <FaVideo />
            </div>
            <h3 className="preview-title">Video Verification</h3>
            <p className="preview-description">
              Analyze videos for AI-generated content. Detect deepfakes and
              synthetic video materials with frame-by-frame analysis.
            </p>
            <div className="preview-demo">
              <div className="demo-placeholder">
                <FaVideo className="demo-placeholder-icon" />
              </div>
              <div className="demo-result">
                <span className="demo-label">Confidence:</span>
                <span className="demo-value">78%</span>
              </div>
            </div>
            <Link to="/video" className="preview-link">
              Try Video Verification <FaArrowRight />
            </Link>
          </div>
        </div>
      </section>

      {/* Trust Bar - Thin horizontal */}
      <section className="trust-bar-section">
        <div className="trust-bar">
          <div className="trust-item">
            <FaShieldAlt className="trust-icon" />
            <span className="trust-text">AI-Powered</span>
          </div>
          <div className="trust-separator"></div>
          <div className="trust-item">
            <FaLock className="trust-icon" />
            <span className="trust-text">Secure</span>
          </div>
          <div className="trust-separator"></div>
          <div className="trust-item">
            <FaBolt className="trust-icon" />
            <span className="trust-text">Fast</span>
          </div>
        </div>
      </section>

      {/* Why Verify AI Content Section */}
      <section className="why-verify-section">
        <div className="why-verify-container">
          <div className="why-verify-content">
            <h2 className="section-title">Why Verify AI Content?</h2>
            <div className="reasons-grid">
              <div className="reason-card">
                <div className="reason-icon">
                  <FaShieldAlt />
                </div>
                <h3 className="reason-title">Content Authenticity</h3>
                <p className="reason-description">
                  Ensure the content you're reading or using is authentic and
                  human-created. Verify sources before trusting them.
                </p>
              </div>
              <div className="reason-card">
                <div className="reason-icon">
                  <FaCheckCircle />
                </div>
                <h3 className="reason-title">Academic Integrity</h3>
                <p className="reason-description">
                  Maintain academic standards by verifying student work and
                  research papers for AI-generated content.
                </p>
              </div>
              <div className="reason-card">
                <div className="reason-icon">
                  <FaLock />
                </div>
                <h3 className="reason-title">Business Protection</h3>
                <p className="reason-description">
                  Protect your business from misinformation and verify content
                  before publishing or sharing with stakeholders.
                </p>
              </div>
          </div>
        </div>
      </div>
      </section>

      {/* Live Demo Section */}
      <section className="live-demo-section">
        <div className="section-header">
          <h2 className="section-title">Live Demo</h2>
          <p className="section-subtitle">See how it works in real-time</p>
        </div>
        <div className="demo-container">
          <div className="demo-card">
            <div className="demo-header">
              <div className="demo-status">
                <span className="status-dot"></span>
                Live Analysis
              </div>
              <FaChartLine className="demo-icon" />
            </div>
            <div className="demo-content">
              <div className="demo-text-preview">
                "Artificial intelligence is revolutionizing the way we interact
                with technology. Machine learning algorithms analyze vast
                amounts of data to identify patterns and make predictions..."
              </div>
              <div className="demo-result-preview">
                <div className="demo-result-item">
                  <span className="demo-label">Type:</span>
                  <span className="demo-value">Text</span>
                </div>
                <div className="demo-result-item">
                  <span className="demo-label">Result:</span>
                  <span className="demo-value ai-detected">AI Generated</span>
          </div>
                <div className="demo-result-item">
                  <span className="demo-label">Confidence:</span>
                  <span className="demo-value">87%</span>
          </div>
          </div>
        </div>
      </div>
        </div>
      </section>

      {/* Trusted By Section */}
      <section className="trusted-by-section">
        <div className="section-header">
          <h2 className="section-title">Trusted By</h2>
          <p className="section-subtitle">
            Used by professionals across various industries
          </p>
        </div>
        <div className="trusted-grid">
          <div className="trusted-item">
            <FaGraduationCap className="trusted-icon" />
            <h3 className="trusted-title">Education</h3>
            <p className="trusted-description">
              Universities and schools verify academic integrity
            </p>
          </div>
          <div className="trusted-item">
            <FaBuilding className="trusted-icon" />
            <h3 className="trusted-title">Business</h3>
            <p className="trusted-description">
              Companies verify content authenticity and compliance
            </p>
          </div>
          <div className="trusted-item">
            <FaNewspaper className="trusted-icon" />
            <h3 className="trusted-title">Media</h3>
            <p className="trusted-description">
              News organizations ensure content credibility
            </p>
          </div>
          <div className="trusted-item">
            <FaBriefcase className="trusted-icon" />
            <h3 className="trusted-title">Legal</h3>
            <p className="trusted-description">
              Law firms verify document authenticity
            </p>
          </div>
        </div>
      </section>

      {/* CTA Footer Section */}
      <section className="cta-footer-section">
        <div className="cta-footer-container">
          <h2 className="cta-title">Ready to Start Verifying?</h2>
          <p className="cta-subtitle">
            Join thousands of users who trust our AI content verification
            platform
          </p>
          <div className="cta-buttons">
            <Link to="/signup" className="cta-button primary">
              Create Free Account
            </Link>
            <Link to="/dashboard" className="cta-button secondary">
              Explore Dashboard
            </Link>
          </div>
        </div>
      </section>
      <Footer />
    </div>
  );
};

export default Home;
