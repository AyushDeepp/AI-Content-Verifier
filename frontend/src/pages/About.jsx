import React from "react";
import { FaShieldAlt, FaBrain, FaLock, FaChartLine, FaGraduationCap } from "react-icons/fa";
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
    <div className="about-page fade-in">
      <div className="about-hero">
        <h1 className="about-title">About Credence AI</h1>
        <p className="about-subtitle">
          Empowering trust and authenticity in the digital age
        </p>
      </div>

      <div className="about-content">
        {/* Project Context Section */}
        <section className="about-section academic-section">
          <div className="academic-badge">
            <FaGraduationCap /> Final Year Project
          </div>
          <h2 className="section-title">Academic Initiative</h2>
          <p className="section-text">
            Credence AI is a sophisticated AI content detection system developed as a 
            <strong> Final Year Project</strong>. It represents the culmination of academic 
            research and technical implementation in the field of artificial intelligence and 
            digital security.
          </p>
          <div className="team-container">
            <h3>Developed By:</h3>
            <div className="team-grid">
              <div className="team-member">
                <span className="member-name">Ayush Deep</span>
              </div>
              <div className="team-member">
                <span className="member-name">Charu Sarswat</span>
              </div>
              <div className="team-member">
                <span className="member-name">Amrendra Kumar Singh</span>
              </div>
              <div className="team-member">
                <span className="member-name">Sonu Rauniyar</span>
              </div>
            </div>
          </div>
        </section>

        <section className="about-section">
          <h2 className="section-title">Our Mission</h2>
          <p className="section-text">
            In an era where AI-generated content is becoming increasingly
            sophisticated, distinguishing between human-created and AI-generated
            content is crucial. Credence AI provides a reliable,
            user-friendly platform to verify the authenticity of text, images,
            and videos.
          </p>
        </section>

        <section className="about-section">
          <h2 className="section-title">Key Capabilities</h2>
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
          <h2 className="section-title">Technology Stack</h2>
          <p className="section-text">
            Credence AI leverages state-of-the-art machine learning
            models trained on diverse datasets to identify AI-generated content.
            Our models continuously learn and adapt to new generation
            techniques, ensuring high accuracy and reliability.
          </p>
          <p className="section-text">
            Built with a modern stack featuring **React** for the intuitive frontend experience 
            and **FastAPI** for a high-performance, scalable backend infrastructure.
          </p>
        </section>
      </div>
    </div>
  );
};

export default About;
