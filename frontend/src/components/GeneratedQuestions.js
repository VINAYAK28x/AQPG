import React from "react";

export default function GeneratedQuestions({ questions }) {
  if (!questions || Object.keys(questions).length === 0) return null;

  return (
    <section className="card generated-card">
      <h2 className="card-title">
        <span className="card-icon">📝</span> Generated Questions
      </h2>

      {Object.entries(questions).map(([partName, partQuestions]) => (
        <div key={partName} className="gen-part">
          <h3 className="gen-part-name">{partName}</h3>
          {Array.isArray(partQuestions) ? (
            partQuestions.map((q, idx) => (
              <div key={idx} className="gen-question">
                <div className="gen-q-header">
                  <span className="gen-q-num">Q{q.question_no || idx + 1}</span>
                  <span className="gen-q-marks">{q.marks || 0} marks</span>
                </div>
                <p className="gen-q-text">{q.text || q.question || "—"}</p>
                <div className="gen-q-tags">
                  {q.bloom_level && <span className="tag bloom">{q.bloom_level}</span>}
                  {q.classified_bloom_level && q.classified_bloom_level !== q.bloom_level && (
                    <span className="tag classified">Classified: {q.classified_bloom_level}</span>
                  )}
                  {q.module && <span className="tag module">{q.module}</span>}
                </div>
              </div>
            ))
          ) : (
            <p>{String(partQuestions)}</p>
          )}
        </div>
      ))}
    </section>
  );
}
