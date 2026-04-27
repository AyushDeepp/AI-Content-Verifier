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
    FaFileAlt,
    FaLock,
    FaGraduationCap,
    FaChartBar,
    FaGlobe,
    FaChevronDown
} from "react-icons/fa";
import "./Home.css";

const Home = () => {
    const { isAuthenticated } = useAuth();
    const [quickText, setQuickText] = useState("");
    const [typedTitle, setTypedTitle] = useState("");
    const [isTypingDone, setIsTypingDone] = useState(false);
    const [expandedIndex, setExpandedIndex] = useState(null);
    const navigate = useNavigate();

    const fullTitle = "Detect AI Content with Confidence";

    const features = [
        {
            icon: <FaRobot />,
            title: "Multi-Modal Analysis",
            desc: "Seamlessly verify text, images, and videos using a unified AI detection core. Our cross-medium analysis ensures that no artificial artifact goes unnoticed.",
            isWide: true
        },
        {
            icon: <FaShieldAlt />,
            title: "99% Accuracy",
            desc: "Industry-standard precision for deepfake and LLM detection.",
            isWide: false
        },
        {
            icon: <FaBolt />,
            title: "Instant Results",
            desc: "Optimized processing engine delivering real-time verification scores.",
            isWide: false
        },
        {
            icon: <FaLock />,
            title: "Privacy-Centric Core",
            desc: "We process data in-memory and never persist sensitive uploads. Your privacy is built into the architecture from the ground up.",
            isWide: true
        },
        {
            icon: <FaGraduationCap />,
            title: "Academic Roots",
            desc: "Built as a research-backed Final Year Project.",
            isWide: false
        },
        {
            icon: <FaChartBar />,
            title: "Smart Metrics",
            desc: "Detailed breakdowns of detection confidence levels.",
            isWide: false
        },
        {
            icon: <FaGlobe />,
            title: "Global Ready",
            desc: "Universal detection for diverse linguistic and visual styles.",
            isWide: false
        }
    ];

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

    const toggleExpand = (index) => {
        // Only toggle on mobile (handled by CSS, but good to have logic)
        setExpandedIndex(expandedIndex === index ? null : index);
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

                {/* Redesigned Bento Grid with Mobile Accordion */}
                <section className="features-grid-section" id="features">
                    <div className="section-header-center">
                        <h2 className="section-title">Platform Features</h2>
                        <p className="section-subtitle">A high-performance detection engine built for modern authentication needs.</p>
                    </div>
                    <div className="clean-bento-grid">
                        {features.map((feature, index) => (
                            <div 
                                key={index} 
                                className={`bento-box ${feature.isWide ? 'bento-wide' : ''} ${expandedIndex === index ? 'is-expanded' : ''}`}
                                onClick={() => toggleExpand(index)}
                            >
                                <div className="bento-header">
                                    <div className="bento-icon-box">
                                        {feature.icon}
                                    </div>
                                    <h3 className="bento-title">{feature.title}</h3>
                                    <FaChevronDown className="mobile-chevron" />
                                </div>
                                <div className="bento-collapse-content">
                                    <p className="bento-desc">{feature.desc}</p>
                                </div>
                            </div>
                        ))}
                    </div>
                </section>

                {/* Minimalist Trust Bar */}
                <section className="trust-bar">
                    <div className="trust-item">
                        <FaCheckCircle className="trust-icon" />
                        <span>Academic Excellence</span>
                    </div>
                    <div className="trust-item">
                        <FaCheckCircle className="trust-icon" />
                        <span>Privacy Protected</span>
                    </div>
                    <div className="trust-item">
                        <FaCheckCircle className="trust-icon" />
                        <span>Real-time Insights</span>
                    </div>
                </section>
            </div>
        </div>
    );
};

export default Home;
