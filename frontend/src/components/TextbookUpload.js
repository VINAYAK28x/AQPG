import React, { useState } from "react";

export default function TextbookUpload({
  chunkCount,
  textbookLoading,
  onUpload,
  onNext,
  totalPdfPages,
  pagesProcessed,
}) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [allPages, setAllPages] = useState(true);
  const [pageRange, setPageRange] = useState("");

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file) {
      setSelectedFile(file);
    }
  };

  const handleUpload = () => {
    if (!selectedFile) return;
    const range = allPages ? "" : pageRange.trim();
    onUpload(selectedFile, range);
  };

  return (
    <section className="card">
      <h2 className="card-title">
        <span className="card-icon">📚</span> Textbook Upload &amp; Content Chunking
      </h2>

      {/* File Selection */}
      <label className="upload-btn purple">
        {selectedFile ? `📄 ${selectedFile.name}` : "Choose Textbook PDF"}
        <input type="file" accept=".pdf" onChange={handleFileSelect} hidden />
      </label>

      {/* Page Range Selector — appears after file selection */}
      {selectedFile && !textbookLoading && chunkCount === 0 && (
        <div className="page-range-section">
          <div className="page-toggle-row">
            <label className="switch">
              <input
                type="checkbox"
                checked={allPages}
                onChange={(e) => setAllPages(e.target.checked)}
              />
              <span className="switch-slider"></span>
            </label>
            <span className="page-toggle-label">
              {allPages ? "Process all pages" : "Custom page range"}
            </span>
          </div>

          {!allPages && (
            <div className="page-range-input-group">
              <input
                type="text"
                className="page-range-input"
                value={pageRange}
                onChange={(e) => setPageRange(e.target.value)}
                placeholder="e.g., 1-5, 8, 10-20"
              />
              <p className="page-range-hint">
                Comma-separated ranges. Example: <strong>1-5, 8, 10-20</strong>
              </p>
            </div>
          )}

          <button
            className="btn indigo"
            onClick={handleUpload}
            disabled={textbookLoading || (!allPages && !pageRange.trim())}
            style={{ marginTop: "14px" }}
          >
            {textbookLoading ? "Processing…" : "📤 Upload & Process"}
          </button>
        </div>
      )}

      {textbookLoading && <p className="loading-text">Chunking textbook content…</p>}

      {chunkCount > 0 && (
        <div className="chunk-result">
          <div className="result-badges-row">
            <div className="result-badge">
              <span className="result-number">{chunkCount}</span>
              <span className="result-label">chunks created</span>
            </div>
            {totalPdfPages > 0 && (
              <div className="result-badge pages-badge">
                <span className="result-number">{pagesProcessed || totalPdfPages}</span>
                <span className="result-label">of {totalPdfPages} pages processed</span>
              </div>
            )}
          </div>
          <button className="btn green next-btn" onClick={onNext}>
            Continue to Semantic Mapping →
          </button>
        </div>
      )}
    </section>
  );
}
