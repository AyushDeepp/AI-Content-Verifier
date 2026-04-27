import React, { useState } from "react";
import UploadCard from "../components/UploadCard";
import ResultCard from "../components/ResultCard";
import { detectAPI } from "../utils/api";

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
      setError(err.response?.status === 401 ? "Please login to verify content." : err.response?.data?.detail || "Failed to verify image");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="verifier-page fade-in">
      <div className="verifier-header">
        <h1 className="page-title">Image Verification</h1>
        <p className="page-subtitle">Upload an image to check for AI generation signals.</p>
      </div>

      <div className="card verifier-card">
        <UploadCard
          onUpload={handleFileUpload}
          type="image"
          accept="image/*"
        />

        {preview && (
          <div className="image-preview" style={{ marginTop: '1rem', textAlign: 'center' }}>
            <img src={preview} alt="Preview" style={{ maxWidth: '100%', borderRadius: '8px', maxHeight: '300px' }} />
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
            {loading ? "Verifying..." : "Verify Image"}
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
            imagePreview={preview}
            explanation={
              result.analysis_details?.map(d => d.analysis).filter(t => t).join('\n\n')
            }
          />
        </div>
      )}
    </div>
  );
};

export default ImageVerifier;
