import React, { useState, useRef, useEffect } from "react";
import UploadCard from "../components/UploadCard";
import ResultCard from "../components/ResultCard";
import { detectAPI } from "../utils/api";

const VideoVerifier = () => {
  const [file, setFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [processingStatus, setProcessingStatus] = useState("");
  const [error, setError] = useState("");
  const prevUrlRef = useRef(null);
  const resultRef = useRef(null);

  useEffect(() => {
    if (result && resultRef.current) {
      resultRef.current.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }, [result]);

  const handleFileUpload = (uploadedFile) => {
    // Revoke old object URL to prevent memory leaks
    if (prevUrlRef.current) {
      URL.revokeObjectURL(prevUrlRef.current);
    }
    const url = URL.createObjectURL(uploadedFile);
    prevUrlRef.current = url;
    setFile(uploadedFile);
    setPreviewUrl(url);
    setError("");
    setResult(null);
  };

  const handleVerify = async () => {
    if (!file) return;
    setError("");
    setLoading(true);
    setResult(null);

    try {
      setProcessingStatus("Uploading and analyzing video...");
      const response = await detectAPI.video(file);
      setResult(response.data);
    } catch (err) {
      console.error("Verification error:", err);
      setError(
        err.response?.status === 401
          ? "Please login to verify content."
          : err.response?.data?.detail || "Failed to process video"
      );
    } finally {
      setLoading(false);
      setProcessingStatus("");
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
          placeholder="Upload or drag & drop video files"
          accept="video/*"
        />

        {/* Local Video Preview — Uses blob URL, no server needed */}
        {previewUrl && (
          <div style={{ marginTop: "1.5rem", borderRadius: "12px", overflow: "hidden", background: "#000" }}>
            <video
              key={previewUrl}
              src={previewUrl}
              controls
              style={{ width: "100%", maxHeight: "360px", display: "block" }}
            >
              Your browser does not support the video tag.
            </video>
            <p style={{ margin: "0.5rem 0 0 0", fontSize: "0.8rem", color: "var(--text-secondary)", textAlign: "center", padding: "0.5rem" }}>
              {file?.name} — {(file?.size / 1024 / 1024).toFixed(2)} MB
            </p>
          </div>
        )}

        {processingStatus && (
          <div className="processing-status" style={{ marginTop: "1rem", textAlign: "center", color: "var(--primary)" }}>
            <div className="loading-spinner-small" style={{ display: "inline-block", marginRight: "8px" }}></div>
            {processingStatus}
          </div>
        )}

        {error && <div className="error-msg" style={{ marginTop: "1rem" }}>{error}</div>}

        {file && (
          <button
            onClick={handleVerify}
            className="btn btn-primary"
            disabled={loading}
            style={{ marginTop: "1rem", width: "100%" }}
          >
            {loading ? "Analyzing..." : "Verify Video"}
          </button>
        )}
      </div>

      {loading && (
        <div className="verifier-loading-box">
          <div className="loading-spinner"></div>
          <div className="loading-text">Analyzing Video...</div>
          <div className="loading-subtext">Running multi-modal forensics — this may take 10–20 seconds</div>
        </div>
      )}

      {result && (
        <div className="result-container" ref={resultRef}>
          <ResultCard
            result={result.result}
            confidence={result.confidence}
            type={result.type}
            timestamp={result.timestamp}
            content={result.content}
            explanation={
              result.analysis_details?.map((d) => d.analysis).filter((t) => t).join("\n\n")
            }
          />
        </div>
      )}
    </div>
  );
};

export default VideoVerifier;
