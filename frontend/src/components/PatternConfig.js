import React from "react";


export default function PatternConfig({
  examName, setExamName,
  parts, setParts,
  expandedParts, setExpandedParts,
  patternLoading,
  onSavePattern,
  onGenerateQuestions,
  generationLoading,
  generationError,
  availableModules,
}) {
  // Use dynamic module list if available, fallback to default
  const MODULES = availableModules && availableModules.length > 0
    ? availableModules
    : ["Module I", "Module II", "Module III", "Module IV"];

  const updatePart = (idx, field, value) => {
    const p = [...parts]; p[idx][field] = value; setParts(p);
  };

  const updateQuestion = (pIdx, qIdx, field, value) => {
    const p = [...parts]; p[pIdx].questions[qIdx][field] = value; setParts(p);
  };

  const addPart = () => {
    const letter = String.fromCharCode(64 + parts.length + 1);
    setParts([...parts, {
      part_name: `PART ${letter}`, answer_type: "ALL",
      marks_per_question: 1, total_questions: 1,
      questions_to_answer: null,
      questions: [{ question_no: 1, marks: 1, module: MODULES[0], has_internal_choice: false, sub_questions: null }]
    }]);
  };

  const removePart = (idx) => setParts(parts.filter((_, i) => i !== idx));

  const addQ = (pIdx) => {
    const p = [...parts];
    const n = p[pIdx].questions.length + 1;
    p[pIdx].questions.push({ question_no: n, marks: p[pIdx].marks_per_question || 1, module: MODULES[0], has_internal_choice: false, sub_questions: null });
    p[pIdx].total_questions = p[pIdx].questions.length;
    setParts(p);
  };

  const removeQ = (pIdx, qIdx) => {
    const p = [...parts];
    p[pIdx].questions = p[pIdx].questions.filter((_, i) => i !== qIdx).map((q, i) => ({ ...q, question_no: i + 1 }));
    p[pIdx].total_questions = p[pIdx].questions.length;
    setParts(p);
  };

  const toggleExpand = (idx) =>
    setExpandedParts(prev => prev.includes(idx) ? prev.filter(i => i !== idx) : [...prev, idx]);

  const totalQ = parts.reduce((s, p) => s + (p.questions?.length || 0), 0);
  const totalM = parts.reduce((s, p) => s + (p.questions?.reduce((a, q) => a + (q.marks || 0), 0) || 0), 0);

  return (
    <section className="card">
      <h2 className="card-title">
        <span className="card-icon">⚙️</span> Question Paper Pattern
      </h2>

      {/* Summary */}
      {examName && parts.length > 0 && (
        <div className="summary-bar">
          <span className="summary-pill">{totalQ} Questions</span>
          <span className="summary-pill">{totalM} Marks</span>
          {parts.map((p, i) => (
            <span key={i} className="summary-pill dim">{p.part_name}: {p.questions?.length || 0}Q</span>
          ))}
        </div>
      )}

      {/* Exam Name */}
      <div className="form-group">
        <label>Exam Name</label>
        <input type="text" value={examName} onChange={e => setExamName(e.target.value)} placeholder="e.g., Mid Semester Exam" />
      </div>

      {/* Parts */}
      <div className="parts-container">
        {parts.map((part, pIdx) => (
          <div key={pIdx} className="part-block">
            <div className="part-header" onClick={() => toggleExpand(pIdx)}>
              <div className="part-header-left">
                <span className="expand-icon">{expandedParts.includes(pIdx) ? "▼" : "▶"}</span>
                <h4 className="part-name">{part.part_name}</h4>
                <span className="part-stat">{part.questions?.length || 0}Q • {part.questions?.reduce((s, q) => s + (q.marks || 0), 0) || 0}M</span>
              </div>
              {parts.length > 1 && (
                <button className="btn-sm red" onClick={e => { e.stopPropagation(); removePart(pIdx); }}>Remove</button>
              )}
            </div>

            {expandedParts.includes(pIdx) && (
              <>
                <div className="part-settings">
                  <div className="form-row-2">
                    <div className="form-group">
                      <label>Part Name</label>
                      <input type="text" value={part.part_name} onChange={e => updatePart(pIdx, "part_name", e.target.value)} />
                    </div>
                    <div className="form-group">
                      <label>Answer Type</label>
                      <select value={part.answer_type} onChange={e => updatePart(pIdx, "answer_type", e.target.value)}>
                        <option value="ALL">ALL (Answer All)</option>
                        <option value="ANY">ANY (Answer Any N)</option>
                      </select>
                    </div>
                  </div>
                </div>

                <div className="questions-box">
                  <h5 className="questions-heading">Questions in {part.part_name}</h5>
                  {part.questions?.map((q, qIdx) => (
                    <React.Fragment key={qIdx}>
                    <div className="question-row">
                      <span className="q-num">Q{q.question_no}</span>
                      <div className="q-fields">
                        <div className="form-group mini">
                          <label>Marks</label>
                          <input type="number" value={q.marks} min="1" onChange={e => updateQuestion(pIdx, qIdx, "marks", parseInt(e.target.value))} />
                        </div>
                        <div className="form-group mini">
                          <label>Module</label>
                          <select value={q.module} onChange={e => updateQuestion(pIdx, qIdx, "module", e.target.value)}>
                            {MODULES.map(m => <option key={m} value={m}>{m}</option>)}
                          </select>
                        </div>
                        <div className="form-group mini choice-toggle">
                          <label>Choice (OR)</label>
                          <label className="switch">
                            <input
                              type="checkbox"
                              checked={q.has_internal_choice}
                              onChange={e => {
                                const checked = e.target.checked;
                                // Initialize default or_choice if turning on
                                if (checked && !q.or_choice) {
                                  updateQuestion(pIdx, qIdx, "or_choice", { marks: q.marks, module: q.module });
                                }
                                updateQuestion(pIdx, qIdx, "has_internal_choice", checked);
                              }}
                            />
                            <span className="switch-slider"></span>
                          </label>
                        </div>
                      </div>
                      {part.questions.length > 1 && (
                        <button className="btn-sm orange" onClick={() => removeQ(pIdx, qIdx)}>✕</button>
                      )}
                    </div>
                    {/* Render extra sub-panel for OR choice if active */}
                    {q.has_internal_choice && (
                      <div className="or-choice-panel">
                        <div className="or-choice-indicator">↳</div>
                        <div className="or-choice-fields">
                          <span className="or-choice-label">Alternative Question (OR)</span>
                          <div className="form-group mini">
                            <label>Marks</label>
                            <input 
                              type="number" min="1" 
                              value={q.or_choice?.marks || q.marks} 
                              onChange={e => updateQuestion(pIdx, qIdx, "or_choice", { ...q.or_choice, marks: parseInt(e.target.value) })}
                            />
                          </div>
                          <div className="form-group mini">
                            <label>Module</label>
                            <select 
                              value={q.or_choice?.module || q.module} 
                              onChange={e => updateQuestion(pIdx, qIdx, "or_choice", { ...q.or_choice, module: e.target.value })}
                            >
                              {MODULES.map(m => <option key={`or-${m}`} value={m}>{m}</option>)}
                            </select>
                          </div>
                        </div>
                      </div>
                    )}
                    </React.Fragment>
                  ))}
                  <button className="btn-sm green full-width" onClick={() => addQ(pIdx)}>+ Add Question</button>
                </div>
              </>
            )}
          </div>
        ))}
      </div>

      <div className="action-row">
        <button className="btn green" onClick={addPart}>+ Add Part</button>
        <button className="btn amber" onClick={onSavePattern} disabled={patternLoading}>
          {patternLoading ? "Saving…" : "💾 Save Pattern"}
        </button>
        <button className="btn indigo" onClick={onGenerateQuestions} disabled={generationLoading}>
          {generationLoading ? "Generating…" : "🚀 Generate Questions"}
        </button>
      </div>

      {generationError && <div className="error-box">{generationError}</div>}
    </section>
  );
}
