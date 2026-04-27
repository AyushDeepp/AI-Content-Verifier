import React, { useState } from "react";
import UploadCard from "../components/UploadCard";
import ResultCard from "../components/ResultCard";
import { detectAPI } from "../utils/api";

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
      setError(err.response?.status === 401 ? "Please login to verify content." : err.response?.data?.detail || "Failed to verify video");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="verifier-page fade-in">
      <div className="verifier-header">
        <h1 className="page-title">Video Verification</h1>
        <p className="page-subtitle">Upload a video to check for AI generation signals.</p>
      </div>

      <div className="card verifier-card">
        <UploadCard
          onUpload={handleFileUpload}
          type="video"
          accept="video/*"
        />

        {file && (
          <div className="file-info" style={{ marginTop: '1rem', textAlign: 'center', fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
            <p><strong>{file.name}</strong> ({(file.size / 1024 / 1024).toFixed(2)} MB)</p>
          </div>
        )}

        {error && <div className="error-msg" style={{ marginTop: '1rem' }}>{error}</div>}

        {file && (
          <button
            onClick={handleVerify}
            className="btn btn-primary"
            disabled={loading}
            style={{ marginTop: '1rem' }}
          >
            {loading ? "Verifying..." : "Verify Video"}
          </button>
        )}
      </div>

      {result && (
        <div className="result-container">
          <ResultCard
            result={result.result}
            confidence={result.confidence}
            type={result.type}
            timestamp={result.timestamp}
            content={result.content}
            explanation={
              result.analysis_details?.map(d => d.analysis).filter(t => t).join('\n\n')
            }
          />
        </div>
      )}
    </div>
  );
};

export default VideoVerifier;
