import React, { useState } from "react";
import Footer from "../components/Footer";
import {
  FaEnvelope,
  FaMapMarkerAlt,
  FaPhone,
  FaPaperPlane,
} from "react-icons/fa";
import { contactAPI } from "../utils/api";
import "./Contact.css";

const Contact = () => {
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    message: "",
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSuccess("");
    setLoading(true);

    try {
      await contactAPI.submit(formData);
      setSuccess("Thank you for your message! We'll get back to you soon.");
      setFormData({ name: "", email: "", message: "" });
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          "Failed to send message. Please try again."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="contact-page">
      <div className="contact-hero">
        <h1 className="contact-title">Get in Touch</h1>
        <p className="contact-subtitle">
          Have questions or feedback? We'd love to hear from you!
        </p>
      </div>

      <div className="contact-content">
        <div className="contact-info">
          <div className="info-card">
            <FaEnvelope className="info-icon" />
            <h3>Email</h3>
            <p>support@aicontentverifier.com</p>
          </div>
          <div className="info-card">
            <FaMapMarkerAlt className="info-icon" />
            <h3>Location</h3>
            <p>Available Worldwide</p>
          </div>
          <div className="info-card">
            <FaPhone className="info-icon" />
            <h3>Response Time</h3>
            <p>We typically respond within 24 hours</p>
          </div>
        </div>

        <div className="contact-form-container">
          <div className="contact-form-card">
            <h2 className="form-title">Send us a Message</h2>
            {error && <div className="error-message">{error}</div>}
            {success && <div className="success-message">{success}</div>}
            <form onSubmit={handleSubmit} className="contact-form">
              <div className="form-group">
                <label htmlFor="name">Name</label>
                <input
                  type="text"
                  id="name"
                  name="name"
                  value={formData.name}
                  onChange={handleChange}
                  required
                  placeholder="Your name"
                />
              </div>
              <div className="form-group">
                <label htmlFor="email">Email</label>
                <input
                  type="email"
                  id="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  required
                  placeholder="your.email@example.com"
                />
              </div>
              <div className="form-group">
                <label htmlFor="message">Message</label>
                <textarea
                  id="message"
                  name="message"
                  value={formData.message}
                  onChange={handleChange}
                  required
                  rows="6"
                  placeholder="Your message here..."
                />
              </div>
              <button
                type="submit"
                className="submit-button"
                disabled={loading}
              >
                <FaPaperPlane /> {loading ? "Sending..." : "Send Message"}
              </button>
            </form>
          </div>
        </div>
      </div>
      <Footer />
    </div>
  );
};

export default Contact;
