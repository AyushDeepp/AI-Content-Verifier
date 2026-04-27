import React from "react";
import { FaRobot, FaUser, FaFileAlt, FaImage, FaVideo, FaDownload } from "react-icons/fa";
import "./ResultCard.css";

const ResultCard = ({ result, confidence, type, timestamp, content, imagePreview, explanation }) => {
  const isAIGenerated = result;
  const confidencePercent = Math.round(confidence * 100);
  const color = isAIGenerated ? "var(--error)" : "var(--success)";

  const getTypeIcon = () => {
    switch (type?.toLowerCase()) {
      case "text": return <FaFileAlt />;
      case "image": return <FaImage />;
      case "video": return <FaVideo />;
      default: return <FaFileAlt />;
    }
  };

  return (
    <div className="result-card-v2" style={{ "--status-color": color }}>
      <div className="result-header-compact">
        <div className="status-indicator">
          <div className="status-icon-box">
            {isAIGenerated ? <FaRobot /> : <FaUser />}
          </div>
          <div className="status-text">
            <div className="status-label">{isAIGenerated ? "AI Generated" : "Human Generated"}</div>
            <div className="status-meta">{type?.toUpperCase()} Content</div>
          </div>
        </div>
        <div className="confidence-pill">
          <div className="confidence-value">{confidencePercent}%</div>
          <div className="confidence-label">Confidence</div>
        </div>
      </div>

      {content && type === "text" && (
        <div className="compact-content-box">
          <div className="content-scroll">{content}</div>
        </div>
      )}

      {imagePreview && type === "image" && (
        <div className="compact-media-box">
          <img src={imagePreview} alt="Preview" />
        </div>
      )}

      {(type === "video" || (type === "image" && !imagePreview)) && (
        <div className="compact-placeholder">
          {getTypeIcon()}
          <span>{type?.charAt(0).toUpperCase() + type?.slice(1)} analyzed</span>
        </div>
      )}

      <div className="analysis-box">
        <div className="analysis-title">Analysis Detail</div>
        <div className="analysis-text">{explanation || `Detected based on ${type} patterns and ${isAIGenerated ? 'AI signatures' : 'natural characteristics'}.`}</div>
      </div>

      <div className="result-actions-compact">
        <button className="btn-icon" title="Download Result">
          <FaDownload />
        </button>
        <span className="timestamp-compact">
          {timestamp ? new Date(timestamp).toLocaleDateString() : 'Just now'}
        </span>
      </div>
    </div>
  );
};

export default ResultCard;
