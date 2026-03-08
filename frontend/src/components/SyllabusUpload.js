import React from "react";

export default function SyllabusUpload({
  topics,
  syllabusLoading,
  onUpload,
  onNext,
}) {
  return (
    <section className="card">
      <h2 className="card-title">
        <span className="card-icon">📄</span> Syllabus Upload &amp; Topic Extraction
      </h2>

      <label className="upload-btn blue">
        {syllabusLoading ? "Processing…" : "Upload Syllabus PDF"}
        <input type="file" accept=".pdf" onChange={onUpload} hidden />
      </label>

      {syllabusLoading && <p className="loading-text">Extracting topics from syllabus…</p>}

      {topics && topics.modules && Object.keys(topics.modules).length > 0 && (
        <div className="modules-grid">
          {Object.entries(topics.modules).map(([moduleName, moduleTopics]) => (
            <div key={moduleName} className="module-card">
              <span className="module-badge">{moduleName}</span>
              <ul className="topic-list">
                {Array.isArray(moduleTopics)
                  ? moduleTopics.map((topic, idx) => <li key={idx}>{topic}</li>)
                  : <li>{String(moduleTopics)}</li>
                }
              </ul>
            </div>
          ))}
        </div>
      )}

      {topics && (
        <button className="btn green next-btn" onClick={onNext}>
          Continue to Textbook Upload →
        </button>
      )}
    </section>
  );
}
