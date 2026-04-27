import React, { useState, useEffect, useCallback } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { resultsAPI } from "../utils/api";
import ResultCard from "../components/ResultCard";
import {
  FaFileAlt,
  FaImage,
  FaVideo,
  FaSearch,
  FaChartLine,
  FaLightbulb,
  FaArrowRight,
  FaRobot,
  FaUser,
} from "react-icons/fa";
import "./Dashboard.css";

const Dashboard = () => {
  const { user, isAuthenticated } = useAuth();
  const [stats, setStats] = useState(null);
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [filterType, setFilterType] = useState("all");
  const [expandedResultId, setExpandedResultId] = useState(null);

  const fetchDashboardData = async () => {
    try {
      const statsResponse = await resultsAPI.getStats();
      setStats(statsResponse.data);
    } catch (error) {
      console.error("Failed to fetch dashboard data:", error);
    } finally {
      setLoading(false);
    }
  };

  const fetchActivityData = useCallback(async () => {
    try {
      const response = await resultsAPI.getAll(1000, 0);
      let allResults = response.data;

      if (filterType !== "all") {
        allResults = allResults.filter((result) => result.type === filterType);
      }

      if (searchQuery.trim()) {
        const query = searchQuery.toLowerCase();
        allResults = allResults.filter((result) => {
          return (
            result.type.toLowerCase().includes(query) ||
            (result.result ? "ai" : "human").includes(query)
          );
        });
      }

      setResults(allResults.slice(0, 10)); // Just show latest 10 for simplicity
    } catch (error) {
      console.error("Failed to fetch activity data:", error);
    }
  }, [filterType, searchQuery]);

  useEffect(() => {
    if (isAuthenticated) {
      fetchDashboardData();
    }
  }, [isAuthenticated]);

  useEffect(() => {
    if (isAuthenticated) {
      fetchActivityData();
    }
  }, [isAuthenticated, fetchActivityData]);

  const verificationPanels = [
    { id: "text", label: "Text", icon: FaFileAlt, path: "/text", description: "Detect AI-generated text" },
    { id: "image", label: "Image", icon: FaImage, path: "/image", description: "Identify AI-generated images" },
    { id: "video", label: "Video", icon: FaVideo, path: "/video", description: "Analyze videos for AI content" },
  ];

  if (loading) {
    return (
      <div className="dashboard-page">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Loading your dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard-page fade-in">
      <div className="dashboard-header">
        <h1 className="greeting-title">Hello, {user?.full_name?.split(' ')[0] || "User"}</h1>
        <p className="greeting-subtitle">Monitor and verify your content authenticity.</p>
      </div>

      {stats && (
        <div className="stats-bar">
          <div className="stat-item">
            <span className="stat-value">{stats.total_verifications || 0}</span>
            <span className="stat-label">Total Checks</span>
          </div>
          <div className="stat-item">
            <span className="stat-value" style={{color: 'var(--error)'}}>{stats.ai_detected || 0}</span>
            <span className="stat-label">AI Detected</span>
          </div>
          <div className="stat-item">
            <span className="stat-value" style={{color: 'var(--success)'}}>{stats.human_detected || 0}</span>
            <span className="stat-label">Human</span>
          </div>
        </div>
      )}

      <div className="dashboard-content">
        <div className="dashboard-main">
          <section className="verification-section">
            <div className="verification-panels-grid">
              {verificationPanels.map((panel) => (
                <div key={panel.id} className="verification-panel">
                  <div className="panel-header">
                    <div className="panel-icon"><panel.icon /></div>
                    <h3 className="panel-title">{panel.label}</h3>
                  </div>
                  <p className="panel-description">{panel.description}</p>
                  <Link to={panel.path} className="btn btn-primary panel-button">
                    Start <FaArrowRight />
                  </Link>
                </div>
              ))}
            </div>
          </section>

          <section className="activity-section">
            <div className="activity-header">
              <h2 className="section-title">Recent Activity</h2>
              <div className="activity-controls">
                {["all", "text", "image", "video"].map(type => (
                  <button 
                    key={type}
                    className={`filter-button ${filterType === type ? "active" : ""}`}
                    onClick={() => {setFilterType(type);}}
                  >
                    {type.charAt(0).toUpperCase() + type.slice(1)}
                  </button>
                ))}
              </div>
            </div>

            <div className="activity-search">
              <div className="search-container">
                <FaSearch className="search-icon" />
                <input
                  type="text"
                  placeholder="Search activities..."
                  value={searchQuery}
                  onChange={(e) => {setSearchQuery(e.target.value);}}
                  className="search-input"
                />
              </div>
            </div>

            <div className="activity-list">
              {results.length === 0 ? (
                <div className="empty-state"><p>No activities found.</p></div>
              ) : (
                results.map((result) => (
                  <div key={result.id} className="activity-list-item">
                    <div className="activity-item-header" onClick={() => setExpandedResultId(expandedResultId === result.id ? null : result.id)}>
                      <div className="activity-item-main">
                        <div className="activity-item-icon" style={{ color: result.result ? 'var(--error)' : 'var(--success)' }}>
                          {result.result ? <FaRobot /> : <FaUser />}
                        </div>
                        <div className="activity-item-info">
                          <div className="activity-item-title">{result.result ? "AI Content" : "Human Content"}</div>
                          <div className="activity-item-meta">
                            <span className="activity-item-type">{result.type.toUpperCase()}</span>
                            <span>•</span>
                            <span>{Math.round(result.confidence * 100)}% Confidence</span>
                            <span>•</span>
                            <span>{new Date(result.timestamp).toLocaleDateString()}</span>
                          </div>
                        </div>
                      </div>
                      <div className={`activity-item-arrow ${expandedResultId === result.id ? "expanded" : ""}`}>
                        <FaArrowRight />
                      </div>
                    </div>
                    {expandedResultId === result.id && (
                      <div className="activity-item-detail">
                        <ResultCard {...result} />
                      </div>
                    )}
                  </div>
                ))
              )}
            </div>
          </section>
        </div>

        <aside className="dashboard-sidebar">
          <div className="insights-card">
            <div className="insights-header">
              <FaChartLine className="insights-icon" />
              <h3 className="insights-title">Insights</h3>
            </div>
            {stats && stats.total_verifications > 0 && (
              <>
                <div className="chart-bar-container">
                  <div className="chart-bar ai-bar" style={{ width: `${(stats.ai_detected / stats.total_verifications) * 100}%` }} />
                  <div className="chart-bar human-bar" style={{ width: `${(stats.human_detected / stats.total_verifications) * 100}%` }} />
                </div>
                <div className="insight-item">
                  <span className="insight-label">AI Rate</span>
                  <span className="insight-value">{Math.round((stats.ai_detected / stats.total_verifications) * 100)}%</span>
                </div>
                <div className="insight-item">
                  <span className="insight-label">Text checks</span>
                  <span className="insight-value">{stats.text_count || 0}</span>
                </div>
              </>
            )}
          </div>

          <div className="tips-card">
            <div className="tips-header">
              <FaLightbulb className="tips-icon" />
              <h3 className="tips-title">Quick Tips</h3>
            </div>
            <div className="tip-item">
              <div className="tip-content">
                <div className="tip-title">Better Text Results</div>
                <p className="tip-text">Provide at least 100 words for higher accuracy.</p>
              </div>
            </div>
          </div>
        </aside>
      </div>
    </div>
  );
};

export default Dashboard;
