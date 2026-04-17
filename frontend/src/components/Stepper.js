import React from "react";

const STEPS = [
  { num: 1, label: "Upload Syllabus" },
  { num: 2, label: "Upload Textbook" },
  { num: 3, label: "Select Topics" },
  { num: 4, label: "Semantic Mapping" },
  { num: 5, label: "Configure Pattern" },
  { num: 6, label: "Generate Questions" },
];

export default function Stepper({ currentStep, onStepClick }) {
  return (
    <div className="stepper">
      {STEPS.map((step, idx) => (
        <React.Fragment key={step.num}>
          <div
            className={`stepper-step ${currentStep === step.num ? "active" : ""} ${currentStep > step.num ? "done" : ""}`}
            onClick={() => onStepClick(step.num)}
          >
            <div className="stepper-circle">
              {currentStep > step.num ? "✓" : step.num}
            </div>
            <span className="stepper-label">{step.label}</span>
          </div>
          {idx < STEPS.length - 1 && (
            <div className={`stepper-line ${currentStep > step.num ? "done" : ""}`} />
          )}
        </React.Fragment>
      ))}
    </div>
  );
}
