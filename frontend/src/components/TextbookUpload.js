import React from "react";

export default function TextbookUpload({
  chunkCount,
  textbookLoading,
  onUpload,
  onNext,
}) {
  return (
    <section className="card">
      <h2 className="card-title">
        <span className="card-icon">📚</span> Textbook Upload &amp; Content Chunking
      </h2>

      <label className="upload-btn purple">
        {textbookLoading ? "Processing…" : "Upload Textbook PDF"}
        <input type="file" accept=".pdf" onChange={onUpload} hidden />
      </label>

      {textbookLoading && <p className="loading-text">Chunking textbook content…</p>}

      {chunkCount > 0 && (
        <div className="chunk-result">
          <div className="result-badge">
            <span className="result-number">{chunkCount}</span>
            <span className="result-label">chunks created</span>
          </div>
          <button className="btn green next-btn" onClick={onNext}>
            Continue to Semantic Mapping →
          </button>
        </div>
      )}
    </section>
  );
}
