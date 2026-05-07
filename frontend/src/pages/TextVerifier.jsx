import React, { useState, useEffect, useRef } from "react";
import ResultCard from "../components/ResultCard";
import { detectAPI } from "../utils/api";

const TextVerifier = () => {
  const [text, setText] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const resultRef = useRef(null);

  useEffect(() => {
    if (result && resultRef.current) {
      resultRef.current.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }, [result]);

  useEffect(() => {
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
      setError(err.response?.status === 401 ? "Please login to verify content." : err.response?.data?.detail || "Failed to verify text");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="verifier-page fade-in">
      <div className="verifier-header">
        <h1 className="page-title">Text Verification</h1>
        <p className="page-subtitle">Paste or type text to check for AI generation signals.</p>
      </div>

      <div className="card verifier-card">
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="text">Content</label>
            <textarea
              id="text"
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="Enter text to verify..."
              rows="8"
              required
              className="form-textarea"
            />
          </div>

          {error && <div className="error-msg">{error}</div>}

          <button
            type="submit"
            className="btn btn-primary"
            disabled={loading || !text.trim()}
          >
            {loading ? "Analyzing..." : "Verify Content"}
          </button>
        </form>
      </div>

      {loading && (
        <div className="verifier-loading-box">
          <div className="loading-spinner"></div>
          <div className="loading-text">Analyzing Text...</div>
          <div className="loading-subtext">Running linguistic forensics — this may take a few seconds</div>
        </div>
      )}

      {result && (
        <div className="result-container" ref={resultRef}>
          <ResultCard
            result={result.result}
            confidence={result.confidence}
            type={result.type}
            timestamp={result.timestamp}
            content={result.content || text}
            explanation={
              result.analysis_details?.map(d => d.analysis).filter(t => t).join('\n\n')
            }
          />
        </div>
      )}
    </div>
  );
};

export default TextVerifier;
