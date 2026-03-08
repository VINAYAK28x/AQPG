import React, { useState } from "react";
import "./App.css";

import Stepper           from "./components/Stepper";
import SyllabusUpload    from "./components/SyllabusUpload";
import TextbookUpload    from "./components/TextbookUpload";
import SemanticMapping   from "./components/SemanticMapping";
import PatternConfig     from "./components/PatternConfig";
import GeneratedQuestions from "./components/GeneratedQuestions";

const API_BASE_URL = process.env.REACT_APP_API_URL || "http://127.0.0.1:8000";

export default function App() {
  /* ---- Step management ---- */
  const [step, setStep] = useState(1);

  /* ---- Syllabus ---- */
  const [topics, setTopics]             = useState(null);
  const [syllabusLoading, setSyllabusLoading] = useState(false);

  /* ---- Textbook ---- */
  const [chunkCount, setChunkCount]     = useState(0);
  const [textbookLoading, setTextbookLoading] = useState(false);

  /* ---- Pattern ---- */
  const [examName, setExamName]         = useState("");
  const [parts, setParts]               = useState([defaultPart()]);
  const [expandedParts, setExpandedParts] = useState([0]);
  const [patternLoading, setPatternLoading] = useState(false);

  /* ---- Generation ---- */
  const [generationLoading, setGenerationLoading] = useState(false);
  const [generatedQuestions, setGeneratedQuestions] = useState(null);
  const [generationError, setGenerationError]       = useState(null);

  /* =========================================================
     HANDLERS
     ========================================================= */

  const uploadSyllabus = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const fd = new FormData();
    fd.append("file", file);
    setSyllabusLoading(true);
    try {
      const res  = await fetch(`${API_BASE_URL}/extract-syllabus`, { method: "POST", body: fd });
      const data = await res.json();
      setTopics(data);
    } catch { alert("Error uploading syllabus"); }
    setSyllabusLoading(false);
  };

  const uploadTextbook = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const fd = new FormData();
    fd.append("file", file);
    setTextbookLoading(true);
    try {
      const res  = await fetch(`${API_BASE_URL}/chunk-textbook`, { method: "POST", body: fd });
      const data = await res.json();
      setChunkCount(data.total_chunks || 0);
    } catch { alert("Error uploading textbook"); }
    setTextbookLoading(false);
  };

  const savePattern = async () => {
    if (!examName) { alert("Enter exam name"); return; }
    setPatternLoading(true);
    try {
      await fetch(`${API_BASE_URL}/set-question-pattern`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ exam_name: examName, parts }),
      });
      alert("Pattern saved!");
    } catch (err) { alert("Error: " + err.message); }
    setPatternLoading(false);
  };

  const generateQuestions = async () => {
    if (!examName) { setGenerationError("Enter exam name"); return; }
    setGenerationLoading(true);
    setGenerationError(null);
    try {
      const res = await fetch(`${API_BASE_URL}/generate-questions`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ exam_name: examName, parts }),
      });
      const data = await res.json();
      if (data.error) { 
        setGenerationError(data.error); 
      } else { 
        setGeneratedQuestions(data.questions || {}); 
        setStep(5); // Transition to the generated questions step
      }
    } catch (err) { setGenerationError("Error: " + err.message); }
    setGenerationLoading(false);
  };

  /* =========================================================
     RENDER
     ========================================================= */

  return (
    <div className="app">
      <header className="app-header">
        <h1>Question Paper Generation System</h1>
        <p>Powered by SBERT · Flan-T5 · DistilBERT</p>
      </header>

      <Stepper currentStep={step} onStepClick={setStep} />

      <main className="app-main">
        {step === 1 && (
          <SyllabusUpload
            topics={topics}
            syllabusLoading={syllabusLoading}
            onUpload={uploadSyllabus}
            onNext={() => setStep(2)}
          />
        )}

        {step === 2 && (
          <TextbookUpload
            chunkCount={chunkCount}
            textbookLoading={textbookLoading}
            onUpload={uploadTextbook}
            onNext={() => setStep(3)}
          />
        )}

        {step === 3 && (
          <SemanticMapping onNext={() => setStep(4)} />
        )}

        {step === 4 && (
          <PatternConfig
            examName={examName} setExamName={setExamName}
            parts={parts} setParts={setParts}
            expandedParts={expandedParts} setExpandedParts={setExpandedParts}
            patternLoading={patternLoading}
            onSavePattern={savePattern}
            onGenerateQuestions={generateQuestions}
            generationLoading={generationLoading}
            generationError={generationError}
          />
        )}

        {step === 5 && (
          <GeneratedQuestions questions={generatedQuestions} />
        )}
      </main>
    </div>
  );
}

/* Default part factory */
function defaultPart() {
  return {
    part_name: "PART A", answer_type: "ALL",
    marks_per_question: 1, total_questions: 2,
    questions_to_answer: null, bloom_levels: ["Remember"],
    questions: [
      { question_no: 1, marks: 1, module: "Module 1", bloom_level: "Remember", has_internal_choice: false, sub_questions: null },
      { question_no: 2, marks: 1, module: "Module 2", bloom_level: "Remember", has_internal_choice: false, sub_questions: null },
    ],
  };
}
