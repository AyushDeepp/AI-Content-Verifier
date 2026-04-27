import React from "react";
import { Link } from "react-router-dom";
import { FaTwitter, FaGithub, FaLinkedin } from "react-icons/fa";
import "./Footer.css";

const Footer = () => {
  return (
    <footer className="footer">
      <div className="footer-container">
        <div className="footer-brand">
          <Link to="/" className="footer-logo">
            <div className="logo-box-small">
              <img src="/ailogo.png" alt="Credence AI Logo" className="logo-img" />
            </div>
            <span>Credence AI</span>
          </Link>
          <p className="footer-tagline">
            Ensuring digital integrity through advanced AI detection and verification.
          </p>
          <div className="footer-socials">
            {/* eslint-disable-next-line jsx-a11y/anchor-is-valid */}
            <a href="#" aria-label="Twitter"><FaTwitter /></a>
            {/* eslint-disable-next-line jsx-a11y/anchor-is-valid */}
            <a href="#" aria-label="GitHub"><FaGithub /></a>
            {/* eslint-disable-next-line jsx-a11y/anchor-is-valid */}
            <a href="#" aria-label="LinkedIn"><FaLinkedin /></a>
          </div>
        </div>

        <div className="footer-links-group">
          <div className="footer-column">
            <h4>Product</h4>
            <Link to="/text">Text Verifier</Link>
            <Link to="/image">Image Verifier</Link>
            <Link to="/video">Video Verifier</Link>
          </div>
          <div className="footer-column">
            <h4>Company</h4>
            <Link to="/about">About Us</Link>
            <Link to="/contact">Contact</Link>
            <Link to="/privacy">Privacy</Link>
          </div>
        </div>
      </div>
      <div className="footer-bottom">
        <p>&copy; {new Date().getFullYear()} Credence AI. All rights reserved.</p>
        <p>Innovation in verification.</p>
      </div>
    </footer>
  );
};

export default Footer;
