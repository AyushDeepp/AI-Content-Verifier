import React, { useState } from "react";
import UploadCard from "../components/UploadCard";
import ResultCard from "../components/ResultCard";
import { detectAPI } from "../utils/api";
import "./ImageVerifier.css";

const ImageVerifier = () => {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleFileUpload = (selectedFile) => {
    setFile(selectedFile);
    setResult(null);
    setError("");

    // Create preview
    const reader = new FileReader();
    reader.onloadend = () => {
      setPreview(reader.result);
    };
    reader.readAsDataURL(selectedFile);
  };

  const handleVerify = async () => {
    if (!file) return;

    setError("");
    setLoading(true);
    setResult(null);

    try {
      const response = await detectAPI.image(file);
      setResult(response.data);
    } catch (err) {
      if (err.response?.status === 401) {
        setError(
          "Please login to verify content. Sign up for free to get started!"
        );
      } else {
      setError(err.response?.data?.detail || "Failed to verify image");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="verifier-page">
      <div className="verifier-header">
        <h1 className="page-title">Image Verification</h1>
        <p className="page-subtitle">
          Upload an image to check if it's AI-generated
        </p>
      </div>

      <div className="verifier-content">
        <div className="verifier-card">
          <UploadCard
            onUpload={handleFileUpload}
            type="image"
            accept="image/*"
          />

          {preview && (
            <div className="image-preview">
              <img src={preview} alt="Preview" />
            </div>
          )}

          {error && <div className="error-message">{error}</div>}

          {file && (
            <button
              onClick={handleVerify}
              className="verify-button primary"
              disabled={loading}
            >
              {loading ? "Verifying..." : "Verify Image"}
            </button>
          )}
        </div>

        {loading && (
          <div className="loading-container">
            <div className="loading-spinner"></div>
            <p>Analyzing image with AI models...</p>
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
              imagePreview={preview}
            />
          </div>
        )}
      </div>
    </div>
  );
};

export default ImageVerifier;
