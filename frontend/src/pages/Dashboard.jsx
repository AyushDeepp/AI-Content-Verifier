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
  FaInfoCircle,
  FaArrowRight,
  FaCalendarAlt,
  FaFilter,
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
  const [pageLimit, setPageLimit] = useState(10);
  const [currentPage, setCurrentPage] = useState(0);
  const [totalResults, setTotalResults] = useState(0);
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
      // Fetch all results to filter client-side (since API doesn't support server-side filtering)
      const response = await resultsAPI.getAll(1000, 0);
      let allResults = response.data;

      // Apply type filter
      if (filterType !== "all") {
        allResults = allResults.filter((result) => result.type === filterType);
      }

      // Apply search filter
      if (searchQuery.trim()) {
        const query = searchQuery.toLowerCase();
        allResults = allResults.filter((result) => {
          return (
            result.type.toLowerCase().includes(query) ||
            (result.result ? "ai" : "human").includes(query)
          );
        });
      }

      setTotalResults(allResults.length);

      // Apply pagination
      const startIndex = currentPage * pageLimit;
      const endIndex = startIndex + pageLimit;
      setResults(allResults.slice(startIndex, endIndex));
    } catch (error) {
      console.error("Failed to fetch activity data:", error);
    }
  }, [filterType, searchQuery, currentPage, pageLimit]);

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
    {
      id: "text",
      label: "Text",
      icon: FaFileAlt,
      path: "/text",
      description: "Detect AI-generated text content",
      lastUsed: stats?.text_count
        ? `Used ${stats.text_count} time${stats.text_count !== 1 ? "s" : ""}`
        : "Never used",
    },
    {
      id: "image",
      label: "Image",
      icon: FaImage,
      path: "/image",
      description: "Identify AI-generated images",
      lastUsed: stats?.image_count
        ? `Used ${stats.image_count} time${stats.image_count !== 1 ? "s" : ""}`
        : "Never used",
    },
    {
      id: "video",
      label: "Video",
      icon: FaVideo,
      path: "/video",
      description: "Analyze videos for AI content",
      lastUsed: stats?.video_count
        ? `Used ${stats.video_count} time${stats.video_count !== 1 ? "s" : ""}`
        : "Never used",
    },
  ];

  const quickTips = [
    {
      title: "Text Analysis Tips",
      content:
        "For best results, provide text samples of at least 100 characters.",
    },
    {
      title: "Image Verification",
      content:
        "Upload clear images in common formats (JPG, PNG) for accurate detection.",
    },
    {
      title: "Understanding Confidence",
      content:
        "Confidence scores above 70% indicate strong AI detection signals.",
    },
  ];

  // Results are already filtered in fetchActivityData
  const filteredResults = results;

  const handleFilterChange = (type) => {
    setFilterType(type);
    setCurrentPage(0); // Reset to first page when filter changes
  };

  const handlePageLimitChange = (limit) => {
    setPageLimit(parseInt(limit));
    setCurrentPage(0);
  };

  const totalPages = Math.ceil(totalResults / pageLimit);

  if (loading) {
    return (
      <div className="dashboard-page">
        <div className="loading-container">
          <div className="loading-spinner"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard-page">
      {/* Personalized Greeting Header */}
      <div className="dashboard-header">
        <div className="greeting-section">
          <h1 className="greeting-title">
            Welcome back, {user?.full_name || "User"} 👋
          </h1>
          <p className="greeting-subtitle">
            Ready to verify your content? Choose a verification type below.
        </p>
      </div>
      </div>

      {/* Quick Stats Summary Bar */}
      {stats && (
        <div className="stats-bar">
          <div className="stat-item">
            <div className="stat-value">{stats.total_verifications || 0}</div>
            <div className="stat-label">Total Verifications</div>
          </div>
          <div className="stat-divider"></div>
          <div className="stat-item">
            <div className="stat-value ai-detected">
              {stats.ai_detected || 0}
            </div>
            <div className="stat-label">AI Detected</div>
          </div>
          <div className="stat-divider"></div>
          <div className="stat-item">
            <div className="stat-value human-detected">
              {stats.human_detected || 0}
            </div>
            <div className="stat-label">Human Detected</div>
          </div>
        </div>
      )}

      {/* Main Dashboard Content */}
      <div className="dashboard-content">
        <div className="dashboard-main">
          {/* Verification Panels */}
          <div className="verification-panels-section">
            <h2 className="section-title">Start Verification</h2>
            <div className="verification-panels-grid">
              {verificationPanels.map((panel) => {
                const IconComponent = panel.icon;
          return (
                  <div key={panel.id} className="verification-panel">
                    <div className="panel-header">
                      <div className="panel-icon">
                        <IconComponent />
                      </div>
                      <div className="panel-info">
                        <h3 className="panel-title">
                          {panel.label} Verification
                        </h3>
                        <p className="panel-description">{panel.description}</p>
                      </div>
                    </div>
                    <div className="panel-footer">
                      <div className="panel-meta">
                        <FaCalendarAlt className="meta-icon" />
                        <span className="meta-text">{panel.lastUsed}</span>
                      </div>
                      <Link to={panel.path} className="panel-button">
                        Start Verification <FaArrowRight />
                      </Link>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Activity Section */}
          <div className="activity-section">
            <div className="activity-header">
              <h2 className="section-title">Activity</h2>
              <div className="activity-controls">
                <div className="filter-controls">
                  <FaFilter className="filter-icon" />
                  <button
                    className={`filter-button ${
                      filterType === "all" ? "active" : ""
                    }`}
                    onClick={() => handleFilterChange("all")}
                  >
                    All
                  </button>
                  <button
                    className={`filter-button ${
                      filterType === "text" ? "active" : ""
                    }`}
                    onClick={() => handleFilterChange("text")}
                  >
                    Text
                  </button>
                  <button
                    className={`filter-button ${
                      filterType === "image" ? "active" : ""
                    }`}
                    onClick={() => handleFilterChange("image")}
                  >
                    Image
                  </button>
                  <button
                    className={`filter-button ${
                      filterType === "video" ? "active" : ""
                    }`}
                    onClick={() => handleFilterChange("video")}
                  >
                    Video
                  </button>
                </div>
                <div className="pagination-controls">
                  <label htmlFor="pageLimit">Show:</label>
                  <select
                    id="pageLimit"
                    value={pageLimit}
                    onChange={(e) => handlePageLimitChange(e.target.value)}
                    className="page-limit-select"
                  >
                    <option value={10}>10</option>
                    <option value={20}>20</option>
                    <option value={50}>50</option>
                    <option value={100}>100</option>
                  </select>
                </div>
              </div>
            </div>

            {/* Search Bar */}
            <div className="activity-search">
              <div className="search-container">
                <FaSearch className="search-icon" />
                <input
                  type="text"
                  placeholder="Search activities..."
                  value={searchQuery}
                  onChange={(e) => {
                    setSearchQuery(e.target.value);
                    setCurrentPage(0);
                  }}
                  className="search-input"
                />
              </div>
            </div>

            {filteredResults.length === 0 ? (
              <div className="empty-state">
                <p className="empty-message">
                  {searchQuery || filterType !== "all"
                    ? "No activities match your filters"
                    : "No verifications yet. Start by verifying your first content!"}
                </p>
              </div>
            ) : (
              <>
                <div className="activity-list">
                  {filteredResults.map((result) => {
                    const isExpanded = expandedResultId === result.id;
                    const isAIGenerated = result.result;
                    const confidencePercent = Math.round(
                      result.confidence * 100
                    );
                    const getResultText = () =>
                      isAIGenerated ? "AI Generated" : "Human Generated";
                    const getResultColor = () =>
                      isAIGenerated ? "#ef4444" : "#10b981";

                    return (
                      <div key={result.id} className="activity-list-item">
                        <div
                          className="activity-item-header"
                          onClick={() =>
                            setExpandedResultId(isExpanded ? null : result.id)
                          }
                        >
                          <div className="activity-item-main">
                            <div
                              className="activity-item-icon"
                              style={{ color: getResultColor() }}
                            >
                              {isAIGenerated ? <FaRobot /> : <FaUser />}
                            </div>
                            <div className="activity-item-info">
                              <div className="activity-item-title">
                                {getResultText()}
                              </div>
                              <div className="activity-item-meta">
                                <span className="activity-item-type">
                                  {result.type.toUpperCase()}
                                </span>
                                <span className="activity-item-separator">
                                  •
                                </span>
                                <span className="activity-item-confidence">
                                  {confidencePercent}% Confidence
                                </span>
                                <span className="activity-item-separator">
                                  •
                                </span>
                                <span className="activity-item-time">
                                  {new Date(result.timestamp).toLocaleString()}
                                </span>
                              </div>
                            </div>
                          </div>
                          <div
                            className={`activity-item-arrow ${
                              isExpanded ? "expanded" : ""
                            }`}
                          >
                            <FaArrowRight />
                          </div>
                        </div>
                        {isExpanded && (
                          <div className="activity-item-detail">
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
          );
        })}
                </div>
                {totalPages > 1 && (
                  <div className="pagination">
                    <button
                      className="pagination-button"
                      onClick={() =>
                        setCurrentPage(Math.max(0, currentPage - 1))
                      }
                      disabled={currentPage === 0}
                    >
                      Previous
                    </button>
                    <span className="pagination-info">
                      Page {currentPage + 1} of {totalPages}
                    </span>
                    <button
                      className="pagination-button"
                      onClick={() =>
                        setCurrentPage(
                          Math.min(totalPages - 1, currentPage + 1)
                        )
                      }
                      disabled={currentPage >= totalPages - 1}
                    >
                      Next
                    </button>
                  </div>
                )}
              </>
            )}
          </div>
        </div>

        {/* Sidebar */}
        <div className="dashboard-sidebar">
          {/* Quick Tips */}
          <div className="tips-card">
            <div className="tips-header">
              <FaLightbulb className="tips-icon" />
              <h3 className="tips-title">Quick Tips</h3>
            </div>
            <div className="tips-list">
              {quickTips.map((tip, index) => (
                <div key={index} className="tip-item">
                  <FaInfoCircle className="tip-icon" />
                  <div className="tip-content">
                    <div className="tip-title">{tip.title}</div>
                    <div className="tip-text">{tip.content}</div>
                  </div>
                </div>
              ))}
            </div>
      </div>

          {/* Insights Mini-Cards */}
          {stats && (
            <div className="insights-card">
              <div className="insights-header">
                <FaChartLine className="insights-icon" />
                <h3 className="insights-title">Insights</h3>
              </div>
              {stats.total_verifications > 0 ? (
                <>
                  <div className="insights-chart">
                    <div className="chart-container">
                      <div className="chart-bar-container">
                        <div
                          className="chart-bar ai-bar"
                          style={{
                            width: `${
                              (stats.ai_detected / stats.total_verifications) *
                              100
                            }%`,
                          }}
                        >
                          <span className="chart-label">
                            AI: {stats.ai_detected}
                          </span>
                        </div>
                        <div
                          className="chart-bar human-bar"
                          style={{
                            width: `${
                              (stats.human_detected /
                                stats.total_verifications) *
                              100
                            }%`,
                          }}
                        >
                          <span className="chart-label">
                            Human: {stats.human_detected}
                          </span>
                        </div>
                      </div>
                      <div className="chart-legend">
                        <div className="legend-item">
                          <span className="legend-color ai-color"></span>
                          <span className="legend-text">
                            AI Generated (
                            {Math.round(
                              (stats.ai_detected / stats.total_verifications) *
                                100
                            ) || 0}
                            %)
                          </span>
                        </div>
                        <div className="legend-item">
                          <span className="legend-color human-color"></span>
                          <span className="legend-text">
                            Human Generated (
                            {Math.round(
                              (stats.human_detected /
                                stats.total_verifications) *
                                100
                            ) || 0}
                            %)
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                  <div className="insights-list">
                    <div className="insight-item">
                      <div className="insight-label">Text Verifications</div>
                      <div className="insight-value">
                        {stats.text_count || 0}
                      </div>
                    </div>
                    <div className="insight-item">
                      <div className="insight-label">Image Verifications</div>
                      <div className="insight-value">
                        {stats.image_count || 0}
                      </div>
                    </div>
                    <div className="insight-item">
                      <div className="insight-label">Video Verifications</div>
                      <div className="insight-value">
                        {stats.video_count || 0}
                      </div>
                    </div>
                    <div className="insight-item highlight">
                      <div className="insight-label">AI Detection Rate</div>
                      <div className="insight-value">
                        {Math.round(
                          (stats.ai_detected / stats.total_verifications) * 100
                        ) || 0}
                        %
                      </div>
                    </div>
                  </div>
                </>
              ) : (
                <div className="insights-empty">
                  <p className="empty-message">
                    No verification data yet. Start verifying content to see
                    insights!
                  </p>
        </div>
              )}
        </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
