import React from "react";

export default function SyllabusUpload({
  topics,
  syllabusLoading,
  onUpload,
  onNext,
}) {
  // Handle new structured format: { course_title, course_code, modules: { ... } }
  const courseTitle = topics?.course_title;
  const courseCode = topics?.course_code;
  const modules = topics?.modules || {};

  return (
    <section className="card">
      <h2 className="card-title">
        <span className="card-icon">📋</span> Syllabus Upload &amp; Topic Extraction
      </h2>

      <label className="upload-btn blue">
        {syllabusLoading ? "Processing…" : "Upload Syllabus PDF"}
        <input type="file" accept=".pdf" onChange={onUpload} hidden />
      </label>

      {syllabusLoading && <p className="loading-text">Extracting syllabus topics…</p>}

      {topics && Object.keys(modules).length > 0 && (
        <>
          {/* Course info header */}
          {(courseTitle || courseCode) && (
            <div className="course-info-bar">
              {courseTitle && courseTitle !== "Unknown" && (
                <span className="course-info-pill title">{courseTitle}</span>
              )}
              {courseCode && courseCode !== "Unknown" && (
                <span className="course-info-pill code">{courseCode}</span>
              )}
            </div>
          )}

          <div className="modules-grid">
            {Object.entries(modules).map(([mod, data]) => {
              // Support both new format (data.topics) and legacy (data as array)
              const topicList = Array.isArray(data) ? data : (data.topics || []);
              return (
                <div key={mod} className="module-card">
                  <span className="module-badge">{mod}</span>
                  <ul className="topic-list">
                    {topicList.map((t, i) => (
                      <li key={i}>{t}</li>
                    ))}
                  </ul>
                </div>
              );
            })}
          </div>

          <button className="btn green next-btn" onClick={onNext}>
            Continue to Textbook Upload →
          </button>
        </>
      )}
    </section>
  );
}
