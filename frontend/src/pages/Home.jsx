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
import "./Home_sections.css";

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
            {/* Enhanced Hero Section */}
            <section className="home-hero">
                <div className="hero-background">
                    <div className="hero-gradient-orb orb-1"></div>
                    <div className="hero-gradient-orb orb-2"></div>
                    <div className="hero-gradient-orb orb-3"></div>
                </div>

                <div className="hero-container">
                    <div className="hero-content">
                        <h1 className="hero-title">
                            Detect AI Content
                            <br />
                            with <span className="highlight">Precision</span>
                        </h1>

                        <p className="hero-subtitle">
                            Advanced multi-model AI detection for text, images, and videos.
                            Get instant, accurate results with detailed analysis powered by
                            Google's Gemini 2.0 Flash.
                        </p>

                        <div className="hero-stats">
                            <div className="stat-item">
                                <FaCheckCircle className="stat-icon" />
                                <div className="stat-content">
                                    <span className="stat-number">95%+</span>
                                    <span className="stat-label">Accuracy</span>
                                </div>
                            </div>
                            <div className="stat-item">
                                <FaBolt className="stat-icon" />
                                <div className="stat-content">
                                    <span className="stat-number">Instant</span>
                                    <span className="stat-label">Results</span>
                                </div>
                            </div>
                            <div className="stat-item">
                                <FaShieldAlt className="stat-icon" />
                                <div className="stat-content">
                                    <span className="stat-number">100%</span>
                                    <span className="stat-label">Secure</span>
                                </div>
                            </div>
                        </div>

                        <div className="hero-buttons">
                            <Link to="/signup" className="hero-button primary">
                                <span>Get Started Free</span>
                                <FaArrowRight className="button-icon" />
                            </Link>
                            <Link to="/text" className="hero-button secondary">
                                <FaFileAlt className="button-icon" />
                                <span>Try Demo</span>
                            </Link>
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
                        <h3 className="step-title">Upload Content</h3>
                        <p className="step-description">
                            Upload your text, image, or video file to our secure platform
                        </p>
                    </div>
                    <div className="step-card">
                        <div className="step-number">2</div>
                        <div className="step-icon">
                            <FaRobot />
                        </div>
                        <h3 className="step-title">AI Analysis</h3>
                        <p className="step-description">
                            Our advanced AI models analyze your content using multiple
                            detection methods
                        </p>
                    </div>
                    <div className="step-card">
                        <div className="step-number">3</div>
                        <div className="step-icon">
                            <FaCheckCircle />
                        </div>
                        <h3 className="step-title">Get Results</h3>
                        <p className="step-description">
                            Receive instant, detailed results with confidence scores and
                            analysis
                        </p>
                    </div>
                </div>
            </section>

            {/* Features Section */}
            <section className="features-section">
                <div className="section-header">
                    <h2 className="section-title">Powerful Features</h2>
                    <p className="section-subtitle">
                        Everything you need to detect AI-generated content
                    </p>
                </div>
                <div className="features-grid">
                    <div className="feature-card">
                        <div className="feature-icon">
                            <FaBolt />
                        </div>
                        <h3 className="feature-title">Lightning Fast</h3>
                        <p className="feature-description">
                            Get results in seconds with our optimized detection algorithms
                        </p>
                    </div>
                    <div className="feature-card">
                        <div className="feature-icon">
                            <FaShieldAlt />
                        </div>
                        <h3 className="feature-title">Highly Accurate</h3>
                        <p className="feature-description">
                            95%+ accuracy rate using state-of-the-art AI models
                        </p>
                    </div>
                    <div className="feature-card">
                        <div className="feature-icon">
                            <FaLock />
                        </div>
                        <h3 className="feature-title">Secure & Private</h3>
                        <p className="feature-description">
                            Your data is encrypted and never stored or shared
                        </p>
                    </div>
                    <div className="feature-card">
                        <div className="feature-icon">
                            <FaChartLine />
                        </div>
                        <h3 className="feature-title">Detailed Analysis</h3>
                        <p className="feature-description">
                            Get comprehensive reports with confidence scores and insights
                        </p>
                    </div>
                </div>
            </section>

            {/* Use Cases Section */}
            <section className="use-cases-section">
                <div className="section-header">
                    <h2 className="section-title">Who Uses AI Content Verifier?</h2>
                    <p className="section-subtitle">
                        Trusted by professionals across industries
                    </p>
                </div>
                <div className="use-cases-grid">
                    <div className="use-case-card">
                        <div className="use-case-icon">
                            <FaGraduationCap />
                        </div>
                        <h3 className="use-case-title">Educators</h3>
                        <p className="use-case-description">
                            Verify student submissions and maintain academic integrity
                        </p>
                    </div>
                    <div className="use-case-card">
                        <div className="use-case-icon">
                            <FaNewspaper />
                        </div>
                        <h3 className="use-case-title">Journalists</h3>
                        <p className="use-case-description">
                            Ensure content authenticity and combat misinformation
                        </p>
                    </div>
                    <div className="use-case-card">
                        <div className="use-case-icon">
                            <FaBuilding />
                        </div>
                        <h3 className="use-case-title">Businesses</h3>
                        <p className="use-case-description">
                            Protect brand reputation and verify marketing content
                        </p>
                    </div>
                    <div className="use-case-card">
                        <div className="use-case-icon">
                            <FaBriefcase />
                        </div>
                        <h3 className="use-case-title">Content Creators</h3>
                        <p className="use-case-description">
                            Verify originality and maintain content quality standards
                        </p>
                    </div>
                </div>
            </section>

            {/* CTA Section */}
            <section className="cta-section">
                <div className="cta-container">
                    <h2 className="cta-title">Ready to Detect AI Content?</h2>
                    <p className="cta-subtitle">
                        Join thousands of users who trust our AI detection platform
                    </p>
                    <div className="cta-buttons">
                        <Link to="/signup" className="cta-button primary">
                            Get Started Free
                        </Link>
                        <Link to="/text" className="cta-button secondary">
                            Try Demo
                        </Link>
                    </div>
                </div>
            </section>

            <Footer />
        </div>
    );
};

export default Home;
