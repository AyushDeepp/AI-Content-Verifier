import React, { useState } from "react";
import { useAuth } from "../context/AuthContext";
import { authAPI } from "../utils/api";
import {
  FaUser,
  FaEnvelope,
  FaLock,
  FaSave,
  FaEdit,
  FaTimes,
} from "react-icons/fa";
import "./Profile.css";

const Profile = () => {
  const { user, fetchUser } = useAuth();
  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState({
    fullName: user?.full_name || "",
    email: user?.email || "",
  });
  const [passwordStep, setPasswordStep] = useState("initial"); // "initial", "validating", "new"
  const [currentPassword, setCurrentPassword] = useState("");
  const [passwordData, setPasswordData] = useState({
    newPassword: "",
    confirmPassword: "",
  });
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(false);

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handlePasswordChange = (e) => {
    if (e.target.name === "currentPassword") {
      setCurrentPassword(e.target.value);
    } else {
      setPasswordData({
        ...passwordData,
        [e.target.name]: e.target.value,
      });
    }
  };

  const handleSaveProfile = async (e) => {
    e.preventDefault();
    setError("");
    setSuccess("");
    setLoading(true);

    try {
      await authAPI.updateProfile({ full_name: formData.fullName });
      setSuccess("Profile updated successfully!");
      setIsEditing(false);
      // Refresh user data
      if (fetchUser) {
        await fetchUser();
      }
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to update profile");
    } finally {
      setLoading(false);
    }
  };

  const handleValidateCurrentPassword = async (e) => {
    e.preventDefault();
    setError("");
    setSuccess("");

    if (!currentPassword) {
      setError("Please enter your current password");
      return;
    }

    setLoading(true);
    setPasswordStep("validating");

    try {
      await authAPI.validatePassword({ current_password: currentPassword });
      setPasswordStep("new");
      setSuccess("Current password verified. Please enter your new password.");
    } catch (err) {
      setError(err.response?.data?.detail || "Current password is incorrect");
      setPasswordStep("initial");
      setCurrentPassword("");
    } finally {
      setLoading(false);
    }
  };

  const handleChangePassword = async (e) => {
    e.preventDefault();
    setError("");
    setSuccess("");

    if (passwordData.newPassword !== passwordData.confirmPassword) {
      setError("New passwords do not match");
      return;
    }

    if (passwordData.newPassword.length < 6) {
      setError("Password must be at least 6 characters");
      return;
    }

    setLoading(true);

    try {
      await authAPI.changePassword({
        current_password: currentPassword,
        new_password: passwordData.newPassword,
      });
      setSuccess("Password changed successfully!");
      setPasswordStep("initial");
      setCurrentPassword("");
      setPasswordData({
        newPassword: "",
        confirmPassword: "",
      });
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to change password");
    } finally {
      setLoading(false);
    }
  };

  const handleCancelPasswordChange = () => {
    setPasswordStep("initial");
    setCurrentPassword("");
    setPasswordData({
      newPassword: "",
      confirmPassword: "",
    });
    setError("");
    setSuccess("");
  };

  const handleCancel = () => {
    setFormData({
      fullName: user?.full_name || "",
      email: user?.email || "",
    });
    setIsEditing(false);
    setError("");
    setSuccess("");
  };

  return (
    <div className="profile-page">
      <div className="profile-header">
        <div className="profile-avatar-large">
          {user?.full_name?.charAt(0).toUpperCase() || "U"}
        </div>
        <div className="profile-info">
          <h1 className="profile-name">{user?.full_name}</h1>
          <p className="profile-email">{user?.email}</p>
        </div>
      </div>

      {error && <div className="error-message">{error}</div>}
      {success && <div className="success-message">{success}</div>}

      {/* Profile Information Section */}
      <div className="profile-section">
        <div className="profile-section-header">
          <h2 className="section-title">Profile Information</h2>
          {!isEditing && (
            <button className="edit-button" onClick={() => setIsEditing(true)}>
              <FaEdit /> Edit Profile
            </button>
          )}
        </div>

        {isEditing ? (
          <form onSubmit={handleSaveProfile} className="profile-form">
            <div className="form-group">
              <label htmlFor="fullName">
                <FaUser className="label-icon" />
                Full Name
              </label>
              <input
                type="text"
                id="fullName"
                name="fullName"
                value={formData.fullName}
                onChange={handleInputChange}
                required
                placeholder="Enter your full name"
              />
            </div>

            <div className="form-group">
              <label htmlFor="email">
                <FaEnvelope className="label-icon" />
                Email
              </label>
              <input
                type="email"
                id="email"
                name="email"
                value={formData.email}
                disabled
                placeholder="Email cannot be changed"
                className="email-disabled"
              />
            </div>

            <div className="form-actions">
              <button
                type="button"
                className="cancel-button"
                onClick={handleCancel}
              >
                <FaTimes /> Cancel
              </button>
              <button type="submit" className="save-button" disabled={loading}>
                <FaSave /> {loading ? "Saving..." : "Save Changes"}
              </button>
            </div>
          </form>
        ) : (
          <div className="profile-details">
            <div className="detail-item">
              <FaUser className="detail-icon" />
              <div className="detail-content">
                <span className="detail-label">Full Name</span>
                <span className="detail-value">{user?.full_name}</span>
              </div>
            </div>
            <div className="detail-item">
              <FaEnvelope className="detail-icon" />
              <div className="detail-content">
                <span className="detail-label">Email</span>
                <span className="detail-value">{user?.email}</span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Change Password Section */}
      <div className="profile-section">
        <div className="profile-section-header">
          <h2 className="section-title">Change Password</h2>
        </div>

        {passwordStep === "initial" ? (
          <div className="password-initial">
            <p className="password-description">
              To change your password, first we need to verify your current
              password for security.
            </p>
            <form
              onSubmit={handleValidateCurrentPassword}
              className="profile-form"
            >
              <div className="form-group">
                <label htmlFor="currentPassword">
                  <FaLock className="label-icon" />
                  Current Password
                </label>
                <input
                  type="password"
                  id="currentPassword"
                  name="currentPassword"
                  value={currentPassword}
                  onChange={handlePasswordChange}
                  required
                  placeholder="Enter current password"
                />
              </div>
              <div className="form-actions">
                <button
                  type="submit"
                  className="save-button"
                  disabled={loading}
                >
                  <FaLock /> {loading ? "Verifying..." : "Verify Password"}
                </button>
              </div>
            </form>
          </div>
        ) : passwordStep === "new" ? (
          <form onSubmit={handleChangePassword} className="profile-form">
            <div className="form-group">
              <label htmlFor="newPassword">
                <FaLock className="label-icon" />
                New Password
              </label>
              <input
                type="password"
                id="newPassword"
                name="newPassword"
                value={passwordData.newPassword}
                onChange={handlePasswordChange}
                required
                placeholder="Enter new password"
                minLength={6}
              />
            </div>

            <div className="form-group">
              <label htmlFor="confirmPassword">
                <FaLock className="label-icon" />
                Confirm New Password
              </label>
              <input
                type="password"
                id="confirmPassword"
                name="confirmPassword"
                value={passwordData.confirmPassword}
                onChange={handlePasswordChange}
                required
                placeholder="Confirm new password"
                minLength={6}
              />
            </div>

            <div className="form-actions">
              <button
                type="button"
                className="cancel-button"
                onClick={handleCancelPasswordChange}
              >
                <FaTimes /> Cancel
              </button>
              <button type="submit" className="save-button" disabled={loading}>
                <FaLock /> {loading ? "Changing..." : "Change Password"}
              </button>
            </div>
          </form>
        ) : null}
      </div>
    </div>
  );
};

export default Profile;
