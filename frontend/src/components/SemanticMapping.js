import React, { useState } from "react";

const API_BASE_URL = process.env.REACT_APP_API_URL || "http://127.0.0.1:8000";

export default function SemanticMapping({ onNext }) {
  const [loading, setLoading] = useState(false);
  const [mapping, setMapping] = useState(null);
  const [error, setError] = useState(null);
  const [expandedModules, setExpandedModules] = useState([]);

  const toggleModule = (modName) => {
    setExpandedModules((prev) =>
      prev.includes(modName)
        ? prev.filter((m) => m !== modName)
        : [...prev, modName]
    );
  };

  const runMapping = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/semantic-mapping`, {
        method: "POST",
      });
      const data = await response.json();

      if (data.error) {
        setError(data.error);
      } else {
        setMapping(data.mapping || {});
      }
    } catch (err) {
      setError("Failed to connect to backend: " + err.message);
    }

    setLoading(false);
  };

  // Module-based mapping: each key is a module name,
  // value has { topics, raw_text, embedding_ready_text, chunks }
  const moduleCount = mapping ? Object.keys(mapping).length : 0;
  const totalChunks = mapping
    ? Object.values(mapping).reduce((sum, mod) => {
        const chunks = mod.chunks || mod;
        return sum + (Array.isArray(chunks) ? chunks.length : 0);
      }, 0)
    : 0;
  const totalTopics = mapping
    ? Object.values(mapping).reduce((sum, mod) => {
        const topics = mod.topics || [];
        return sum + topics.length;
      }, 0)
    : 0;

  return (
    <section className="card">
      <h2 className="card-title">
        <span className="card-icon">🔗</span> Semantic Module–Chunk Mapping
      </h2>
      <p className="card-desc">
        Uses the fine-tuned <strong>SBERT model</strong> to semantically map
        syllabus modules to the most relevant textbook chunks.
      </p>

      <button
        className="btn indigo"
        onClick={runMapping}
        disabled={loading}
      >
        {loading ? "Running SBERT Mapping…" : "Run Semantic Mapping"}
      </button>

      {error && <div className="error-box">{error}</div>}

      {mapping && (
        <>
          <div className="mapping-stats">
            <div className="stat-pill">
              <span className="stat-value">{moduleCount}</span>
              <span className="stat-label">modules mapped</span>
            </div>
            <div className="stat-pill">
              <span className="stat-value">{totalTopics}</span>
              <span className="stat-label">topics covered</span>
            </div>
            <div className="stat-pill">
              <span className="stat-value">{totalChunks}</span>
              <span className="stat-label">chunks linked</span>
            </div>
          </div>

          <div className="mapping-results">
            {Object.entries(mapping).map(([moduleName, moduleData]) => {
              const chunks = moduleData.chunks || [];
              const topics = moduleData.topics || [];
              const isExpanded = expandedModules.includes(moduleName);
              const visibleTopics = isExpanded ? topics : topics.slice(0, 5);

              return (
                <div key={moduleName} className="mapping-item">
                  <div className="mapping-topic">{moduleName}</div>
                  {topics.length > 0 && (
                    <div className="mapping-topic-list">
                      {visibleTopics.map((t, i) => (
                        <span key={i} className="topic-tag">{t}</span>
                      ))}
                      {topics.length > 5 && (
                        <button
                          className="topic-tag dim"
                          onClick={() => toggleModule(moduleName)}
                          style={{ cursor: "pointer", background: "none", border: "none" }}
                        >
                          {isExpanded ? "↑ Show less" : `+${topics.length - 5} more (Click to Expand)`}
                        </button>
                      )}
                    </div>
                  )}
                  <div className="mapping-chunks">
                    {chunks.map((chunk, idx) => (
                      <span key={idx} className="chunk-tag">
                        Chunk #{chunk.chunk_id}{" "}
                        <small>({(chunk.score * 100).toFixed(0)}%)</small>
                      </span>
                    ))}
                  </div>
                </div>
              );
            })}
          </div>

          <button className="btn green next-btn" onClick={onNext}>
            Continue to Pattern Configuration →
          </button>
        </>
      )}
    </section>
  );
}
