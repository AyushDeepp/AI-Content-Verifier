import React, { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import {
    FaShieldAlt,
    FaBolt,
    FaRobot,
    FaArrowRight,
    FaCheckCircle,
    FaUpload,
    FaMagic,
    FaFileAlt
} from "react-icons/fa";
import "./Home.css";

const Home = () => {
    const { isAuthenticated } = useAuth();
    const [quickText, setQuickText] = useState("");
    const [typedTitle, setTypedTitle] = useState("");
    const [isTypingDone, setIsTypingDone] = useState(false);
    const navigate = useNavigate();

    const fullTitle = "Detect AI Content with Confidence";

    useEffect(() => {
        let index = 0;
        const typingInterval = setInterval(() => {
            if (index <= fullTitle.length) {
                setTypedTitle(fullTitle.slice(0, index));
                index++;
            } else {
                clearInterval(typingInterval);
                setTimeout(() => setIsTypingDone(true), 500);
            }
        }, 60);

        return () => clearInterval(typingInterval);
    }, []);

    const handleQuickVerify = (e) => {
        e.preventDefault();
        if (quickText.trim()) {
            sessionStorage.setItem("quickText", quickText.trim());
            navigate("/text");
        }
    };

    return (
        <div className="home-page fade-in">
            {/* Hero Section */}
            <section className="hero" id="home">
                <div className="hero-container">
                    <h1 className="hero-title">
                        {typedTitle}<span className="cursor">|</span>
                    </h1>
                    
                    <div className={`hero-content-delayed ${isTypingDone ? "visible" : ""}`}>
                        <p className="hero-subtitle">
                            The professional tool for verifying text, images, and videos. 
                            Powered by state-of-the-art AI detection models.
                        </p>
                        <div className="hero-actions">
                            {!isAuthenticated ? (
                                <>
                                    <Link to="/signup" className="btn btn-primary btn-glow">
                                        Get Started Free
                                    </Link>
                                    <Link to="/text" className="btn btn-secondary">
                                        Try Demo
                                    </Link>
                                </>
                            ) : (
                                <Link to="/dashboard" className="btn btn-primary btn-glow">
                                    Go to Dashboard
                                </Link>
                            )}
                        </div>
                    </div>
                </div>
            </section>

            <div className={`home-rest-content ${isTypingDone ? "visible" : ""}`}>
                {/* Integrated Quick Verify */}
                <section className="quick-verify">
                    <div className="card glass quick-verify-card">
                        <h2 className="card-title">Quick Verification</h2>
                        <p className="card-subtitle">Paste text below to check for AI generation signals.</p>
                        <form onSubmit={handleQuickVerify} className="quick-verify-form">
                            <textarea
                                value={quickText}
                                onChange={(e) => setQuickText(e.target.value)}
                                placeholder="Type or paste your text here..."
                                className="quick-textarea"
                            />
                            <button
                                type="submit"
                                className="btn btn-primary"
                                disabled={!quickText.trim()}
                            >
                                Analyze Text <FaArrowRight />
                            </button>
                        </form>
                    </div>
                </section>

                {/* How to Use Section */}
                <section className="how-to-use-section">
                    <div className="section-header-center">
                        <h2 className="section-title">How to use?</h2>
                        <p className="section-subtitle">Get started with Credence AI in three simple steps.</p>
                    </div>
                    <div className="steps-container">
                        <div className="step-card">
                            <div className="step-icon-box">
                                <FaUpload />
                            </div>
                            <h3>1. Input Content</h3>
                            <p>Upload your image, video or paste your text into our specialized verifiers.</p>
                        </div>
                        <div className="step-connector"></div>
                        <div className="step-card">
                            <div className="step-icon-box">
                                <FaMagic />
                            </div>
                            <h3>2. AI Analysis</h3>
                            <p>Our deep learning models scan for structural patterns and AI artifacts.</p>
                        </div>
                        <div className="step-connector"></div>
                        <div className="step-card">
                            <div className="step-icon-box">
                                <FaFileAlt />
                            </div>
                            <h3>3. Detailed Report</h3>
                            <p>Receive a comprehensive confidence score and authenticity breakdown.</p>
                        </div>
                    </div>
                </section>

                {/* Features Grid */}
                <section className="features-grid-section" id="features">
                    <div className="section-header-center">
                        <h2 className="section-title">Why Credence AI?</h2>
                        <p className="section-subtitle">Advanced detection capabilities across multiple mediums.</p>
                    </div>
                    <div className="feature-grid-container">
                        <div className="card feature-card">
                            <div className="feature-icon-wrapper">
                                <FaBolt className="feature-icon" />
                            </div>
                            <h3 className="feature-title">Lightning Fast</h3>
                            <p className="feature-description">
                                Get accurate results in seconds with our optimized processing engine.
                            </p>
                        </div>
                        <div className="card feature-card">
                            <div className="feature-icon-wrapper">
                                <FaShieldAlt className="feature-icon" />
                            </div>
                            <h3 className="feature-title">High Accuracy</h3>
                            <p className="feature-description">
                                Industry-leading detection rates for GPT-4, Gemini, and Claude models.
                            </p>
                        </div>
                        <div className="card feature-card">
                            <div className="feature-icon-wrapper">
                                <FaRobot className="feature-icon" />
                            </div>
                            <h3 className="feature-title">Multi-Modal</h3>
                            <p className="feature-description">
                                The only platform supporting Text, Image, and Video AI detection.
                            </p>
                        </div>
                    </div>
                </section>

                {/* Minimalist Trust Bar */}
                <section className="trust-bar">
                    <div className="trust-item">
                        <FaCheckCircle className="trust-icon" />
                        <span>99% Uptime Detection</span>
                    </div>
                    <div className="trust-item">
                        <FaCheckCircle className="trust-icon" />
                        <span>Privacy Protected</span>
                    </div>
                    <div className="trust-item">
                        <FaCheckCircle className="trust-icon" />
                        <span>Enterprise Ready</span>
                    </div>
                </section>
            </div>
        </div>
    );
};

export default Home;
