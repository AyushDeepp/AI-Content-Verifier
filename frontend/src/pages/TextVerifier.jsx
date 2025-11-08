import React, { useState, useEffect } from "react";
import ResultCard from "../components/ResultCard";
import { detectAPI } from "../utils/api";
import "./TextVerifier.css";

const TextVerifier = () => {
  const [text, setText] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    // Check for quick text from home page
    const quickText = sessionStorage.getItem("quickText");
    if (quickText) {
      setText(quickText);
      sessionStorage.removeItem("quickText");
    }
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    setResult(null);

    try {
      const response = await detectAPI.text(text);
      setResult(response.data);
    } catch (err) {
      if (err.response?.status === 401) {
        setError(
          "Please login to verify content. Sign up for free to get started!"
        );
      } else {
        setError(err.response?.data?.detail || "Failed to verify text");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="verifier-page">
      <div className="verifier-header">
        <h1 className="page-title">Text Verification</h1>
        <p className="page-subtitle">
          Paste or type text to check if it's AI-generated
        </p>
      </div>

      <div className="verifier-content">
        <div className="verifier-card">
          <form onSubmit={handleSubmit} className="text-form">
            <div className="form-group">
              <label htmlFor="text">Text Content</label>
              <textarea
                id="text"
                value={text}
                onChange={(e) => setText(e.target.value)}
                placeholder="Enter or paste the text you want to verify..."
                rows="10"
                required
                className="text-input"
              />
              <div className="text-count">{text.length} characters</div>
            </div>

            {error && <div className="error-message">{error}</div>}

            <button
              type="submit"
              className="verify-button primary"
              disabled={loading || !text.trim()}
            >
              {loading ? "Verifying..." : "Verify Text"}
            </button>
          </form>
        </div>

        {loading && (
          <div className="loading-container">
            <div className="loading-spinner"></div>
            <p>Analyzing text with AI models...</p>
          </div>
        )}

        {result && (
          <div className="result-container">
            <ResultCard
              result={result.result}
              confidence={result.confidence}
              type={result.type}
              timestamp={result.timestamp}
              content={result.content || text}
            />
          </div>
        )}
      </div>
    </div>
  );
};

export default TextVerifier;
