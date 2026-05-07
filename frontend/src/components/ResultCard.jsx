import React from "react";
import { FaRobot, FaUser, FaFileAlt, FaImage, FaVideo, FaDownload } from "react-icons/fa";
import { API_BASE_URL } from "../utils/api";
import "./ResultCard.css";

const ResultCard = ({ result, confidence, type, timestamp, content, imagePreview, explanation, analysis_details }) => {
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

  const getMediaUrl = () => {
    if (imagePreview) return imagePreview;
    if (content && typeof content === 'string' && content.startsWith('/uploads')) {
      return `${API_BASE_URL}${content}`;
    }
    return null;
  };

  const mediaUrl = getMediaUrl();

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

      {type === "image" && mediaUrl ? (
        <div className="compact-media-box">
          <img src={mediaUrl} alt="Preview" crossOrigin="anonymous" />
        </div>
      ) : type === "video" && mediaUrl ? (
        <div className="compact-media-box">
          <video
            src={mediaUrl}
            controls
            crossOrigin="anonymous"
            style={{ width: '100%', maxHeight: '300px', borderRadius: '8px' }}
            onError={(e) => {
              // Fallback: try without crossOrigin if CORS fails
              e.target.removeAttribute('crossorigin');
              e.target.load();
            }}
          />
        </div>
      ) : (type === "video" || type === "image") ? (
        <div className="compact-placeholder">
          {getTypeIcon()}
          <span>{type?.charAt(0).toUpperCase() + type?.slice(1)} analyzed</span>
        </div>
      ) : null}

      <div className="analysis-box">
        <div className="analysis-title">Analysis Detail</div>
        <div className="analysis-text">
          {explanation || (analysis_details && analysis_details.length > 0 ? (
            <div className="details-list">
              {analysis_details.map((detail, idx) => (
                <div key={idx} className="detail-item" style={{ marginBottom: '0.75rem', padding: '0.5rem', background: 'rgba(255,255,255,0.03)', borderRadius: '8px', borderLeft: `3px solid ${detail.verdict?.includes('AI') || detail.verdict?.includes('High') || detail.verdict?.includes('Vocoder') || detail.verdict?.includes('Suspicious') ? 'var(--error)' : 'var(--success)'}` }}>
                  <div style={{ marginBottom: '0.25rem' }}>
                    <span style={{ fontSize: '0.8rem', fontWeight: 600, color: detail.verdict?.includes('AI') || detail.verdict?.includes('High') || detail.verdict?.includes('Vocoder') || detail.verdict?.includes('Suspicious') ? 'var(--error)' : 'var(--success)' }}>
                      {detail.verdict}
                    </span>
                  </div>
                  <div style={{ fontSize: '0.82rem', lineHeight: 1.5 }}>{detail.explanation || detail.analysis}</div>
                </div>
              ))}
            </div>
          ) : `Detected based on ${type} patterns and ${isAIGenerated ? 'AI signatures' : 'natural characteristics'}.`)}
        </div>
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
