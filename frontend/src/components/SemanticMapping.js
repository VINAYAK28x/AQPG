import React, { useState } from "react";

const API_BASE_URL = process.env.REACT_APP_API_URL || "http://127.0.0.1:8000";

export default function SemanticMapping({ onNext }) {
  const [loading, setLoading] = useState(false);
  const [mapping, setMapping] = useState(null);
  const [error, setError] = useState(null);

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

  const topicCount = mapping ? Object.keys(mapping).length : 0;
  const totalChunks = mapping
    ? Object.values(mapping).reduce((sum, chunks) => sum + chunks.length, 0)
    : 0;

  return (
    <section className="card">
      <h2 className="card-title">
        <span className="card-icon">🔗</span> Semantic Topic–Chunk Mapping
      </h2>
      <p className="card-desc">
        Uses the fine-tuned <strong>SBERT model</strong> to semantically map
        syllabus topics to the most relevant textbook chunks.
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
              <span className="stat-value">{topicCount}</span>
              <span className="stat-label">topics mapped</span>
            </div>
            <div className="stat-pill">
              <span className="stat-value">{totalChunks}</span>
              <span className="stat-label">chunks linked</span>
            </div>
          </div>

          <div className="mapping-results">
            {Object.entries(mapping).slice(0, 8).map(([topic, chunks]) => (
              <div key={topic} className="mapping-item">
                <div className="mapping-topic">{topic}</div>
                <div className="mapping-chunks">
                  {chunks.map((chunk, idx) => (
                    <span key={idx} className="chunk-tag">
                      Chunk #{chunk.chunk_id}{" "}
                      <small>({(chunk.score * 100).toFixed(0)}%)</small>
                    </span>
                  ))}
                </div>
              </div>
            ))}
            {topicCount > 8 && (
              <p className="more-text">… and {topicCount - 8} more topics</p>
            )}
          </div>

          <button className="btn green next-btn" onClick={onNext}>
            Continue to Pattern Configuration →
          </button>
        </>
      )}
    </section>
  );
}
