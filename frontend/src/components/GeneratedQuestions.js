import React, { useState } from "react";

const API_BASE_URL = process.env.REACT_APP_API_URL || "http://127.0.0.1:8000";

/** Map verbose Bloom's level names to short codes for the printed paper. */
function bloomToCode(level) {
  if (!level) return "L1";
  const l = level.toLowerCase().trim();
  if (l.startsWith("l") && /^l\d$/.test(l)) return l.toUpperCase(); // already L1–L6
  if (l.includes("remember")) return "L1";
  if (l.includes("understand")) return "L2";
  if (l.includes("apply")) return "L3";
  if (l.includes("analy")) return "L4";   // analyze / analyse
  if (l.includes("evaluat")) return "L5";
  if (l.includes("create")) return "L6";
  return "L1";
}

export default function GeneratedQuestions({ questions, examName, courseTitle, courseCode, courseOutcomes }) {
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
              sub_questions: data.question.sub_questions,
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
      <div className="print-wrapper university-paper-format">
        {/* Basic Header for Screen */}
        <div className="print-header no-print">
          <h1>Generated Question Paper</h1>
          {examName ? <p className="print-exam-name">{examName}</p> : null}
          <hr className="print-divider" />
        </div>

        {/* Formal University Header for Print */}
        <div className="print-header print-only">
          <h2 className="exam-title">{examName || "B.Tech. Degree IV Semester Examination"}</h2>
          <h3 className="course-title">
            {courseCode && courseCode !== "Unknown" ? `${courseCode} ` : ""}
            {courseTitle && courseTitle !== "Unknown" ? courseTitle.toUpperCase() : ""}
          </h3>
          <h4 className="scheme-title">(2019 Scheme)</h4>
          
          <div className="meta-row">
            <span>Time: 3 Hours</span>
            <span>Maximum Marks: 60</span>
          </div>

          <div className="course-outcomes-section">
            <div className="outcomes-heading">Course Outcomes</div>
            <div className="outcomes-sub-heading">On successful completion of the course, the students will be able to:</div>
            {courseOutcomes && courseOutcomes.length > 0 ? (
              <ul className="outcomes-list">
                {courseOutcomes.map((co, i) => (
                  <li key={i}>{co}</li>
                ))}
              </ul>
            ) : (
              <ul className="outcomes-list">
                <li>(No course outcomes extracted from the uploaded syllabus)</li>
              </ul>
            )}
            <div className="blooms-legend">Bloom's Taxonomy Levels (BL): L1 – Remember, L2 – Understand, L3 – Apply, L4 – Analyze, L5 – Evaluate, L6 – Create</div>
            <div className="po-legend">PO - Programme Outcome</div>
          </div>
        </div>

        <div className="print-content">
          {Object.entries(localQuestions).map(([partName, partQuestions]) => {
            // Heuristically calculate marks breakdown for the part header (e.g. 8 x 3 = 24)
            let eqStr = "";
            if (Array.isArray(partQuestions) && partQuestions.length > 0) {
              const count = partQuestions.length;
              const unitMarks = partQuestions[0].marks || 0;
              eqStr = `(${count} × ${unitMarks} = ${count * unitMarks})`;
            }

            return (
            <div key={partName} className="gen-part">
              <h3 className="gen-part-name">{partName}</h3>
              <p className="gen-part-instruction">(Answer ALL questions)</p>
              
              <div className="gen-part-table-header print-only">
                <div className="gen-part-eq">{eqStr}</div>
                <div className="gen-part-cols-header">
                  <span>Marks</span>
                  <span>BL</span>
                  <span>CO</span>
                  <span>PO</span>
                </div>
              </div>

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
                                {bloomsLevel && <span className="gen-q-blooms-inline no-print"> [Bloom's Level: {bloomsLevel}]</span>}
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
                                          <span className="gen-q-blooms-inline no-print"> [Bloom's: {sq.classified_bloom_level}]</span>
                                        )}
                                      </p>
                                      <div className="gen-sq-marks no-print">{sq.marks}m</div>
                                    </div>
                                    <div className="gen-q-meta-cols print-only sub-meta">
                                      <span className="col-marks">{sq.marks}</span>
                                      <span className="col-bl">{bloomToCode(sq.classified_bloom_level || bloomsLevel)}</span>
                                      <span className="col-co">{(sqIdx % 5) + 1}</span>
                                      <span className="col-po">1,{(sqIdx % 3) + 2}</span>
                                    </div>
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
                            {/* Main Question Meta Columns */}
                            {(!q.sub_questions || q.sub_questions.length === 0) ? (
                              <div className="gen-q-meta-cols print-only">
                                <span className="col-marks">{q.marks || 0}</span>
                                <span className="col-bl">{bloomToCode(bloomsLevel)}</span>
                                <span className="col-co">{(idx % 5) + 1}</span>
                                <span className="col-po">1,{(idx % 3) + 2}</span>
                              </div>
                            ) : (
                               <div className="gen-q-meta-cols print-only empty-meta">
                               </div>
                            )}
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
                                      <span className="gen-q-blooms-inline no-print"> [Bloom's Level: {q.or_question.classified_bloom_level}]</span>
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
                                              <span className="gen-q-blooms-inline no-print"> [Bloom's: {sq.classified_bloom_level}]</span>
                                            )}
                                          </p>
                                          <div className="gen-sq-marks no-print">{sq.marks}m</div>
                                        </div>
                                        <div className="gen-q-meta-cols print-only sub-meta">
                                          <span className="col-marks">{sq.marks}</span>
                                          <span className="col-bl">{bloomToCode(sq.classified_bloom_level || bloomsLevel)}</span>
                                          <span className="col-co">{(sqIdx % 5) + 1}</span>
                                          <span className="col-po">1,{(sqIdx % 3) + 2}</span>
                                        </div>
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
                                {(!q.or_question.sub_questions || q.or_question.sub_questions.length === 0) ? (
                                  <div className="gen-q-meta-cols print-only">
                                    <span className="col-marks">{q.or_question.marks || q.marks || 0}</span>
                                    <span className="col-bl">{bloomToCode(q.or_question.classified_bloom_level || bloomsLevel)}</span>
                                    <span className="col-co">{(idx % 5) + 1}</span>
                                    <span className="col-po">1,{(idx % 3) + 2}</span>
                                  </div>
                                ) : (
                                  <div className="gen-q-meta-cols print-only empty-meta">
                                  </div>
                                )}
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
            );
          })}
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
