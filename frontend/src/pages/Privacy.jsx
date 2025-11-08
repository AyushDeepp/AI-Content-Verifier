import React from "react";
import Footer from "../components/Footer";
import { FaLock, FaShieldAlt, FaUserShield, FaDatabase } from "react-icons/fa";
import "./Privacy.css";

const Privacy = () => {
  const privacyPoints = [
    {
      icon: <FaLock />,
      title: "Data Encryption",
      description:
        "All data transmitted to and from our servers is encrypted using industry-standard SSL/TLS protocols.",
    },
    {
      icon: <FaShieldAlt />,
      title: "Content Privacy",
      description:
        "We do not store your content without explicit permission. Text content is only stored if you choose to save verification results.",
    },
    {
      icon: <FaUserShield />,
      title: "User Data Protection",
      description:
        "Your personal information is protected and never shared with third parties without your consent.",
    },
    {
      icon: <FaDatabase />,
      title: "Secure Storage",
      description:
        "All stored data is kept in secure databases with regular backups and access controls.",
    },
  ];

  return (
    <div className="privacy-page">
      <div className="privacy-hero">
        <h1 className="privacy-title">Privacy Policy</h1>
        <p className="privacy-subtitle">
          Last updated: {new Date().toLocaleDateString()}
        </p>
      </div>

      <div className="privacy-content">
        <section className="privacy-section">
          <h2 className="section-title">Introduction</h2>
          <p className="section-text">
            At AI Content Verifier, we take your privacy seriously. This Privacy
            Policy explains how we collect, use, disclose, and safeguard your
            information when you use our service.
          </p>
        </section>

        <section className="privacy-section">
          <h2 className="section-title">Information We Collect</h2>
          <div className="info-list">
            <div className="info-item">
              <h3>Account Information</h3>
              <p>
                When you create an account, we collect your name, email address,
                and a securely hashed password.
              </p>
            </div>
            <div className="info-item">
              <h3>Verification Data</h3>
              <p>
                We may store metadata about your verifications (type, result,
                confidence, timestamp) to provide dashboard statistics. Text
                content is only stored if you choose to save results.
              </p>
            </div>
            <div className="info-item">
              <h3>Usage Data</h3>
              <p>
                We collect anonymous usage statistics to improve our service,
                including feature usage and performance metrics.
              </p>
            </div>
          </div>
        </section>

        <section className="privacy-section">
          <h2 className="section-title">How We Use Your Information</h2>
          <ul className="usage-list">
            <li>To provide and maintain our verification service</li>
            <li>To display your verification history and statistics</li>
            <li>To improve and optimize our detection algorithms</li>
            <li>To respond to your inquiries and provide support</li>
            <li>To send important service updates and notifications</li>
          </ul>
        </section>

        <section className="privacy-section">
          <h2 className="section-title">Data Security</h2>
          <div className="security-grid">
            {privacyPoints.map((point, index) => (
              <div key={index} className="security-card">
                <div className="security-icon">{point.icon}</div>
                <h3 className="security-title">{point.title}</h3>
                <p className="security-description">{point.description}</p>
              </div>
            ))}
          </div>
        </section>

        <section className="privacy-section">
          <h2 className="section-title">Your Rights</h2>
          <p className="section-text">You have the right to:</p>
          <ul className="rights-list">
            <li>Access your personal data</li>
            <li>Request correction of inaccurate data</li>
            <li>Request deletion of your account and data</li>
            <li>Export your verification data</li>
            <li>Opt-out of non-essential communications</li>
          </ul>
        </section>

        <section className="privacy-section">
          <h2 className="section-title">Third-Party Services</h2>
          <p className="section-text">
            We use trusted third-party services for hosting, analytics, and
            email delivery. These services are bound by their own privacy
            policies and security standards.
          </p>
        </section>

        <section className="privacy-section">
          <h2 className="section-title">Contact Us</h2>
          <p className="section-text">
            If you have questions about this Privacy Policy or wish to exercise
            your rights, please contact us at{" "}
            <a
              href="mailto:privacy@aicontentverifier.com"
              className="privacy-link"
            >
              privacy@aicontentverifier.com
            </a>
          </p>
        </section>
      </div>
      <Footer />
    </div>
  );
};

export default Privacy;
