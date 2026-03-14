export default function GeneratedQuestions({ questions }) {
  if (!questions || Object.keys(questions).length === 0) return null;

  const handleDownloadPDF = () => {
    // Triggers standard CSS @media print layout
    window.print();
  };

  return (
    <section className="card generated-card">
      <h2 className="card-title no-print">
        <span className="card-icon">📝</span> Generated Questions
      </h2>

      {/* 
        This wrapper holds the precise layout meant for paper printing.
        We show it normally on screen too, but it transforms fully via @media print.
      */}
      <div className="print-wrapper">
        <div className="print-header">
          <h1>Generated Question Paper</h1>
          <hr className="print-divider" />
        </div>

        <div className="print-content">
          {Object.entries(questions).map(([partName, partQuestions]) => (
            <div key={partName} className="gen-part">
              <h3 className="gen-part-name">{partName}</h3>
              <p className="gen-part-instruction">(Answer ALL questions)</p>

              {Array.isArray(partQuestions) ? (
                <div className="gen-questions-list">
                  {partQuestions.map((q, idx) => {
                    const bloomsLevel = q.classified_bloom_level || q.bloom_level;
                    return (
                      <div key={idx} className="gen-question-group">
                        <div className="gen-question-row">
                          <div className="gen-q-num">{q.question_no || idx + 1}.</div>
                          <div className="gen-q-body">
                            <p className="gen-q-text">
                              {q.text || q.question || "—"} 
                              {bloomsLevel && <span className="gen-q-blooms-inline"> [Bloom's Level: {bloomsLevel}]</span>}
                            </p>
                            {/* On-screen footer for tags and marks */}
                            <div className="gen-q-footer no-print">
                              <div className="gen-q-tags">
                                {q.bloom_level && <span className="tag bloom">{q.bloom_level}</span>}
                                {q.classified_bloom_level && q.classified_bloom_level !== q.bloom_level && (
                                  <span className="tag classified">Classified: {q.classified_bloom_level}</span>
                                )}
                                {q.module && <span className="tag module">{q.module}</span>}
                              </div>
                              <div className="gen-q-marks-pill">{q.marks || 0} marks</div>
                            </div>
                          </div>
                          <div className="gen-q-marks print-only">({q.marks || 0})</div>
                        </div>

                        {/* Render Internal Choice (OR) if present */}
                        {q.has_internal_choice && q.or_question && (
                          <div className="gen-question-or-block">
                            <div className="gen-or-divider">— OR —</div>
                            <div className="gen-question-row">
                              <div className="gen-q-num"></div>
                              <div className="gen-q-body">
                                <p className="gen-q-text">
                                  {q.or_question.text || "—"}
                                  {q.or_question.classified_bloom_level && (
                                    <span className="gen-q-blooms-inline"> [Bloom's Level: {q.or_question.classified_bloom_level}]</span>
                                  )}
                                </p>
                                <div className="gen-q-footer no-print">
                                  <div className="gen-q-tags">
                                    {q.or_question.module && <span className="tag module">{q.or_question.module}</span>}
                                  </div>
                                  <div className="gen-q-marks-pill">{q.or_question.marks || q.marks || 0} marks</div>
                                </div>
                              </div>
                              <div className="gen-q-marks print-only">({q.or_question.marks || q.marks || 0})</div>
                            </div>
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              ) : (
                <p>{String(partQuestions)}</p>
              )}
            </div>
          ))}
        </div>
      </div>

      <div className="action-row no-print" style={{ marginTop: "30px", justifyContent: "flex-end" }}>
        <button className="upload-btn indigo" onClick={handleDownloadPDF}>
            <span role="img" aria-label="download">📄</span> Print / Download PDF
        </button>
      </div>
    </section>
  );
}
