import React from "react";
import { Link } from "react-router-dom";
import {
  FaShieldAlt,
  FaEnvelope,
  FaFacebook,
  FaTwitter,
  FaLinkedin,
  FaGithub,
} from "react-icons/fa";
import "./Footer.css";

const Footer = () => {
  return (
    <footer className="footer">
      <div className="footer-container">
        <div className="footer-content">
          <div className="footer-section">
            <div className="footer-brand">
              <FaShieldAlt className="footer-logo" />
              <h3 className="footer-brand-name">AI Content Verifier</h3>
              <p className="footer-brand-description">
                Detect AI-generated content with confidence. Verify text,
                images, and videos using advanced machine learning.
              </p>
            </div>
          </div>

          <div className="footer-section">
            <h4 className="footer-title">Quick Links</h4>
            <ul className="footer-links">
              <li>
                <Link to="/">Home</Link>
              </li>
              <li>
                <Link to="/about">About</Link>
              </li>
              <li>
                <Link to="/contact">Contact</Link>
              </li>
              <li>
                <Link to="/privacy">Privacy Policy</Link>
              </li>
            </ul>
          </div>

          <div className="footer-section">
            <h4 className="footer-title">Verification</h4>
            <ul className="footer-links">
              <li>
                <Link to="/text">Text Verification</Link>
              </li>
              <li>
                <Link to="/image">Image Verification</Link>
              </li>
              <li>
                <Link to="/video">Video Verification</Link>
              </li>
              <li>
                <Link to="/dashboard">Dashboard</Link>
              </li>
            </ul>
          </div>

          <div className="footer-section">
            <h4 className="footer-title">Contact Us</h4>
            <ul className="footer-contact">
              <li>
                <FaEnvelope className="footer-contact-icon" />
                <a href="mailto:support@aicontentverifier.com">
                  support@aicontentverifier.com
                </a>
              </li>
            </ul>
            <div className="footer-social">
              <a
                href="https://facebook.com"
                target="_blank"
                rel="noopener noreferrer"
                aria-label="Facebook"
              >
                <FaFacebook />
              </a>
              <a
                href="https://twitter.com"
                target="_blank"
                rel="noopener noreferrer"
                aria-label="Twitter"
              >
                <FaTwitter />
              </a>
              <a
                href="https://linkedin.com"
                target="_blank"
                rel="noopener noreferrer"
                aria-label="LinkedIn"
              >
                <FaLinkedin />
              </a>
              <a
                href="https://github.com"
                target="_blank"
                rel="noopener noreferrer"
                aria-label="GitHub"
              >
                <FaGithub />
              </a>
            </div>
          </div>
        </div>

        <div className="footer-bottom">
          <p className="footer-copyright">
            © {new Date().getFullYear()} AI Content Verifier. All rights
            reserved.
          </p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
