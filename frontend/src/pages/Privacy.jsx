import React from "react";
import { FaLock, FaUserShield, FaDatabase, FaEyeSlash } from "react-icons/fa";
import "./Privacy.css";

const Privacy = () => {
  const privacyPoints = [
    {
      icon: <FaLock />,
      title: "End-to-End Encryption",
      description: "All data transmissions are secured using enterprise-grade TLS 1.3 encryption protocols."
    },
    {
      icon: <FaEyeSlash />,
      title: "No Content Storage",
      description: "We do not store your uploaded text, images, or videos after analysis is complete."
    },
    {
      icon: <FaUserShield />,
      title: "Identity Protection",
      description: "Your personal details are never shared with third-party advertisers or data brokers."
    },
    {
      icon: <FaDatabase />,
      title: "Secure Infrastructure",
      description: "Our systems are hosted on highly secure, compliant cloud infrastructure."
    }
  ];

  return (
    <div className="privacy-page fade-in">
      <div className="privacy-hero">
        <h1 className="privacy-title">Privacy & Security</h1>
        <p className="privacy-subtitle">
          How we protect your data at Credence AI. Last updated: {new Date().toLocaleDateString()}
        </p>
      </div>

      <div className="privacy-content">
        <section className="privacy-section">
          <h2 className="section-title">Our Privacy Philosophy</h2>
          <p className="section-text">
            At Credence AI, we believe privacy is a fundamental right. Our system is designed 
            with <strong>Privacy by Design</strong> principles, ensuring that your content 
            remains your own throughout the verification process.
          </p>
        </section>

        <section className="privacy-section">
          <h2 className="section-title">Core Protections</h2>
          <div className="privacy-points-grid">
            {privacyPoints.map((point, index) => (
              <div key={index} className="privacy-point-card">
                <div className="point-icon">{point.icon}</div>
                <div className="point-info">
                  <h3>{point.title}</h3>
                  <p>{point.description}</p>
                </div>
              </div>
            ))}
          </div>
        </section>

        <section className="privacy-section">
          <h2 className="section-title">Data Collection & Use</h2>
          <div className="policy-block">
            <h3>Account Data</h3>
            <p>We collect minimal information required for account management: your name, email, and hashed password.</p>
          </div>
          <div className="policy-block">
            <h3>Analysis Data</h3>
            <p>During analysis, content is processed in volatile memory and is purged immediately after the session ends.</p>
          </div>
        </section>

        <section className="privacy-section">
          <h2 className="section-title">Your Control</h2>
          <p className="section-text">
            You maintain full control over your data. You can request account deletion at any time, 
            which will permanently remove all associated metadata from our systems.
          </p>
        </section>

        <section className="privacy-section contact-privacy">
          <h2 className="section-title">Contact Privacy Team</h2>
          <p className="section-text">
            If you have specific concerns about your data, reach out to us at: 
            <a href="mailto:privacy@credenceai.com" className="privacy-link"> privacy@credenceai.com</a>
          </p>
        </section>
      </div>
    </div>
  );
};

export default Privacy;
