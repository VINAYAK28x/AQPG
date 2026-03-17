import React, { useState } from "react";

const API_BASE_URL = process.env.REACT_APP_API_URL || "http://127.0.0.1:8000";

export default function GeneratedQuestions({ questions }) {
  // Local state so individual questions can be swapped in-place
  const [localQuestions, setLocalQuestions] = useState(questions);
  // Track which question is currently regenerating: "partName-idx" or "partName-idx-or"
  const [regenerating, setRegenerating] = useState(null);

  // Sync if parent passes entirely new questions (e.g. full regeneration)
  React.useEffect(() => {
    setLocalQuestions(questions);
  }, [questions]);

  if (!localQuestions || Object.keys(localQuestions).length === 0) return null;

  const handleRegenerate = async (partName, idx, isOr = false) => {
    const key = isOr ? `${partName}-${idx}-or` : `${partName}-${idx}`;
    setRegenerating(key);

    const q = localQuestions[partName][idx];
    const module = isOr ? (q.or_question?.module || q.module) : q.module;
    const marks = isOr ? (q.or_question?.marks || q.marks) : q.marks;
    const sub_questions = isOr ? q.or_question?.sub_questions : q.sub_questions;

    try {
      const res = await fetch(`${API_BASE_URL}/regenerate-question`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          module,
          marks,
          question_no: q.question_no || idx + 1,
          sub_questions,
        }),
      });
      const data = await res.json();

      if (data.question) {
        setLocalQuestions((prev) => {
          const updated = JSON.parse(JSON.stringify(prev)); // deep clone
          if (isOr) {
            updated[partName][idx].or_question = {
              ...updated[partName][idx].or_question,
              text: data.question.text,
              classified_bloom_level: data.question.classified_bloom_level,
              source_chunk: data.question.source_chunk,
            };
          } else {
            updated[partName][idx] = {
              ...updated[partName][idx],
              text: data.question.text,
              classified_bloom_level: data.question.classified_bloom_level,
              bloom_level: data.question.bloom_level,
              source_chunk: data.question.source_chunk,
              sub_questions: data.question.sub_questions,
            };
          }
          return updated;
        });
      }
    } catch (err) {
      console.error("Regeneration failed:", err);
    }
    setRegenerating(null);
  };

  const handleDownloadPDF = () => {
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
          {Object.entries(localQuestions).map(([partName, partQuestions]) => (
            <div key={partName} className="gen-part">
              <h3 className="gen-part-name">{partName}</h3>
              <p className="gen-part-instruction">(Answer ALL questions)</p>

              {Array.isArray(partQuestions) ? (
                <div className="gen-questions-list">
                  {partQuestions.map((q, idx) => {
                    const bloomsLevel = q.classified_bloom_level || q.bloom_level;
                    const isRegenerating = regenerating === `${partName}-${idx}`;
                    const isOrRegenerating = regenerating === `${partName}-${idx}-or`;
                    return (
                      <div key={idx} className={`gen-question-group ${isRegenerating ? "regen-flash" : ""}`}>
                        <div className="gen-question-row">
                          <div className="gen-q-num">{q.question_no || idx + 1}.</div>
                          <div className="gen-q-body">
                            {(!q.sub_questions || q.sub_questions.length === 0) && (
                              <p className="gen-q-text">
                                {q.text || q.question || "—"} 
                                {bloomsLevel && <span className="gen-q-blooms-inline"> [Bloom's Level: {bloomsLevel}]</span>}
                              </p>
                            )}

                            {/* Render sub-questions if present */}
                            {q.sub_questions && q.sub_questions.length > 0 && (
                              <div className="gen-sub-questions">
                                {q.sub_questions.map((sq, sqIdx) => (
                                  <div key={sqIdx} className="gen-sub-question">
                                    <span className="gen-sq-label">({sq.label})</span>
                                    <div className="gen-sq-body">
                                      <p className="gen-q-text">
                                        {sq.text || "—"}
                                        {sq.classified_bloom_level && (
                                          <span className="gen-q-blooms-inline"> [Bloom's: {sq.classified_bloom_level}]</span>
                                        )}
                                      </p>
                                      <div className="gen-sq-marks no-print">{sq.marks}m</div>
                                    </div>
                                    <div className="gen-q-marks print-only">({sq.marks})</div>
                                  </div>
                                ))}
                              </div>
                            )}

                            {/* On-screen footer for tags and marks */}
                            {(!q.sub_questions || q.sub_questions.length === 0) ? (
                              <div className="gen-q-footer no-print">
                                <div className="gen-q-tags">
                                  {q.bloom_level && <span className="tag bloom">{q.bloom_level}</span>}
                                  {q.classified_bloom_level && q.classified_bloom_level !== q.bloom_level && (
                                    <span className="tag classified">Classified: {q.classified_bloom_level}</span>
                                  )}
                                  {q.module && <span className="tag module">{q.module}</span>}
                                </div>
                                <button
                                  className={`regen-btn ${isRegenerating ? "regen-spinning" : ""}`}
                                  onClick={() => handleRegenerate(partName, idx)}
                                  disabled={regenerating !== null}
                                  title="Regenerate this question"
                                >
                                  🔄
                                </button>
                                <div className="gen-q-marks-pill">{q.marks || 0} marks</div>
                              </div>
                            ) : (
                              /* Simplified footer for sub-question blocks */
                              <div className="gen-q-footer no-print sub-q-footer">
                                <div className="gen-q-tags">
                                  {q.module && <span className="tag module">{q.module}</span>}
                                </div>
                                <button
                                  className={`regen-btn ${isRegenerating ? "regen-spinning" : ""}`}
                                  onClick={() => handleRegenerate(partName, idx)}
                                  disabled={regenerating !== null}
                                  title="Regenerate all sub-questions"
                                >
                                  🔄
                                </button>
                                <div className="gen-q-marks-pill">{q.marks || 0} marks total</div>
                              </div>
                            )}
                          </div>
                          <div className="gen-q-marks print-only">({q.marks || 0})</div>
                        </div>

                        {/* Render Internal Choice (OR) if present */}
                        {q.has_internal_choice && q.or_question && (
                          <div className={`gen-question-or-block ${isOrRegenerating ? "regen-flash" : ""}`}>
                            <div className="gen-or-divider">— OR —</div>
                            <div className="gen-question-row">
                              <div className="gen-q-num"></div>
                              <div className="gen-q-body">
                                {(!q.or_question.sub_questions || q.or_question.sub_questions.length === 0) && (
                                  <p className="gen-q-text">
                                    {q.or_question.text || "—"}
                                    {q.or_question.classified_bloom_level && (
                                      <span className="gen-q-blooms-inline"> [Bloom's Level: {q.or_question.classified_bloom_level}]</span>
                                    )}
                                  </p>
                                )}

                                {/* Render sub-questions for OR if present */}
                                {q.or_question.sub_questions && q.or_question.sub_questions.length > 0 && (
                                  <div className="gen-sub-questions">
                                    {q.or_question.sub_questions.map((sq, sqIdx) => (
                                      <div key={sqIdx} className="gen-sub-question">
                                        <span className="gen-sq-label">({sq.label})</span>
                                        <div className="gen-sq-body">
                                          <p className="gen-q-text">
                                            {sq.text || "—"}
                                            {sq.classified_bloom_level && (
                                              <span className="gen-q-blooms-inline"> [Bloom's: {sq.classified_bloom_level}]</span>
                                            )}
                                          </p>
                                          <div className="gen-sq-marks no-print">{sq.marks}m</div>
                                        </div>
                                        <div className="gen-q-marks print-only">({sq.marks})</div>
                                      </div>
                                    ))}
                                  </div>
                                )}

                                <div className="gen-q-footer no-print">
                                  <div className="gen-q-tags">
                                    {q.or_question.module && <span className="tag module">{q.or_question.module}</span>}
                                  </div>
                                  <button
                                    className={`regen-btn ${isOrRegenerating ? "regen-spinning" : ""}`}
                                    onClick={() => handleRegenerate(partName, idx, true)}
                                    disabled={regenerating !== null}
                                    title={q.or_question.sub_questions ? "Regenerate all OR sub-questions" : "Regenerate this OR question"}
                                  >
                                    🔄
                                  </button>
                                  <div className="gen-q-marks-pill">
                                    {q.or_question.marks || q.marks || 0} marks {q.or_question.sub_questions ? 'total' : ''}
                                  </div>
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
