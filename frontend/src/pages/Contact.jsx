import React, { useState } from "react";
import {
  FaEnvelope,
  FaMapMarkerAlt,
  FaClock,
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
      setSuccess("Thank you! Your message has been sent successfully.");
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
    <div className="contact-page fade-in">
      <div className="contact-hero">
        <h1 className="contact-title">Contact Us</h1>
        <p className="contact-subtitle">
          Have questions about Credence AI? Reach out to our team.
        </p>
      </div>

      <div className="contact-content-grid">
        <div className="contact-sidebar">
          <div className="contact-info-card">
            <div className="info-item-small">
              <FaEnvelope className="info-icon" />
              <div>
                <h3>Email</h3>
                <p>support@credenceai.com</p>
              </div>
            </div>
            <div className="info-item-small">
              <FaMapMarkerAlt className="info-icon" />
              <div>
                <h3>Availability</h3>
                <p>Global / Remote</p>
              </div>
            </div>
            <div className="info-item-small">
              <FaClock className="info-icon" />
              <div>
                <h3>Response Time</h3>
                <p>Within 24 Hours</p>
              </div>
            </div>
          </div>
        </div>

        <div className="contact-form-main">
          <div className="card glass contact-form-card">
            <h2 className="form-title">Send a Message</h2>
            {error && <div className="error-msg">{error}</div>}
            {success && <div className="success-msg">{success}</div>}
            
            <form onSubmit={handleSubmit} className="contact-form">
              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="name">Full Name</label>
                  <input
                    type="text"
                    id="name"
                    name="name"
                    value={formData.name}
                    onChange={handleChange}
                    required
                    placeholder="John Doe"
                    className="form-input"
                  />
                </div>
                <div className="form-group">
                  <label htmlFor="email">Email Address</label>
                  <input
                    type="email"
                    id="email"
                    name="email"
                    value={formData.email}
                    onChange={handleChange}
                    required
                    placeholder="name@company.com"
                    className="form-input"
                  />
                </div>
              </div>
              <div className="form-group">
                <label htmlFor="message">Message</label>
                <textarea
                  id="message"
                  name="message"
                  value={formData.message}
                  onChange={handleChange}
                  required
                  rows="5"
                  placeholder="How can we help you?"
                  className="form-input"
                />
              </div>
              <button
                type="submit"
                className="btn btn-primary submit-button"
                disabled={loading}
              >
                <FaPaperPlane style={{marginRight: '0.5rem'}} /> 
                {loading ? "Sending..." : "Send Message"}
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Contact;
