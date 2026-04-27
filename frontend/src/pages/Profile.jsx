import React, { useState } from "react";
import { useAuth } from "../context/AuthContext";
import { authAPI } from "../utils/api";
import { FaUser, FaEnvelope, FaLock, FaEdit } from "react-icons/fa";

const Profile = () => {
  const { user, fetchUser } = useAuth();
  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState({ fullName: user?.full_name || "", email: user?.email || "" });
  const [passwordStep, setPasswordStep] = useState("initial");
  const [currentPassword, setCurrentPassword] = useState("");
  const [passwordData, setPasswordData] = useState({ newPassword: "", confirmPassword: "" });
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSaveProfile = async (e) => {
    e.preventDefault();
    setError(""); setSuccess(""); setLoading(true);
    try {
      await authAPI.updateProfile({ full_name: formData.fullName });
      setSuccess("Profile updated successfully!");
      setIsEditing(false);
      if (fetchUser) await fetchUser();
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to update profile");
    } finally {
      setLoading(false);
    }
  };

  const handleValidatePassword = async (e) => {
    e.preventDefault();
    setError(""); setSuccess("");
    if (!currentPassword) return setError("Enter current password");
    setLoading(true);
    try {
      await authAPI.validatePassword({ current_password: currentPassword });
      setPasswordStep("new");
    } catch (err) {
      setError(err.response?.data?.detail || "Incorrect password");
    } finally {
      setLoading(false);
    }
  };

  const handleChangePassword = async (e) => {
    e.preventDefault();
    setError(""); setSuccess("");
    if (passwordData.newPassword !== passwordData.confirmPassword) return setError("Passwords do not match");
    setLoading(true);
    try {
      await authAPI.changePassword({ current_password: currentPassword, new_password: passwordData.newPassword });
      setSuccess("Password changed!");
      setPasswordStep("initial");
      setCurrentPassword("");
      setPasswordData({ newPassword: "", confirmPassword: "" });
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to change password");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="verifier-page fade-in">
      <div className="verifier-header">
        <h1 className="page-title">Profile Settings</h1>
        <p className="page-subtitle">Manage your account information and security.</p>
      </div>

      {error && <div className="error-msg">{error}</div>}
      {success && <div className="success-msg">{success}</div>}

      <div className="card verifier-card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
          <h2 style={{ fontSize: '1.125rem', fontWeight: 700 }}>Personal Information</h2>
          {!isEditing && <button className="btn btn-secondary" onClick={() => setIsEditing(true)}><FaEdit /> Edit</button>}
        </div>

        {isEditing ? (
          <form onSubmit={handleSaveProfile}>
            <div className="form-group">
              <label><FaUser style={{ marginRight: '0.5rem' }} /> Full Name</label>
              <input type="text" value={formData.fullName} onChange={(e) => setFormData({ ...formData, fullName: e.target.value })} required className="form-input" />
            </div>
            <div className="form-group">
              <label><FaEnvelope style={{ marginRight: '0.5rem' }} /> Email</label>
              <input type="email" value={formData.email} disabled className="form-input" style={{ opacity: 0.6 }} />
            </div>
            <div style={{ display: 'flex', gap: '0.75rem' }}>
              <button type="submit" className="btn btn-primary" disabled={loading}>Save</button>
              <button type="button" className="btn btn-secondary" onClick={() => setIsEditing(false)}>Cancel</button>
            </div>
          </form>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Full Name</div>
              <div style={{ fontWeight: 600 }}>{user?.full_name}</div>
            </div>
            <div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Email Address</div>
              <div style={{ fontWeight: 600 }}>{user?.email}</div>
            </div>
          </div>
        )}
      </div>

      <div className="card verifier-card">
        <h2 style={{ fontSize: '1.125rem', fontWeight: 700, marginBottom: '1.5rem' }}>Security</h2>
        {passwordStep === "initial" ? (
          <form onSubmit={handleValidatePassword}>
            <div className="form-group">
              <label><FaLock style={{ marginRight: '0.5rem' }} /> Current Password</label>
              <input type="password" value={currentPassword} onChange={(e) => setCurrentPassword(e.target.value)} required className="form-input" placeholder="Verify current password" />
            </div>
            <button type="submit" className="btn btn-primary" disabled={loading}>Verify & Continue</button>
          </form>
        ) : (
          <form onSubmit={handleChangePassword}>
            <div className="form-group">
              <label>New Password</label>
              <input type="password" value={passwordData.newPassword} onChange={(e) => setPasswordData({ ...passwordData, newPassword: e.target.value })} required className="form-input" minLength={6} />
            </div>
            <div className="form-group">
              <label>Confirm Password</label>
              <input type="password" value={passwordData.confirmPassword} onChange={(e) => setPasswordData({ ...passwordData, confirmPassword: e.target.value })} required className="form-input" minLength={6} />
            </div>
            <div style={{ display: 'flex', gap: '0.75rem' }}>
              <button type="submit" className="btn btn-primary" disabled={loading}>Update Password</button>
              <button type="button" className="btn btn-secondary" onClick={() => setPasswordStep("initial")}>Cancel</button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
};

export default Profile;
