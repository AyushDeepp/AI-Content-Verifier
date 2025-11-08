import React from "react";
import {
  FaRobot,
  FaUser,
  FaFileAlt,
  FaImage,
  FaVideo,
  FaDownload,
} from "react-icons/fa";
import "./ResultCard.css";

const ResultCard = ({
  result,
  confidence,
  type,
  timestamp,
  content,
  imagePreview,
  explanation,
}) => {
  const isAIGenerated = result;
  const confidencePercent = Math.round(confidence * 100);

  const getResultColor = () => {
    return isAIGenerated ? "#ef4444" : "#10b981";
  };

  const getExplanation = () => {
    if (isAIGenerated) {
      switch (type.toLowerCase()) {
        case "text":
          return "Detected based on linguistic features, style patterns, and structural analysis";
        case "image":
          return "Detected based on visual artifacts, pixel patterns, and generation signatures";
        case "video":
          return "Detected based on frame inconsistencies, temporal patterns, and synthesis artifacts";
        default:
          return "Detected based on AI-generated content patterns";
      }
    } else {
      switch (type.toLowerCase()) {
        case "text":
          return "Detected based on natural language patterns and human writing characteristics";
        case "image":
          return "Detected based on natural image characteristics and photographic patterns";
        case "video":
          return "Detected based on natural video flow and realistic motion patterns";
        default:
          return "Detected based on human-created content patterns";
      }
    }
  };

  const getTypeIcon = () => {
    switch (type.toLowerCase()) {
      case "text":
        return <FaFileAlt />;
      case "image":
        return <FaImage />;
      case "video":
        return <FaVideo />;
      default:
        return <FaFileAlt />;
    }
  };

  return (
    <div
      className="result-card"
      style={{
        "--result-color": getResultColor(),
      }}
    >
      {/* Confidence Display */}
      <div className="result-confidence-section">
        <div className="confidence-ring">
          <svg className="ring-svg" viewBox="0 0 120 120">
            <circle
              className="ring-background"
              cx="60"
              cy="60"
              r="50"
              fill="none"
              stroke="var(--border-color)"
              strokeWidth="8"
            />
            <circle
              className="ring-progress"
              cx="60"
              cy="60"
              r="50"
              fill="none"
              stroke="var(--result-color)"
              strokeWidth="8"
              strokeLinecap="round"
              strokeDasharray={`${2 * Math.PI * 50}`}
              strokeDashoffset={`${2 * Math.PI * 50 * (1 - confidence)}`}
              transform="rotate(-90 60 60)"
            />
          </svg>
          <div className="confidence-text">
            <span className="confidence-percent">{confidencePercent}%</span>
            <span className="confidence-label">Confidence</span>
          </div>
        </div>
        <div className="result-status">
          <div
            className={`status-badge ${
              isAIGenerated ? "ai-badge" : "human-badge"
            }`}
          >
            {isAIGenerated ? <FaRobot /> : <FaUser />}
            <span>{isAIGenerated ? "AI Generated" : "Human Generated"}</span>
          </div>
        </div>
      </div>

      {/* Content Display */}
      <div className="result-content-section">
        <div className="content-header">
          <div className="content-type-icon">{getTypeIcon()}</div>
          <span className="content-type-label">
            {type.toUpperCase()} Content
          </span>
        </div>

        {type.toLowerCase() === "text" && content ? (
          <div className="content-text-display">
            <div className="content-text">{content}</div>
            {content.length >= 1000 && (
              <div className="content-truncated">
                (Content truncated to first 1000 characters)
              </div>
            )}
          </div>
        ) : type.toLowerCase() === "image" ? (
          <div className="content-media-display">
            {imagePreview ? (
              <div className="media-image-preview">
                <img src={imagePreview} alt="Verification result" />
              </div>
            ) : (
              <div className="media-placeholder">
                <FaImage className="media-placeholder-icon" />
                <p className="media-placeholder-text">
                  Image file was analyzed but not stored for privacy reasons.
                </p>
              </div>
            )}
          </div>
        ) : type.toLowerCase() === "video" ? (
          <div className="content-media-display">
            <div className="media-placeholder">
              <FaVideo className="media-placeholder-icon" />
              <p className="media-placeholder-text">
                Video file was analyzed but not stored for privacy reasons.
              </p>
            </div>
          </div>
        ) : (
          <div className="content-text-display">
            <div className="content-text">No content available</div>
          </div>
        )}
      </div>

      {/* Explanation */}
      <div className="result-explanation-section">
        <div className="explanation-label">Analysis Details</div>
        <div className="result-explanation">
          {explanation || getExplanation()}
        </div>
      </div>

      {/* Export Button */}
      <div className="result-export-section">
        <button
          className="export-button"
          onClick={() => {
            const exportData = {
              type: type,
              result: isAIGenerated ? "AI Generated" : "Human Generated",
              confidence: `${confidencePercent}%`,
              explanation: explanation || getExplanation(),
              timestamp: timestamp
                ? new Date(timestamp).toLocaleString()
                : new Date().toLocaleString(),
              content:
                type.toLowerCase() === "text"
                  ? content
                  : type.toLowerCase() === "image"
                  ? "Image file"
                  : "Video file",
            };

            const blob = new Blob([JSON.stringify(exportData, null, 2)], {
              type: "application/json",
            });
            const url = URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            a.download = `verification-result-${new Date().getTime()}.json`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
          }}
        >
          <FaDownload /> Export Result
        </button>
      </div>

      {/* Footer */}
      {timestamp && (
        <div className="result-footer">
          <span className="result-timestamp">
            Verified on {new Date(timestamp).toLocaleString()}
          </span>
        </div>
      )}
    </div>
  );
};

export default ResultCard;
