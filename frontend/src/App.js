import React, { useState } from "react";
import "./App.css";

import Stepper           from "./components/Stepper";
import SyllabusUpload    from "./components/SyllabusUpload";
import TextbookUpload    from "./components/TextbookUpload";
import SemanticMapping   from "./components/SemanticMapping";
import TopicSelection    from "./components/TopicSelection";
import PatternConfig     from "./components/PatternConfig";
import GeneratedQuestions from "./components/GeneratedQuestions";

const API_BASE_URL = process.env.REACT_APP_API_URL || "http://127.0.0.1:8000";

export default function App() {
  /* ---- Step management ---- */
  const [step, setStep] = useState(1);

  /* ---- Syllabus & Topic Selection ---- */
  const [topics, setTopics]             = useState(null);
  const [syllabusLoading, setSyllabusLoading] = useState(false);
  const [selectedTopics, setSelectedTopics]   = useState({});

  /* ---- Textbook ---- */
  const [chunkCount, setChunkCount]     = useState(0);
  const [textbookLoading, setTextbookLoading] = useState(false);
  const [totalPdfPages, setTotalPdfPages]     = useState(0);
  const [pagesProcessed, setPagesProcessed]   = useState(0);

  /* ---- Pattern ---- */
  const [examName, setExamName]         = useState("BTech Degree Computer Science Examination");
  const [parts, setParts]               = useState(defaultPattern());
  const [expandedParts, setExpandedParts] = useState([0, 1]);
  const [patternLoading, setPatternLoading] = useState(false);

  /* ---- Generation ---- */
  const [generationLoading, setGenerationLoading] = useState(false);
  const [generatedQuestions, setGeneratedQuestions] = useState(null);
  const [generationError, setGenerationError]       = useState(null);

  /* =========================================================
     DERIVED STATE
     ========================================================= */

  // Extract available module names from syllabus topics
  const availableModules = topics?.modules
    ? Object.keys(topics.modules)
    : [];

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

  const uploadTextbook = async (file, pageRange) => {
    if (!file) return;
    const fd = new FormData();
    fd.append("file", file);
    if (pageRange) {
      fd.append("page_range", pageRange);
    }
    setTextbookLoading(true);
    try {
      const res  = await fetch(`${API_BASE_URL}/chunk-textbook`, { method: "POST", body: fd });
      const data = await res.json();
      setChunkCount(data.total_chunks || 0);
      setTotalPdfPages(data.total_pdf_pages || 0);
      setPagesProcessed(data.pages_processed || 0);
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
        setStep(6); // Transition to the generated questions step
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
            totalPdfPages={totalPdfPages}
            pagesProcessed={pagesProcessed}
          />
        )}

        {step === 3 && (
          <TopicSelection
            topics={topics}
            selectedTopics={selectedTopics}
            setSelectedTopics={setSelectedTopics}
            onNext={() => setStep(4)}
          />
        )}

        {step === 4 && (
          <SemanticMapping 
            selectedTopics={selectedTopics}
            onNext={() => setStep(5)} 
          />
        )}

        {step === 5 && (
          <PatternConfig
            examName={examName} setExamName={setExamName}
            parts={parts} setParts={setParts}
            expandedParts={expandedParts} setExpandedParts={setExpandedParts}
            patternLoading={patternLoading}
            onSavePattern={savePattern}
            onGenerateQuestions={generateQuestions}
            generationLoading={generationLoading}
            generationError={generationError}
            availableModules={availableModules}
          />
        )}

        {step === 6 && (
          <GeneratedQuestions 
            questions={generatedQuestions} 
            examName={examName} 
            courseTitle={topics?.course_title}
            courseCode={topics?.course_code}
            courseOutcomes={topics?.course_outcomes}
          />
        )}
      </main>
    </div>
  );
}

/* Default pattern factory (8x3M Part A, 4x12M OR Part B) */
function defaultPattern() {
  const defaultModules = ["Module I", "Module II", "Module III", "Module IV"];
  const getMod = (i) => defaultModules[i % 4]; // Distribute roughly across first 4 modules (used for Part B)

  // Required default Part A order:
  // Q1-Q2: Module I, Q3-Q4: Module II, Q5-Q6: Module III, Q7-Q8: Module IV
  const partA_modules = [
    "Module I",
    "Module I",
    "Module II",
    "Module II",
    "Module III",
    "Module III",
    "Module IV",
    "Module IV",
  ];

  const partA_questions = Array.from({ length: 8 }).map((_, i) => ({
    question_no: i + 1,
    marks: 3,
    module: partA_modules[i],
    has_internal_choice: false,
    sub_questions: null
  }));

  const partB_questions = Array.from({ length: 4 }).map((_, i) => ({
    question_no: i + 1,
    marks: 12,
    module: getMod(i),
    has_internal_choice: true,
    or_choice: { marks: 12, module: getMod(i) },
    sub_questions: null
  }));

  return [
    {
      part_name: "PART A", answer_type: "ALL",
      marks_per_question: 3, total_questions: 8,
      questions: partA_questions
    },
    {
      part_name: "PART B", answer_type: "ALL",
      marks_per_question: 12, total_questions: 4,
      questions: partB_questions
    }
  ];
}
