import React from "react";
import Footer from "../components/Footer";
import { FaShieldAlt, FaBrain, FaLock, FaChartLine } from "react-icons/fa";
import "./About.css";

const About = () => {
  const features = [
    {
      icon: <FaBrain />,
      title: "Advanced AI Detection",
      description:
        "Our cutting-edge machine learning models analyze content patterns to identify AI-generated text, images, and videos with high accuracy.",
    },
    {
      icon: <FaShieldAlt />,
      title: "Secure & Private",
      description:
        "Your data is encrypted and secure. We respect your privacy and never store sensitive content without your permission.",
    },
    {
      icon: <FaChartLine />,
      title: "Real-time Analysis",
      description:
        "Get instant verification results with detailed confidence scores and explanations to help you understand the detection process.",
    },
    {
      icon: <FaLock />,
      title: "Trusted Technology",
      description:
        "Built with modern security practices and continuously updated to detect the latest AI generation techniques.",
    },
  ];

  return (
    <div className="about-page">
      <div className="about-hero">
        <h1 className="about-title">About AI Content Verifier</h1>
        <p className="about-subtitle">
          Empowering trust and authenticity in the digital age
        </p>
      </div>

      <div className="about-content">
        <section className="about-section">
          <h2 className="section-title">Our Mission</h2>
          <p className="section-text">
            In an era where AI-generated content is becoming increasingly
            sophisticated, distinguishing between human-created and AI-generated
            content is crucial. AI Content Verifier provides a reliable,
            user-friendly platform to verify the authenticity of text, images,
            and videos.
          </p>
          <p className="section-text">
            We believe in transparency and trust. Our mission is to help
            individuals, educators, businesses, and content creators maintain
            authenticity in their digital communications.
          </p>
        </section>

        <section className="about-section">
          <h2 className="section-title">Key Features</h2>
          <div className="features-grid">
            {features.map((feature, index) => (
              <div key={index} className="feature-card">
                <div className="feature-icon">{feature.icon}</div>
                <h3 className="feature-title">{feature.title}</h3>
                <p className="feature-description">{feature.description}</p>
              </div>
            ))}
          </div>
        </section>

        <section className="about-section">
          <h2 className="section-title">How It Works</h2>
          <div className="how-it-works">
            <div className="step-item">
              <div className="step-number">1</div>
              <div className="step-content">
                <h3>Upload Content</h3>
                <p>
                  Upload your text, image, or video content through our
                  intuitive interface.
                </p>
              </div>
            </div>
            <div className="step-item">
              <div className="step-number">2</div>
              <div className="step-content">
                <h3>AI Analysis</h3>
                <p>
                  Our advanced algorithms analyze patterns, structures, and
                  artifacts to detect AI generation.
                </p>
              </div>
            </div>
            <div className="step-item">
              <div className="step-number">3</div>
              <div className="step-content">
                <h3>Get Results</h3>
                <p>
                  Receive detailed results with confidence scores and
                  explanations of the detection process.
                </p>
              </div>
            </div>
          </div>
        </section>

        <section className="about-section">
          <h2 className="section-title">Technology</h2>
          <p className="section-text">
            AI Content Verifier leverages state-of-the-art machine learning
            models trained on diverse datasets to identify AI-generated content.
            Our models continuously learn and adapt to new generation
            techniques, ensuring high accuracy and reliability.
          </p>
          <p className="section-text">
            Built with modern web technologies including React for the frontend
            and FastAPI for the backend, ensuring fast, secure, and scalable
            performance.
          </p>
        </section>
      </div>
      <Footer />
    </div>
  );
};

export default About;
