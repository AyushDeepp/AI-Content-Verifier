import React, { useState } from "react";
import UploadCard from "../components/UploadCard";
import ResultCard from "../components/ResultCard";
import { detectAPI } from "../utils/api";
import "./VideoVerifier.css";

const VideoVerifier = () => {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleFileUpload = (selectedFile) => {
    setFile(selectedFile);
    setResult(null);
    setError("");
  };

  const handleVerify = async () => {
    if (!file) return;

    setError("");
    setLoading(true);
    setResult(null);

    try {
      const response = await detectAPI.video(file);
      setResult(response.data);
    } catch (err) {
      if (err.response?.status === 401) {
        setError(
          "Please login to verify content. Sign up for free to get started!"
        );
      } else {
        setError(err.response?.data?.detail || "Failed to verify video");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="verifier-page">
      <div className="verifier-header">
        <h1 className="page-title">Video Verification</h1>
        <p className="page-subtitle">
          Upload a video to check if it's AI-generated
        </p>
      </div>

      <div className="verifier-content">
        <div className="verifier-card">
          <UploadCard
            onUpload={handleFileUpload}
            type="video"
            accept="video/*"
          />

          {file && (
            <div className="file-info-display">
              <p className="file-name">{file.name}</p>
              <p className="file-size">
                {(file.size / 1024 / 1024).toFixed(2)} MB
              </p>
            </div>
          )}

          {error && <div className="error-message">{error}</div>}

          {file && (
            <button
              onClick={handleVerify}
              className="verify-button primary"
              disabled={loading}
            >
              {loading ? "Verifying..." : "Verify Video"}
            </button>
          )}
        </div>

        {loading && (
          <div className="loading-container">
            <div className="loading-spinner"></div>
            <p>Analyzing video with AI models...</p>
          </div>
        )}

        {result && (
          <div className="result-container">
            <ResultCard
              result={result.result}
              confidence={result.confidence}
              type={result.type}
              timestamp={result.timestamp}
              content={result.content}
            />
          </div>
        )}
      </div>
    </div>
  );
};

export default VideoVerifier;
