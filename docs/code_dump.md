# Full Codebase Dump

## Frontend Code

---

### `frontend/src/App.css`

```css
/* ===================================================
   QUESTION PAPER GENERATION SYSTEM — Design System
   =================================================== */

/* ---------- RESET & BASE ---------- */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

body {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%);
  color: #e2e8f0;
  min-height: 100vh;
  -webkit-font-smoothing: antialiased;
}

/* ---------- APP LAYOUT ---------- */
.app {
  max-width: 960px;
  margin: 0 auto;
  padding: 40px 24px 80px;
}

.app-header {
  text-align: center;
  margin-bottom: 40px;
}
.app-header h1 {
  font-size: 32px;
  font-weight: 700;
  background: linear-gradient(135deg, #818cf8, #c084fc, #f0abfc);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 6px;
}
.app-header p {
  font-size: 14px;
  color: #94a3b8;
  letter-spacing: 2px;
  text-transform: uppercase;
}

.app-main { margin-top: 32px; }

/* ---------- STEPPER ---------- */
.stepper {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0;
  margin-bottom: 8px;
}
.stepper-step {
  display: flex;
  flex-direction: column;
  align-items: center;
  cursor: pointer;
  transition: transform 0.2s;
  padding: 8px 12px;
}
.stepper-step:hover { transform: translateY(-2px); }

.stepper-circle {
  width: 36px; height: 36px;
  border-radius: 50%;
  background: rgba(255,255,255,0.08);
  border: 2px solid rgba(255,255,255,0.15);
  display: flex; align-items: center; justify-content: center;
  font-size: 14px; font-weight: 600;
  transition: all 0.3s;
  color: #94a3b8;
}
.stepper-step.active .stepper-circle {
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  border-color: #a78bfa;
  color: #fff;
  box-shadow: 0 0 20px rgba(99,102,241,0.4);
}
.stepper-step.done .stepper-circle {
  background: linear-gradient(135deg, #10b981, #059669);
  border-color: #34d399;
  color: #fff;
}

.stepper-label {
  font-size: 11px;
  margin-top: 6px;
  color: #64748b;
  font-weight: 500;
  text-align: center;
  white-space: nowrap;
}
.stepper-step.active .stepper-label { color: #c4b5fd; }
.stepper-step.done .stepper-label { color: #6ee7b7; }

.stepper-line {
  width: 40px; height: 2px;
  background: rgba(255,255,255,0.1);
  margin-bottom: 20px;
  transition: background 0.3s;
}
.stepper-line.done { background: linear-gradient(90deg, #10b981, #6366f1); }

/* ---------- CARDS ---------- */
.card {
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 16px;
  padding: 32px;
  backdrop-filter: blur(12px);
  animation: fadeIn 0.3s ease;
}
@keyframes fadeIn { from { opacity: 0; transform: translateY(12px); } to { opacity: 1; transform: translateY(0); } }

.card-title {
  font-size: 20px;
  font-weight: 600;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 10px;
}
.card-icon { font-size: 24px; }
.card-desc {
  color: #94a3b8;
  font-size: 14px;
  margin-bottom: 20px;
  line-height: 1.6;
}

/* ---------- BUTTONS ---------- */
.upload-btn {
  display: inline-block;
  padding: 12px 28px;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  border: none;
  transition: all 0.2s;
  letter-spacing: 0.3px;
}
.upload-btn:hover { transform: translateY(-2px); box-shadow: 0 8px 24px rgba(0,0,0,0.3); }
.upload-btn.blue   { background: linear-gradient(135deg, #3b82f6, #2563eb); color: #fff; }
.upload-btn.purple { background: linear-gradient(135deg, #8b5cf6, #7c3aed); color: #fff; }

.btn {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 10px 22px;
  border-radius: 10px;
  border: none;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  color: #fff;
  transition: all 0.2s;
}
.btn:hover:not(:disabled) { transform: translateY(-1px); filter: brightness(1.1); }
.btn:disabled { opacity: 0.5; cursor: not-allowed; }
.btn.green  { background: linear-gradient(135deg, #10b981, #059669); }
.btn.amber  { background: linear-gradient(135deg, #f59e0b, #d97706); }
.btn.indigo { background: linear-gradient(135deg, #6366f1, #4f46e5); }
.btn.red    { background: linear-gradient(135deg, #f87171, #ef4444); }

.btn-sm {
  padding: 5px 14px;
  border-radius: 8px;
  border: none;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  color: #fff;
  transition: all 0.2s;
}
.btn-sm.red    { background: linear-gradient(135deg, #f87171, #ef4444); }
.btn-sm.orange { background: linear-gradient(135deg, #fb923c, #f97316); }
.btn-sm.green  { background: linear-gradient(135deg, #34d399, #10b981); }
.btn-sm.full-width { width: 100%; margin-top: 8px; padding: 8px; }

.next-btn { margin-top: 20px; }

.action-row {
  display: flex; gap: 12px;
  flex-wrap: wrap;
  margin-top: 20px;
}

/* ---------- TEXTBOOK UPLOAD: PAGE RANGE ---------- */
.page-range-section {
  margin-top: 20px;
  padding: 20px;
  background: rgba(0,0,0,0.15);
  border-radius: 12px;
  border: 1px solid rgba(255,255,255,0.05);
  animation: fadeIn 0.3s ease;
}

.page-toggle-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.page-toggle-label {
  font-size: 14px;
  font-weight: 600;
  color: #e2e8f0;
}

.page-range-input-group {
  margin-bottom: 16px;
  animation: fadeIn 0.3s ease;
}

.page-range-input {
  width: 100%;
  max-width: 400px;
  padding: 10px 14px;
  border-radius: 8px;
  border: 1px solid rgba(129,140,248,0.4);
  background: rgba(255,255,255,0.06);
  color: #fff;
  font-size: 14px;
  font-family: monospace;
}
.page-range-input:focus {
  outline: none;
  border-color: #818cf8;
  box-shadow: 0 0 0 2px rgba(129,140,248,0.2);
}

.page-range-hint {
  font-size: 12px;
  color: #94a3b8;
  margin-top: 6px;
}
.page-range-hint strong {
  color: #cbd5e1;
}

/* ---------- LOADING & ERROR ---------- */
.loading-text {
  margin-top: 12px;
  color: #93c5fd;
  font-style: italic;
  font-size: 14px;
  animation: pulse 1.5s infinite;
}
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }

.error-box {
  margin-top: 16px;
  padding: 12px 16px;
  background: rgba(239,68,68,0.12);
  border: 1px solid rgba(239,68,68,0.3);
  border-radius: 10px;
  color: #fca5a5;
  font-size: 14px;
}

/* ---------- SYLLABUS COURSE INFO & MODULES GRID ---------- */
.course-info-bar {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 24px;
  margin-top: 20px;
}
.course-info-pill {
  padding: 6px 16px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 600;
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.1);
}
.course-info-pill.title {
  color: #a78bfa;
  border-color: rgba(167,139,250,0.3);
  background: rgba(167,139,250,0.1);
}
.course-info-pill.code {
  color: #60a5fa;
  border-color: rgba(96,165,250,0.3);
  background: rgba(96,165,250,0.1);
  font-family: monospace;
}

.modules-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 16px;
}
.module-card {
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 12px;
  padding: 16px;
}
.module-badge {
  display: inline-block;
  padding: 4px 14px;
  border-radius: 20px;
  background: linear-gradient(135deg, rgba(99,102,241,0.3), rgba(139,92,246,0.3));
  font-size: 12px;
  font-weight: 600;
  color: #c4b5fd;
  margin-bottom: 10px;
}
.topic-list {
  list-style: none;
  padding: 0;
}
.topic-list li {
  padding: 4px 0;
  font-size: 13px;
  color: #cbd5e1;
  border-bottom: 1px solid rgba(255,255,255,0.04);
}
.topic-list li::before {
  content: "›";
  color: #818cf8;
  margin-right: 8px;
  font-weight: 700;
}

/* ---------- CHUNK RESULT ---------- */
.chunk-result { margin-top: 20px; }
.result-badges-row {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
  margin-bottom: 16px;
}
.result-badge {
  display: inline-flex;
  align-items: baseline;
  gap: 8px;
  background: rgba(16,185,129,0.12);
  border: 1px solid rgba(52,211,153,0.3);
  border-radius: 12px;
  padding: 12px 20px;
}
.result-badge.pages-badge {
  background: rgba(59,130,246,0.12);
  border-color: rgba(96,165,250,0.3);
}
.result-badge.pages-badge .result-number { color: #60a5fa; }
.result-badge.pages-badge .result-label { color: #93c5fd; }

.result-number {
  font-size: 28px;
  font-weight: 700;
  color: #34d399;
}
.result-label {
  font-size: 14px;
  color: #6ee7b7;
}

/* ---------- SEMANTIC MAPPING ---------- */
.mapping-stats {
  display: flex; gap: 12px;
  margin: 20px 0;
  flex-wrap: wrap;
}
.stat-pill {
  display: flex;
  flex-direction: column;
  align-items: center;
  background: rgba(99,102,241,0.12);
  border: 1px solid rgba(129,140,248,0.3);
  border-radius: 12px;
  padding: 14px 24px;
  flex: 1;
  min-width: 120px;
}
.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #a5b4fc;
}
.stat-label {
  font-size: 12px;
  color: #94a3b8;
  margin-top: 2px;
}

.mapping-results { margin-top: 16px; }
.mapping-item {
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 10px;
  padding: 16px;
  margin-bottom: 12px;
}
.mapping-topic {
  font-size: 16px;
  font-weight: 700;
  color: #c4b5fd;
  margin-bottom: 10px;
  border-bottom: 1px solid rgba(255,255,255,0.06);
  padding-bottom: 6px;
}
.mapping-topic-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 12px;
}
.topic-tag {
  font-size: 12px;
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.1);
  padding: 3px 8px;
  border-radius: 4px;
  color: #cbd5e1;
}
.topic-tag.dim {
  color: #64748b;
  font-style: italic;
  border: none;
  background: transparent;
}

.mapping-chunks {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.chunk-tag {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 16px;
  background: rgba(16,185,129,0.15);
  border: 1px solid rgba(52,211,153,0.3);
  font-size: 12px;
  color: #6ee7b7;
  font-weight: 600;
}
.chunk-tag small { opacity: 0.8; font-weight: normal; }

/* ---------- FORM ELEMENTS ---------- */
.form-group {
  display: flex;
  flex-direction: column;
  margin-bottom: 14px;
}
.form-group label {
  font-size: 12px;
  font-weight: 600;
  color: #94a3b8;
  margin-bottom: 5px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
.form-group input[type="text"],
.form-group input[type="number"],
.form-group select {
  padding: 9px 14px;
  border-radius: 8px;
  border: 1px solid rgba(255,255,255,0.12);
  background: rgba(255,255,255,0.06);
  color: #e2e8f0;
  font-size: 14px;
  font-family: inherit;
  transition: border-color 0.2s;
}
.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: #818cf8;
}
.form-group select option {
  background: #1e293b;
  color: #e2e8f0;
}

.form-group.mini { margin-bottom: 0; }
.form-group.mini input,
.form-group.mini select {
  padding: 6px 10px;
  font-size: 13px;
}

/* Toggle Switch instead of Checkbox */
.switch {
  position: relative;
  display: inline-block;
  width: 44px;
  height: 24px;
}
.switch input { 
  opacity: 0;
  width: 0;
  height: 0;
}
.switch-slider {
  position: absolute;
  cursor: pointer;
  top: 0; left: 0; right: 0; bottom: 0;
  background-color: rgba(255,255,255,0.1);
  transition: .3s;
  border-radius: 24px;
  border: 1px solid rgba(255,255,255,0.2);
}
.switch-slider:before {
  position: absolute;
  content: "";
  height: 18px;
  width: 18px;
  left: 2px;
  bottom: 2px;
  background-color: #94a3b8;
  transition: .3s;
  border-radius: 50%;
}
input:checked + .switch-slider {
  background-color: #6366f1;
  border-color: #818cf8;
}
input:checked + .switch-slider:before {
  transform: translateX(20px);
  background-color: #fff;
}

.form-group.choice-toggle {
  display: flex;
  flex-direction: column;
  align-items: center; /* Center horizontally in its flex column */
  justify-content: flex-start;
}

.form-row-2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
}

.form-row-3 {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 14px;
}

/* ---------- SUMMARY BAR ---------- */
.summary-bar {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 20px;
  padding: 12px 16px;
  background: rgba(16,185,129,0.08);
  border: 1px solid rgba(52,211,153,0.2);
  border-radius: 10px;
}
.summary-pill {
  padding: 4px 12px;
  border-radius: 16px;
  background: rgba(0,0,0,0.2);
  font-size: 12px;
  font-weight: 600;
  color: #6ee7b7;
}
.summary-pill.dim { color: #94a3b8; }

/* ---------- PATTERN CONFIG ---------- */
.parts-container { margin-top: 16px; }

.part-block {
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 14px;
}
.part-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  padding-bottom: 10px;
  border-bottom: 1px solid rgba(255,255,255,0.06);
  margin-bottom: 12px;
}
.part-header-left {
  display: flex;
  align-items: center;
  gap: 10px;
}
.expand-icon {
  font-size: 12px;
  color: #fbbf24;
  width: 20px;
}
.part-name {
  font-size: 15px;
  font-weight: 600;
  color: #fbbf24;
  margin: 0;
}
.part-stat {
  font-size: 12px;
  color: #64748b;
  font-style: italic;
}
.part-settings {
  margin-bottom: 16px;
  padding-bottom: 14px;
  border-bottom: 1px solid rgba(255,255,255,0.06);
}

.questions-box {
  background: rgba(0,0,0,0.15);
  border-radius: 10px;
  padding: 14px;
}
.questions-heading {
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
  color: #64748b;
  letter-spacing: 1px;
  margin-bottom: 12px;
}

.question-row {
  display: flex;
  align-items: center;
  gap: 12px;
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 8px;
  padding: 10px 14px;
  margin-bottom: 8px;
}
.q-num {
  font-weight: 700;
  font-size: 13px;
  color: #818cf8;
  min-width: 30px;
}
.q-fields {
  display: flex;
  gap: 10px;
  flex: 1;
  flex-wrap: wrap;
  align-items: flex-start;
}
.q-fields .form-group { flex: 1; min-width: 80px; }

.or-choice-panel {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-left: 20px;
  margin-bottom: 12px;
  padding: 10px 14px;
  background: rgba(99, 102, 241, 0.08); /* Indigo tint */
  border-left: 3px solid #818cf8;
  border-radius: 6px;
  border-bottom-right-radius: 8px;
  border-top-right-radius: 8px;
}
.or-choice-indicator {
  font-size: 18px;
  color: #818cf8;
  font-weight: bold;
}
.or-choice-fields {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
  flex-wrap: wrap;
}
.or-choice-label {
  font-size: 13px;
  font-weight: 700;
  color: #c084fc;
  margin-left: 6px;
}
.or-choice-indicator {
  font-family: monospace;
  color: #c084fc;
  font-weight: bold;
  font-size: 16px;
}
.error-text {
  color: #f87171 !important;
  font-weight: 700;
}
.question-setup-block {
  margin-bottom: 12px;
  padding: 10px;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.05);
  transition: all 0.2s ease;
}
.question-setup-block.has-choice {
  border-color: rgba(192, 132, 252, 0.2);
  background: rgba(192, 132, 252, 0.03);
}
.or-header-row {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-bottom: 8px;
}
.or-fields-row {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  padding-left: 20px;
}
.sub-q-footer {
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  padding-top: 8px !important;
  margin-top: 4px;
}


/* ---------- SUB-QUESTIONS (PATTERN CONFIG) ---------- */
.sub-questions-panel {
  margin-left: 32px;
  margin-top: 8px;
  margin-bottom: 10px;
  padding: 12px 14px;
  background: rgba(250, 204, 21, 0.04);
  border-left: 3px solid #fbbf24;
  border-radius: 4px 8px 8px 4px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}
.sub-questions-panel.or-sub-panel {
  background: rgba(192, 132, 252, 0.04);
  border-left-color: #c084fc;
}
.sub-questions-panel.or-sub-panel .sub-questions-title {
  color: #c084fc;
}
.sub-questions-panel.or-sub-panel .sq-label {
  color: #c084fc;
}
.sub-questions-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 10px;
}
.sub-questions-title {
  font-size: 12px;
  font-weight: 700;
  color: #fbbf24;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
.sub-questions-summary {
  font-size: 11px;
  color: #94a3b8;
  font-style: italic;
}
.sub-question-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 6px;
  padding: 6px 10px;
  background: rgba(0,0,0,0.15);
  border-radius: 6px;
}
.sq-label {
  font-weight: 700;
  font-size: 13px;
  color: #fbbf24;
  min-width: 28px;
}

/* ---------- SUB-QUESTIONS (GENERATED DISPLAY) ---------- */
.gen-sub-questions {
  margin: 12px 0 8px 16px;
  padding-left: 12px;
  border-left: 2px solid rgba(251,191,36,0.3);
}
.gen-sub-question {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  margin-bottom: 10px;
}
.gen-sq-label {
  font-weight: 700;
  font-size: 13px;
  color: #fbbf24;
  min-width: 24px;
  flex-shrink: 0;
  margin-top: 2px;
}
.gen-sq-body {
  flex: 1;
  display: flex;
  align-items: flex-start;
  gap: 8px;
}
.gen-sq-body .gen-q-text {
  flex: 1;
  margin-bottom: 0;
}
.gen-sq-marks {
  font-size: 10px;
  font-weight: 700;
  color: #fbbf24;
  background: rgba(251,191,36,0.12);
  padding: 2px 8px;
  border-radius: 10px;
  border: 1px solid rgba(251,191,36,0.25);
  flex-shrink: 0;
  margin-top: 3px;
}

/* ---------- GENERATED QUESTIONS ---------- */
.generated-card {
  border-color: rgba(52,211,153,0.3);
  background: rgba(16,185,129,0.04);
}
.gen-part {
  margin-bottom: 24px;
}
.gen-part-name {
  font-size: 16px;
  font-weight: 600;
  color: #818cf8;
  margin-bottom: 14px;
  padding-bottom: 8px;
  border-bottom: 1px solid rgba(255,255,255,0.08);
}
.gen-part-instruction {
  font-size: 13px;
  color: #94a3b8;
  font-style: italic;
  margin-bottom: 16px;
}

.gen-question-group {
  margin-bottom: 24px;
  padding: 16px;
  background: rgba(0,0,0,0.2);
  border-radius: 10px;
  border-left: 4px solid #fbbf24;
}
.gen-question-row {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}
.gen-q-num {
  font-weight: 700;
  font-size: 14px;
  color: #fbbf24;
  min-width: 24px;
  flex-shrink: 0;
}
.gen-q-body {
  flex: 1;
}
.gen-q-text {
  font-size: 14px;
  line-height: 1.7;
  color: #e2e8f0;
  margin-bottom: 10px;
}
.gen-q-blooms-inline {
  font-style: italic;
  color: #94a3b8;
}
.gen-question-group {
  margin-bottom: 24px;
}
.gen-or-divider {
  text-align: center;
  font-weight: bold;
  color: #818cf8;
  margin: 12px 0;
}
.gen-q-tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}
.gen-q-footer {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px dashed rgba(255,255,255,0.06);
}
.gen-q-marks-pill {
  font-size: 11px;
  font-weight: 700;
  color: #6ee7b7;
  background: rgba(16,185,129,0.15);
  padding: 4px 10px;
  border-radius: 12px;
  border: 1px solid rgba(52,211,153,0.3);
  margin-left: auto; /* Push marks pill to the exact right edge of the footer */
}
.print-only {
  display: none;
}
.tag {
  display: inline-block;
  padding: 3px 10px;
  border-radius: 14px;
  font-size: 11px;
  font-weight: 600;
}
.tag.bloom {
  background: rgba(96,165,250,0.15);
  color: #93c5fd;
  border: 1px solid rgba(96,165,250,0.3);
}
.tag.classified {
  background: rgba(250,204,21,0.12);
  color: #fde68a;
  border: 1px solid rgba(250,204,21,0.3);
}
.tag.module {
  background: rgba(192,132,252,0.12);
  color: #d8b4fe;
  border: 1px solid rgba(192,132,252,0.3);
}

/* ---------- REGENERATE BUTTON ---------- */
.regen-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 30px;
  height: 30px;
  border-radius: 8px;
  border: 1px solid rgba(129,140,248,0.3);
  background: linear-gradient(135deg, rgba(99,102,241,0.15), rgba(139,92,246,0.15));
  color: #a5b4fc;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.25s ease;
  flex-shrink: 0;
}
.regen-btn:hover:not(:disabled) {
  background: linear-gradient(135deg, rgba(99,102,241,0.35), rgba(139,92,246,0.35));
  border-color: #818cf8;
  transform: scale(1.1);
  box-shadow: 0 0 12px rgba(129,140,248,0.3);
}
.regen-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
.regen-spinning {
  animation: regenSpin 0.8s linear infinite;
}
@keyframes regenSpin {
  from { transform: rotate(0deg); }
  to   { transform: rotate(360deg); }
}

/* Brief flash when a question is regenerated */
.regen-flash {
  animation: regenFlash 0.6s ease-out;
}
@keyframes regenFlash {
  0%   { background: rgba(99,102,241,0.25); }
  100% { background: rgba(0,0,0,0.2); }
}

/* ---------- RESPONSIVE ---------- */
@media (max-width: 640px) {
  .app { padding: 20px 12px 60px; }
  .app-header h1 { font-size: 24px; }
  .stepper { flex-wrap: wrap; gap: 4px; }
  .stepper-line { display: none; }
  .form-row-2, .form-row-3 { grid-template-columns: 1fr; }
  .q-fields { flex-direction: column; }
  .form-group.choice-toggle { align-items: flex-start; }
  .mapping-stats { flex-direction: column; }
  .modules-grid { grid-template-columns: 1fr; }
}

/* ===================================================
   PRINT LAYOUT (Native CSS PDF Export)
   =================================================== */
@media print {
  @page {
    size: A4;
    margin: 20mm;
  }

  /* Reset all background colors to white and text to black to save ink */
  body, .app, .card, .generated-card {
    background: #fff !important;
    color: #000 !important;
    box-shadow: none !important;
    border: none !important;
    padding: 0 !important;
    margin: 0 !important;
    filter: none !important;
    -webkit-print-color-adjust: exact;
  }

  /* Hide everything we don't want on paper */
  .app-header, .stepper, .no-print {
    display: none !important;
  }

  /* Show and style the print wrapper */
  .print-wrapper {
    display: block !important;
    font-family: 'Times New Roman', Times, serif;
    width: 100%;
  }

  /* Show elements that only belong on paper */
  .print-only {
    display: block !important;
  }

  /* Formal Header Styling */
  .print-header {
    text-align: center;
    margin-bottom: 30px;
  }
  .print-header h1 {
    font-size: 20pt;
    font-weight: bold;
    margin-bottom: 8px;
    letter-spacing: 1px;
    text-transform: uppercase;
  }
  .print-divider {
    border: none;
    border-top: 2px solid #000;
    margin: 10px 0;
  }

  /* Part Formatting */
  .gen-part {
    margin-bottom: 40px;
    page-break-inside: avoid;
  }
  .gen-part-name {
    margin-bottom: 5px;
    font-size: 14pt;
    font-weight: bold;
    text-align: center;
    border: none !important;
    padding: 0 !important;
  }
  .gen-part-instruction {
    text-align: center;
    font-size: 11pt;
    font-style: italic;
    margin-bottom: 20px;
  }

  /* Questions List Formal Format */
  .gen-questions-list {
    display: flex;
    flex-direction: column;
    gap: 16px;
  }
  
  .gen-question-row {
    display: flex;
    flex-direction: row;
    align-items: flex-start;
    width: 100%;
    page-break-inside: avoid;
    font-size: 12pt;
    line-height: 1.5;
  }

  .gen-q-num {
    width: 35px;
    flex-shrink: 0;
    font-weight: normal;
    color: #000 !important;
    font-size: 12pt !important;
  }

  .gen-q-body {
    flex-grow: 1;
    padding-right: 20px;
  }

  .gen-q-text {
    margin: 0 !important;
    color: #000 !important;
    font-size: 12pt !important;
  }

  .gen-q-marks {
    width: 70px;
    flex-shrink: 0;
    text-align: right;
    font-weight: bold;
    color: #000 !important;
    background: transparent !important;
    padding: 0 !important;
    border-radius: 0 !important;
    font-size: 12pt !important;
  }

  .gen-q-blooms-inline {
    font-style: italic;
    color: #333 !important;
  }

  .gen-question-group {
    page-break-inside: avoid;
    margin-bottom: 8px;
    border: none !important;
    background: transparent !important;
    padding: 0 !important;
  }

  .gen-or-divider {
    text-align: center;
    font-weight: bold;
    margin: 10px 0;
    font-size: 11pt;
  }

  /* Optional separator between parts */
  .gen-part:not(:last-child)::after {
    content: "";
    display: block;
    width: 40%;
    margin: 30px auto 0;
    border-top: 1px dashed #999;
  }

  .university-paper-format { background: white !important; padding: 20px !important; }

  /* ===================================================
     UNIVERSITY B.TECH PAPER FORMAT (PRINT ONLY)
     =================================================== */

  .university-paper-format {
    font-family: 'Times New Roman', Times, serif;
    color: #000 !important;
    line-height: 1.4;
    text-align: justify;
  }
  .university-paper-format .print-header {
    text-align: center;
    border-bottom: none;
    margin-bottom: 20px;
  }
  .university-paper-format .exam-title {
    font-size: 16pt;
    font-style: italic;
    font-weight: bold;
    margin-bottom: 6px;
    background: transparent !important;
    -webkit-text-fill-color: #000 !important;
  }
  .university-paper-format .course-title {
    font-size: 14pt;
    font-weight: bold;
    margin-bottom: 4px;
  }
  .university-paper-format .scheme-title {
    font-size: 12pt;
    font-style: italic;
    margin-bottom: 12px;
    font-weight: normal;
  }
  .university-paper-format .meta-row {
    display: flex;
    justify-content: space-between;
    font-size: 12pt;
    margin-bottom: 16px;
  }

  /* Course Outcomes */
  .course-outcomes-section {
    text-align: left;
    font-size: 11pt;
    margin-bottom: 24px;
    padding-bottom: 10px;
    border-bottom: 1px solid #000;
  }
  .outcomes-heading {
    font-size: 12pt;
    font-weight: bold;
    text-decoration: underline;
    margin-bottom: 4px;
  }
  .outcomes-sub-heading {
    margin-bottom: 6px;
    font-style: italic;
  }
  .outcomes-list {
    list-style: none;
    padding-left: 10px;
    margin-bottom: 12px;
  }
  .outcomes-list li {
    margin-bottom: 2px;
    font-size: 11pt;
  }
  .outcomes-list li::before {
    content: none !important;
  }
  .blooms-legend, .po-legend {
    margin-top: 4px;
    font-size: 10pt;
  }

  /* Part Table Header (Marks BL CO PO columns) */
  .gen-part-table-header {
    display: flex;
    justify-content: flex-end;
    margin-bottom: 4px;
    padding-right: 0;
  }
  .gen-part-eq {
    font-size: 12pt;
    margin-right: auto;
    padding-left: 40px;
  }
  .gen-part-cols-header {
    display: flex;
    gap: 8px;
    width: 260px;
  }
  .gen-part-cols-header span {
    width: 55px;
    text-align: center;
    font-size: 11pt;
    font-weight: bold;
  }

  /* Per-question meta columns (Marks BL CO PO) */
  .gen-q-meta-cols {
    display: flex !important;
    gap: 8px;
    width: 260px;
    flex-shrink: 0;
  }
  .gen-q-meta-cols span {
    width: 55px;
    text-align: center;
    font-size: 11pt;
  }
  .gen-q-meta-cols.sub-meta {
    margin-left: auto;
  }
  .empty-meta {
    display: none !important;
  }

  /* Question row alignment */
  .university-paper-format .gen-question-row {
    display: flex;
    align-items: flex-start;
    border: none !important;
    background: transparent !important;
  }
  .university-paper-format .gen-q-num {
    font-size: 12pt;
    font-weight: normal;
    color: #000;
    min-width: 35px;
    flex-shrink: 0;
  }
  .university-paper-format .gen-q-text {
    font-size: 12pt;
    color: #000;
  }
  .university-paper-format .gen-q-body {
    flex: 1;
  }
  .university-paper-format .gen-part-name {
    font-size: 14pt;
    text-align: center;
    font-weight: bold;
    color: #000;
  }
  .university-paper-format .gen-part-instruction {
    text-align: center;
    font-size: 11pt;
    font-style: italic;
    margin-bottom: 8px;
    color: #000;
  }
  .university-paper-format .gen-sub-questions {
    border-left: none;
    padding-left: 0;
    margin-left: 0;
  }
  .university-paper-format .gen-sq-label {
    font-size: 12pt;
    font-weight: normal;
    color: #000;
  }

  /* OR divider — plain black, no color */
  .university-paper-format .gen-or-divider {
    text-align: center;
    font-weight: bold;
    margin: 10px 0;
    font-size: 12pt;
    color: #000 !important;
    background: transparent !important;
    border: none !important;
  }
  .university-paper-format .gen-question-or-block {
    background: transparent !important;
    border: none !important;
  }
} /* end @media print */

/* Hide print-only elements on screen by default */
.print-only {
  display: none;
}


```

### `frontend/src/index.js`

```js
import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

```

### `frontend/src/index.css`

```css
/* index.css intentionally minimal — design system is in App.css */

```

### `frontend/src/App.js`

```js
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

```

### `frontend/src/components/TextbookUpload.js`

```js
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

```

### `frontend/src/components/PatternConfig.js`

```js
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

  // --- Generalized Sub-question helpers ---
  const toggleSubQuestions = (pIdx, qIdx, isOr = false) => {
    const p = [...parts];
    const q = p[pIdx].questions[qIdx];
    const target = isOr ? q.or_choice : q;
    const baseMarks = isOr ? q.marks : q.marks; // Marks usually match for OR questions

    if (target.sub_questions && target.sub_questions.length > 0) {
      target.sub_questions = null;
    } else {
      const count = 2;
      const perMark = Math.floor(target.marks / count);
      target.sub_questions = Array.from({ length: count }, (_, i) => ({
        label: String.fromCharCode(97 + i), // a, b, c...
        marks: perMark,
      }));
    }
    setParts(p);
  };

  const addSubQuestion = (pIdx, qIdx, isOr = false) => {
    const p = [...parts];
    const q = p[pIdx].questions[qIdx];
    const target = isOr ? q.or_choice : q;
    
    const nextLabel = String.fromCharCode(97 + (target.sub_questions?.length || 0));
    const allocated = (target.sub_questions || []).reduce((s, sq) => s + sq.marks, 0);
    const remainingMarks = target.marks - allocated;
    
    target.sub_questions = [...(target.sub_questions || []), { label: nextLabel, marks: Math.max(1, remainingMarks) }];
    setParts(p);
  };

  const removeSubQuestion = (pIdx, qIdx, sqIdx, isOr = false) => {
    const p = [...parts];
    const q = p[pIdx].questions[qIdx];
    const target = isOr ? q.or_choice : q;
    
    target.sub_questions = target.sub_questions
      .filter((_, i) => i !== sqIdx)
      .map((sq, i) => ({ ...sq, label: String.fromCharCode(97 + i) }));
    if (target.sub_questions.length === 0) target.sub_questions = null;
    setParts(p);
  };

  const updateSubQuestion = (pIdx, qIdx, sqIdx, field, value, isOr = false) => {
    const p = [...parts];
    const q = p[pIdx].questions[qIdx];
    const target = isOr ? q.or_choice : q;
    target.sub_questions[sqIdx][field] = value;
    setParts(p);
  };

  const totalQ = parts.reduce((s, p) => s + (p.questions?.length || 0), 0);
  const totalM = parts.reduce((s, p) => s + (p.questions?.reduce((a, q) => a + (q.marks || 0), 0) || 0), 0);

  // Sub-question config sub-panel component for reusability
  const SubQuestionsConfig = ({ pIdx, qIdx, subQuestions, totalMarks, isOr = false }) => {
    if (!subQuestions || subQuestions.length === 0) return null;
    const allocatedMarks = subQuestions.reduce((s, sq) => s + sq.marks, 0);
    const isError = allocatedMarks !== totalMarks;

    return (
      <div className={`sub-questions-panel ${isOr ? 'or-sub-panel' : ''}`}>
        <div className="sub-questions-header">
          <span className="sub-questions-title">📋 {isOr ? 'OR ' : ''}Sub-Questions</span>
          <span className={`sub-questions-summary ${isError ? 'error-text' : ''}`}>
            {subQuestions.length} parts • {allocatedMarks}/{totalMarks} marks {isError ? '⚠️' : '✅'}
          </span>
        </div>
        {subQuestions.map((sq, sqIdx) => (
          <div key={sqIdx} className="sub-question-row">
            <span className="sq-label">({sq.label})</span>
            <div className="form-group mini">
              <label>Marks</label>
              <input
                type="number" min="1"
                value={sq.marks}
                onChange={e => updateSubQuestion(pIdx, qIdx, sqIdx, "marks", parseInt(e.target.value), isOr)}
              />
            </div>
            {subQuestions.length > 1 && (
              <button className="btn-sm orange" onClick={() => removeSubQuestion(pIdx, qIdx, sqIdx, isOr)} style={{padding: "3px 8px", fontSize: "10px"}}>✕</button>
            )}
          </div>
        ))}
        <button className="btn-sm green" onClick={() => addSubQuestion(pIdx, qIdx, isOr)} style={{marginTop: "6px", fontSize: "11px", padding: "4px 10px"}}>+ Add Sub-Q</button>
      </div>
    );
  };

  return (
    <section className="card pattern-config-card">
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
              <div className="part-body">
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
                      <div className={`question-setup-block ${q.has_internal_choice ? 'has-choice' : ''}`}>
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
                                    if (checked && !q.or_choice) {
                                      updateQuestion(pIdx, qIdx, "or_choice", { marks: q.marks, module: q.module, sub_questions: null });
                                    }
                                    updateQuestion(pIdx, qIdx, "has_internal_choice", checked);
                                  }}
                                />
                                <span className="switch-slider"></span>
                              </label>
                            </div>
                            {/* Main Sub-questions toggle for marks >= 12 */}
                            {q.marks >= 12 && (
                              <div className="form-group mini choice-toggle">
                                <label>Sub-Qs</label>
                                <label className="switch">
                                  <input
                                    type="checkbox"
                                    checked={!!(q.sub_questions && q.sub_questions.length > 0)}
                                    onChange={() => toggleSubQuestions(pIdx, qIdx, false)}
                                  />
                                  <span className="switch-slider"></span>
                                </label>
                              </div>
                            )}
                          </div>
                          {part.questions.length > 1 && (
                            <button className="btn-sm orange" onClick={() => removeQ(pIdx, qIdx)}>✕</button>
                          )}
                        </div>

                        {/* Config for main question sub-parts */}
                        {q.sub_questions && q.sub_questions.length > 0 && (
                          <SubQuestionsConfig 
                            pIdx={pIdx} qIdx={qIdx} 
                            subQuestions={q.sub_questions} 
                            totalMarks={q.marks} 
                            isOr={false} 
                          />
                        )}

                        {/* Internal Choice (OR) Panel */}
                        {q.has_internal_choice && (
                          <div className="or-choice-panel">
                            <div className="or-choice-fields">
                              <div className="or-header-row">
                                <div className="or-choice-indicator">↳</div>
                                <span className="or-choice-label">Alternative (OR Choice)</span>
                              </div>
                              <div className="or-fields-row">
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
                                {((q.or_choice?.marks || q.marks) >= 12) && (
                                  <div className="form-group mini choice-toggle">
                                    <label>Sub-Qs</label>
                                    <label className="switch">
                                      <input
                                        type="checkbox"
                                        checked={!!(q.or_choice?.sub_questions && q.or_choice.sub_questions.length > 0)}
                                        onChange={() => toggleSubQuestions(pIdx, qIdx, true)}
                                      />
                                      <span className="switch-slider"></span>
                                    </label>
                                  </div>
                                )}
                              </div>
                            </div>
                            
                            {/* Config for OR question sub-parts */}
                            {q.or_choice?.sub_questions && q.or_choice.sub_questions.length > 0 && (
                              <SubQuestionsConfig 
                                pIdx={pIdx} qIdx={qIdx} 
                                subQuestions={q.or_choice.sub_questions} 
                                totalMarks={q.or_choice.marks} 
                                isOr={true} 
                              />
                            )}
                          </div>
                        )}
                      </div>
                    </React.Fragment>
                  ))}
                  <button className="btn-sm green full-width" onClick={() => addQ(pIdx)}>+ Add Question</button>
                </div>
              </div>
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

```

### `frontend/src/components/SemanticMapping.js`

```js
import React, { useState } from "react";

const API_BASE_URL = process.env.REACT_APP_API_URL || "http://127.0.0.1:8000";

export default function SemanticMapping({ selectedTopics, onNext }) {
  const [loading, setLoading] = useState(false);
  const [mapping, setMapping] = useState(null);
  const [error, setError] = useState(null);
  const [expandedModules, setExpandedModules] = useState([]);

  const toggleModule = (modName) => {
    setExpandedModules((prev) =>
      prev.includes(modName)
        ? prev.filter((m) => m !== modName)
        : [...prev, modName]
    );
  };

  const runMapping = async () => {
    setLoading(true);
    setError(null);

    try {
      const payload = Object.keys(selectedTopics || {}).length > 0 
        ? { selected_modules: selectedTopics } 
        : {};

      const response = await fetch(`${API_BASE_URL}/semantic-mapping`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await response.json();

      if (data.error) {
        setError(data.error);
      } else {
        setMapping(data.mapping || {});
      }
    } catch (err) {
      setError("Failed to connect to backend: " + err.message);
    }

    setLoading(false);
  };

  // Module-based mapping: each key is a module name,
  // value has { topics, raw_text, embedding_ready_text, chunks }
  const moduleCount = mapping ? Object.keys(mapping).length : 0;
  
  const totalChunks = mapping
    ? Object.values(mapping).reduce((sum, mod) => {
        // Handle new nested topic_mappings structure
        if (mod.topic_mappings) {
          const chunkSet = new Set();
          Object.values(mod.topic_mappings).forEach((chunksList) => {
            if (Array.isArray(chunksList)) {
              chunksList.forEach(c => chunkSet.add(c.chunk_id));
            }
          });
          return sum + chunkSet.size;
        }
        // Fallback for legacy format
        const chunks = mod.chunks || mod;
        return sum + (Array.isArray(chunks) ? chunks.length : 0);
      }, 0)
    : 0;

  const totalTopics = mapping
    ? Object.values(mapping).reduce((sum, mod) => {
        const topics = mod.topics || [];
        return sum + topics.length;
      }, 0)
    : 0;

  return (
    <section className="card">
      <h2 className="card-title">
        <span className="card-icon">🔗</span> Semantic Module–Chunk Mapping
      </h2>
      <p className="card-desc">
        Uses the fine-tuned <strong>SBERT model</strong> to semantically map
        syllabus modules to the most relevant textbook chunks.
      </p>

      <button
        className="btn indigo"
        onClick={runMapping}
        disabled={loading}
      >
        {loading ? "Running SBERT Mapping…" : "Run Semantic Mapping"}
      </button>

      {error && <div className="error-box">{error}</div>}

      {mapping && (
        <>
          <div className="mapping-stats">
            <div className="stat-pill">
              <span className="stat-value">{moduleCount}</span>
              <span className="stat-label">modules mapped</span>
            </div>
            <div className="stat-pill">
              <span className="stat-value">{totalTopics}</span>
              <span className="stat-label">topics covered</span>
            </div>
            <div className="stat-pill">
              <span className="stat-value">{totalChunks}</span>
              <span className="stat-label">chunks linked</span>
            </div>
          </div>

          <div className="mapping-results">
            {Object.entries(mapping).map(([moduleName, moduleData]) => {
              // Extract unique chunks from nested topic_mappings
              let extractedChunks = [];
              if (moduleData.topic_mappings) {
                const uniqueChunksMap = new Map();
                for (const chunkList of Object.values(moduleData.topic_mappings)) {
                  if (Array.isArray(chunkList)) {
                    for (const chunk of chunkList) {
                      if (!uniqueChunksMap.has(chunk.chunk_id) || chunk.score > uniqueChunksMap.get(chunk.chunk_id).score) {
                        uniqueChunksMap.set(chunk.chunk_id, chunk);
                      }
                    }
                  }
                }
                extractedChunks = Array.from(uniqueChunksMap.values());
              } else {
                extractedChunks = moduleData.chunks || [];
              }
              
              const isExpanded = expandedModules.includes(moduleName);
              const topics = moduleData.topics || [];
              const visibleTopics = isExpanded ? topics : topics.slice(0, 5);
              
              // Only show top 8 chunks initially, or all if expanded
              const sortedChunks = extractedChunks.sort((a,b) => b.score - a.score);
              const visibleChunks = isExpanded ? sortedChunks : sortedChunks.slice(0, 8);

              return (
                <div key={moduleName} className="mapping-item">
                  <div className="mapping-topic">{moduleName}</div>
                  {topics.length > 0 && (
                    <div className="mapping-topic-list">
                      {visibleTopics.map((t, i) => (
                        <span key={i} className="topic-tag">{t}</span>
                      ))}
                      {topics.length > 5 && (
                        <button
                          className="topic-tag dim"
                          onClick={() => toggleModule(moduleName)}
                          style={{ cursor: "pointer", background: "none", border: "none" }}
                        >
                          {isExpanded ? "↑ Show less" : `+${topics.length - 5} more (Click to Expand)`}
                        </button>
                      )}
                    </div>
                  )}
                  <div className="mapping-chunks">
                    {visibleChunks.map((chunk, idx) => (
                      <span key={idx} className="chunk-tag">
                        Chunk #{chunk.chunk_id}{" "}
                        <small>({(chunk.score * 100).toFixed(0)}%)</small>
                      </span>
                    ))}
                    {!isExpanded && sortedChunks.length > 8 && (
                      <span className="chunk-tag dim">+{sortedChunks.length - 8} more...</span>
                    )}
                  </div>
                </div>
              );
            })}
          </div>

          <button className="btn green next-btn" onClick={onNext}>
            Continue to Pattern Configuration →
          </button>
        </>
      )}
    </section>
  );
}

```

### `frontend/src/components/TopicSelection.js`

```js
import React, { useState, useEffect } from "react";

export default function TopicSelection({ topics, selectedTopics, setSelectedTopics, onNext }) {
  const [isAutomatic, setIsAutomatic] = useState(true);

  // Initialize selectedTopics if empty and we switch out of automatic
  useEffect(() => {
    if (!isAutomatic && Object.keys(selectedTopics).length === 0 && topics?.modules) {
      const initialSelection = {};
      Object.entries(topics.modules).forEach(([modName, modData]) => {
        initialSelection[modName] = Array.isArray(modData) ? [...modData] : [...(modData.topics || [])];
      });
      setSelectedTopics(initialSelection);
    }
  }, [isAutomatic, selectedTopics, setSelectedTopics, topics]);

  if (!topics || !topics.modules) {
    return (
      <section className="card">
        <h2 className="card-title">
          <span className="card-icon">🎯</span> Select Topics
        </h2>
        <p>No syllabus topics found. Please upload a syllabus first.</p>
      </section>
    );
  }

  const handleTopicToggle = (modName, topicList, topic, isChecked) => {
    setSelectedTopics((prev) => {
      const updatedMod = prev[modName] ? [...prev[modName]] : [...topicList];
      if (isChecked) {
        if (!updatedMod.includes(topic)) updatedMod.push(topic);
      } else {
        const index = updatedMod.indexOf(topic);
        if (index > -1) updatedMod.splice(index, 1);
      }
      return { ...prev, [modName]: updatedMod };
    });
  };

  const handleSelectAll = (modName, topicList, selectAll) => {
    setSelectedTopics((prev) => ({
      ...prev,
      [modName]: selectAll ? [...topicList] : [],
    }));
  };

  return (
    <section className="card">
      <h2 className="card-title">
        <span className="card-icon">🎯</span> Select Examination Topics
      </h2>
      <p className="card-desc">
        Choose specific topics to limit the scope of the generated questions.
        Or leave it on "Automatic" to use the entire syllabus.
      </p>

      <div className="page-toggle-row">
        <label className="switch">
          <input
            type="checkbox"
            checked={isAutomatic}
            onChange={(e) => {
              setIsAutomatic(e.target.checked);
              if (e.target.checked) setSelectedTopics({}); // Clear selections to signal full automatic to backend
            }}
          />
          <span className="switch-slider"></span>
        </label>
        <span className="page-toggle-label">
          {isAutomatic ? "Automatic (Process entire syllabus)" : "Custom Topic Selection"}
        </span>
      </div>

      {!isAutomatic && (
        <div className="topic-selection-grid">
          {Object.entries(topics.modules).map(([modName, modData]) => {
            const topicList = Array.isArray(modData) ? modData : (modData.topics || []);
            const currentlySelected = selectedTopics[modName] || [];
            const isAllSelected = currentlySelected.length === topicList.length;

            return (
              <div key={modName} className="module-card topic-picker-card">
                <div className="module-header-flex">
                  <span className="module-badge">{modName}</span>
                  <label className="select-all-label">
                    <input
                      type="checkbox"
                      checked={isAllSelected}
                      onChange={(e) => handleSelectAll(modName, topicList, e.target.checked)}
                    />
                    Select All
                  </label>
                </div>
                
                <ul className="topic-list interactive-topic-list">
                  {topicList.map((t, i) => {
                    const isChecked = selectedTopics[modName]?.includes(t) ?? true;
                    return (
                      <li key={i}>
                        <label className="topic-checkbox-label">
                          <input
                            type="checkbox"
                            checked={isChecked}
                            onChange={(e) => handleTopicToggle(modName, topicList, t, e.target.checked)}
                          />
                          <span className="topic-text">{t}</span>
                        </label>
                      </li>
                    );
                  })}
                </ul>
              </div>
            );
          })}
        </div>
      )}

      <button className="btn green next-btn" onClick={onNext} style={{ marginTop: "20px" }}>
        Continue to Semantic Mapping →
      </button>
    </section>
  );
}

```

### `frontend/src/components/Stepper.js`

```js
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

```

### `frontend/src/components/SyllabusUpload.js`

```js
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

```

### `frontend/src/components/GeneratedQuestions.js`

```js
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

```

## Backend Code

---

### `backend/app/factory.py`

```py
"""
FastAPI Application Factory.

Creates and configures the FastAPI app instance with
all middleware and routers registered.
"""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import CORS_ORIGINS
from app.api import syllabus, textbook, mapping, questions

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.

    Returns:
        Configured FastAPI app instance with all routers registered.
    """
    app = FastAPI(
        title="Question Paper Generation System",
        description=(
            "An intelligent NLP-based platform for automated "
            "question paper generation using SBERT, Flan-T5, "
            "and Bloom's taxonomy classification."
        ),
        version="1.0.0",
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register API routers
    app.include_router(syllabus.router)
    app.include_router(textbook.router)
    app.include_router(mapping.router)
    app.include_router(questions.router)

    # Health check route
    @app.get("/")
    def root():
        return {"status": "Backend running successfully"}

    return app

```

### `backend/app/core/config.py`

```py
"""
Centralized configuration for the backend application.
All paths, model names, and constants are defined here.
"""

import os
from pathlib import Path


# --------------------------------------------------
# DIRECTORY PATHS
# --------------------------------------------------

# Root of the entire project (parent of backend/)
PROJECT_ROOT = Path(__file__).resolve().parents[3]

# Backend root
BACKEND_ROOT = Path(__file__).resolve().parents[2]

# Runtime output directory (moved to PROJECT_ROOT to avoid uvicorn --reload loops)
PROCESSED_DATA_DIR = PROJECT_ROOT / "processed_data"
PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

# --------------------------------------------------
# MODEL PATHS
# --------------------------------------------------

SBERT_MODEL_PATH = str(PROJECT_ROOT / "models" / "sbert_custom_model")
FLAN_T5_MODEL_PATH = str(PROJECT_ROOT / "models" / "flan t5 large final")

# Fallback model names (downloaded from HuggingFace if local not found)
SBERT_FALLBACK_MODEL = "all-MiniLM-L6-v2"
FLAN_T5_FALLBACK_MODEL = "google/flan-t5-small"

# Semantic Syllabus Extractor (Local Mistral via Ollama)
OLLAMA_BASE_URL = "http://localhost:11434"
LLM_MODEL = "mistral"


# --------------------------------------------------
# SBERT MAPPING SETTINGS
# --------------------------------------------------

SIMILARITY_THRESHOLD = 0.45
DIVERSITY_THRESHOLD = 0.85
MAX_CHUNKS_PER_TOPIC = 6

# --------------------------------------------------
# CHUNKING SETTINGS (character-based for RecursiveCharacterTextSplitter)
# --------------------------------------------------

CHUNK_SIZE_CHARS = 2000
CHUNK_OVERLAP_CHARS = 300
MIN_CHUNK_LENGTH = 300

# --------------------------------------------------
# CORS SETTINGS
# --------------------------------------------------

CORS_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
]

# --------------------------------------------------
# TESSERACT / POPPLER (platform-aware)
# --------------------------------------------------

import platform

if platform.system() == "Windows":
    TESSERACT_CMD = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    POPPLER_PATH = r"C:\poppler\Library\bin"
else:
    # On macOS/Linux, assume installed via brew/apt and available on PATH
    TESSERACT_CMD = "tesseract"
    POPPLER_PATH = None

```

### `backend/app/utils/image_utils.py`

```py
"""
Utility functions for image extraction from PDFs and
mapping images to text chunks by page number.
"""

import os
import fitz  # PyMuPDF
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


def extract_images_from_pdf(
    pdf_bytes: bytes, output_dir: str
) -> List[Dict[str, Any]]:
    """
    Extract all images from a PDF and save them to the output directory.

    Args:
        pdf_bytes: Raw bytes of the PDF file.
        output_dir: Directory to save extracted images.

    Returns:
        List of image metadata dicts with keys: image_id, page, path.
    """
    os.makedirs(output_dir, exist_ok=True)

    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    images_metadata = []

    for page_index, page in enumerate(doc, start=1):
        images = page.get_images(full=True)

        for img_index, img in enumerate(images):
            xref = img[0]
            try:
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]

                image_name = f"page_{page_index}_img_{img_index + 1}.{image_ext}"
                image_path = os.path.join(output_dir, image_name)

                with open(image_path, "wb") as f:
                    f.write(image_bytes)

                images_metadata.append({
                    "image_id": image_name,
                    "page": page_index,
                    "path": image_path,
                })
            except Exception as e:
                logger.warning(
                    f"Failed to extract image {img_index} from page {page_index}: {e}"
                )

    logger.info(f"Extracted {len(images_metadata)} images from PDF")
    return images_metadata


def map_chunks_to_images(
    chunks: List[Dict[str, Any]], images: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Associate images with text chunks based on matching page numbers.

    Args:
        chunks: List of chunk dicts (must have 'page' key).
        images: List of image metadata dicts (must have 'page' key).

    Returns:
        The chunks list with an added 'images' key on each chunk.
    """
    image_map: Dict[int, List[Dict[str, Any]]] = {}
    for img in images:
        image_map.setdefault(img["page"], []).append(img)

    for chunk in chunks:
        chunk["images"] = image_map.get(chunk["page"], [])

    return chunks

```

### `backend/app/utils/ollama_client.py`

```py
"""
Ollama API client — standalone HTTP caller for local LLM inference.

Extracted from question_service.py to isolate network I/O from business logic.
"""

import json
import re
import logging
import urllib.request
import urllib.error

logger = logging.getLogger(__name__)

OLLAMA_GENERATE_URL = "http://localhost:11434/api/generate"


def ollama_generate(
    prompt: str,
    options: dict,
    timeout_s: int = 60,
    model: str = "mistral",
) -> str:
    """Send a prompt to the local Ollama server and return the raw response text."""
    data = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": options,
    }

    req = urllib.request.Request(
        OLLAMA_GENERATE_URL,
        data=json.dumps(data).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=timeout_s) as response:
        result_data = json.loads(response.read().decode("utf-8"))
        return result_data.get("response", "")


def extract_generated_question(full_output: str) -> str:
    """Strip the prompt echo from Mistral output.
    Handles both [INST]...[/INST] format and Alpaca ### Response: format.
    """
    # Alpaca format: the response comes after ### Response:
    if "### Response:" in full_output:
        return full_output.split("### Response:")[-1].strip()
    # Legacy [INST] format
    if "[/INST]" in full_output:
        return full_output.split("[/INST]")[-1].strip()
    return full_output.strip()


def refine_with_ollama(question: str, marks: int, topic: str = "", extract_topic_tokens_fn=None) -> str:
    """
    Send the generated question to the local Ollama mistral model to polish it into
    a strict, mark-aware university exam format. The original topic name is provided
    so Mistral can correct any garbled proper nouns from T5.
    """
    try:
        # Topic anchoring instruction
        topic_anchor = ""
        if topic:
            topic_anchor = (
                f"\nIMPORTANT: The correct topic name is '{topic}'. "
                f"If the draft contains a misspelling or garbled version of this topic name, "
                f"fix it to use exactly '{topic}'.\n"
            )

        if marks <= 3:
            style_guide = (
                "Keep the question very short, direct, and specific to the draft topic. "
                "Preserve the technical scope of the draft instead of broadening it into a generic theory question. "
                "Prefer one focused ask. Avoid filler phrases such as 'importance', 'real-world applications', "
                "'where appropriate', or 'with suitable examples' unless the draft already requires them."
            )
        else:
            style_guide = (
                "Make the question sound like it was written naturally by a human professor while keeping the exact "
                "technical focus of the draft. Vary sentence structure without changing the core concept being tested. "
                "Avoid generic expansions such as applications, advantages, limitations, or examples unless they are "
                "already implied by the draft. Use plain academic English and keep the question focused."
            )

        prompt = (
            f"You are an engineering professor finalizing an exam. Rewrite the following draft question into a natural, human-sounding exam question for a {marks}-mark allocation.\n\n"
            f"{topic_anchor}"
            f"STYLE RULES:\n"
            f"{style_guide}\n\n"
            f"Preserve technical terms from the draft. Do not introduce concepts from unrelated subjects.\n"
            f"DO NOT include any introductory text, conversational parts, or meta-commentary like 'Here is the question'. "
            f"Output ONLY the refined question text.\n\n"
            f"Draft: {question}\n\nFinal Question:"
        )

        data = {
            "model": "mistral",
            "prompt": prompt,
            "system": "You are a human engineering professor writing varied, practical exam questions. You avoid repetitive, robotic templates and never use flowery vocabulary.",
            "stream": False,
            "options": {
                "temperature": 0.45
            }
        }

        req = urllib.request.Request(
            OLLAMA_GENERATE_URL, data=json.dumps(data).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )

        # Using 60s timeout to accommodate longer inference on lower-spec hardware
        with urllib.request.urlopen(req, timeout=60) as response:
            result_data = json.loads(response.read().decode("utf-8"))
            refined = result_data.get("response", "").strip()
            # Clean up occasional hallucinated prefixes from Mistral
            refined = re.sub(r"^(Question|Output|Refined Question|Draft Question|Final Question)[\s]*:[\s]*", "", refined, flags=re.IGNORECASE).strip()
            # Strip wrapping quotes that Mistral occasionally adds
            refined = refined.strip('"').strip("'")
            refined = re.sub(r"\s+", " ", refined).strip()
            if "?" in refined:
                refined = refined[: refined.index("?") + 1].strip()
            if refined and not refined.endswith("?"):
                refined = refined.rstrip(".") + "?"
            if topic and extract_topic_tokens_fn:
                topic_tokens = extract_topic_tokens_fn(topic)
                refined_lower = refined.lower()
                if topic_tokens and not any(token in refined_lower for token in topic_tokens):
                    return question
            if refined:
                logger.info(f"\n[Mistral] Original: {question}\n[Mistral] Refined : {refined}\n")
                return refined
    except urllib.error.URLError as e:
        logger.warning(f"Ollama refinement failed (is Ollama running?): {e}")
    except Exception as e:
        logger.error(f"Unexpected error during Ollama refinement: {e}")

    # Fall back to the original question if Ollama fails
    return question

```

### `backend/app/utils/pdf_utils.py`

```py
"""
Utility functions for PDF reading and text extraction.
Shared by ingestion and syllabus services.
"""

import fitz  # PyMuPDF
import logging
from typing import List, Tuple

logger = logging.getLogger(__name__)


def extract_full_text(pdf_bytes: bytes) -> str:
    """
    Extract all text from a PDF using PyMuPDF.

    Args:
        pdf_bytes: Raw bytes of the PDF file.

    Returns:
        Concatenated text from all pages.
    """
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text("text") + "\n"
    return text


def extract_text_by_page(pdf_bytes: bytes) -> List[Tuple[int, str]]:
    """
    Extract text from a PDF page-by-page with page number metadata.

    Args:
        pdf_bytes: Raw bytes of the PDF file.

    Returns:
        List of (page_number, page_text) tuples.
    """
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    pages_text = []
    for page_number, page in enumerate(doc, start=1):
        text = page.get_text("text")
        pages_text.append((page_number, text))
    return pages_text


def is_valid_extracted_text(text: str) -> bool:
    """
    Detect and reject fake/hidden text layers commonly found in scanned textbooks.

    Args:
        text: Extracted text to validate.

    Returns:
        True if the text appears to be genuine content.
    """
    if not text or len(text.strip()) < 300:
        return False

    lower_text = text.lower()

    garbage_patterns = [
        "hidden page",
        "this page intentionally left blank",
        "digitized by",
        "scanned by",
        "copyright",
    ]

    for pattern in garbage_patterns:
        if lower_text.count(pattern) > 3:
            return False

    words = text.split()
    unique_words = set(words)
    diversity_ratio = len(unique_words) / max(len(words), 1)

    if diversity_ratio < 0.25:
        return False

    return True

```

### `backend/app/utils/context_utils.py`

```py
"""
Context compression, module normalisation, and topic-token extraction helpers.

Extracted from question_service.py to keep the service file focused on orchestration.
"""

import re
import logging
from typing import List, Dict, Optional

from app.utils.question_constants import CONTEXT_STOPWORDS

logger = logging.getLogger(__name__)


# =====================================================
# Module Name Normalisation
# =====================================================

def normalize_module_name(name: str) -> str:
    """
    Normalize a module name so that both Arabic and Roman numeral
    variants map to the same canonical form.
    e.g. "Module 1" -> "module_1", "Module I" -> "module_1",
         "Module IV" -> "module_4", "Module 4" -> "module_4"
    """
    roman_to_arabic = {
        "i": "1", "ii": "2", "iii": "3", "iv": "4",
        "v": "5", "vi": "6", "vii": "7", "viii": "8",
    }
    text = name.strip().lower()
    # Try to extract "module <token>" pattern
    m = re.match(r"^module\s+(.+)$", text)
    if m:
        token = m.group(1).strip()
        # If the token is a Roman numeral, convert it
        if token in roman_to_arabic:
            return f"module_{roman_to_arabic[token]}"
        # If it's already an Arabic numeral, use it
        if token.isdigit():
            return f"module_{token}"
        # Otherwise, return a cleaned version
        return f"module_{token}"
    return text.replace(" ", "_")


def find_matching_key(module: str, keys) -> Optional[str]:
    """Find the dictionary key that matches the given module name exactly
    after normalization. Returns the original key or None."""
    norm = normalize_module_name(module)
    for key in keys:
        if normalize_module_name(key) == norm:
            return key
    return None


# =====================================================
# Subject & Topic Helpers
# =====================================================

def normalize_subject_name(subject: Optional[str]) -> str:
    normalized = re.sub(r"[^a-z0-9]+", " ", (subject or "").strip().lower())
    return " ".join(normalized.split())


def mark_bucket(marks: Optional[int]) -> str:
    if marks is None:
        return "unknown"
    if marks <= 5:
        return "short"
    if marks <= 8:
        return "medium"
    return "long"


def extract_topic_tokens(topic: str) -> List[str]:
    tokens = re.findall(r"[a-z0-9]+", (topic or "").lower())
    return [
        token for token in tokens
        if len(token) > 2 and token not in CONTEXT_STOPWORDS
    ]


# =====================================================
# Context Compression (SBERT + BM25)
# =====================================================

def compress_context(
    chunks: List[str],
    topic: str,
    max_tokens: int = 400,
    sbert_model=None,
) -> str:
    """
    Re-rank input chunks by combined SBERT + BM25 relevance, then extract highest-scoring
    sentences within a token budget.
    """
    if not chunks:
        return ""

    if sbert_model is None:
        return " ".join(chunks)[:max_tokens * 5]  # rough fallback

    from sentence_transformers import util

    # nltk sent_tokenize
    try:
        from nltk.tokenize import sent_tokenize
    except Exception:
        sent_tokenize = None

    tokenized_chunks = [c.lower().split() for c in chunks]
    bm25_scores = None
    try:
        from rank_bm25 import BM25Okapi

        bm25 = BM25Okapi(tokenized_chunks)
        bm25_scores = bm25.get_scores(topic.lower().split())
    except Exception:
        # If rank_bm25 is missing, degrade to SBERT-only scoring.
        bm25_scores = [0.0 for _ in chunks]

    topic_vec = sbert_model.encode(topic, convert_to_tensor=True)
    chunk_vecs = sbert_model.encode(chunks, convert_to_tensor=True)
    sbert_scores = util.cos_sim(topic_vec, chunk_vecs)[0].cpu().numpy()

    scored = [
        (float(sbert_scores[i]) * 0.6 + float(bm25_scores[i]) * 0.4, chunks[i])
        for i in range(len(chunks))
    ]
    scored.sort(reverse=True, key=lambda x: x[0])

    selected_sentences: List[str] = []
    budget = 0
    for _, chunk in scored:
        if sent_tokenize is not None:
            try:
                sents = sent_tokenize(chunk)
            except Exception:
                sents = [
                    s.strip()
                    for s in re.split(r"(?<=[.!?])\s+", chunk.strip())
                    if s.strip()
                ]
        else:
            sents = [
                s.strip()
                for s in re.split(r"(?<=[.!?])\s+", chunk.strip())
                if s.strip()
            ]

        for sent in sents:
            tok_count = len(sent.split())
            if budget + tok_count <= max_tokens:
                selected_sentences.append(sent)
                budget += tok_count

    return " ".join(selected_sentences)


# =====================================================
# Chunk Retrieval
# =====================================================

def get_relevant_chunks(
    module: str, topic: str, topic_mapping: Dict, chunks_dict: Dict[int, str]
) -> Optional[str]:
    """Retrieve only the highest-scoring chunks mapped to the requested topic."""
    relevant_chunk_ids = []

    # First, try exact normalized matching (handles Roman <-> Arabic)
    matched_key = find_matching_key(module, topic_mapping.keys())

    if matched_key:
        value = topic_mapping[matched_key]

        # 1. NEW LOGIC: Granular topic-level chunks
        if isinstance(value, dict) and "topic_mappings" in value and topic in value["topic_mappings"]:
            sorted_topic_chunks = sorted(
                value["topic_mappings"][topic],
                key=lambda item: float(item.get("score", 0.0)),
                reverse=True,
            )
            for chunk_info in sorted_topic_chunks[:3]:
                chunk_id = chunk_info.get("chunk_id")
                if chunk_id in chunks_dict and chunk_id not in relevant_chunk_ids:
                    relevant_chunk_ids.append(chunk_id)

        # 2. LEGACY LOGIC: Module-level average chunks (fallback for unstructured JSONs)
        elif isinstance(value, dict) and "chunks" in value:
            for chunk_info in value["chunks"][:3]:
                chunk_id = chunk_info.get("chunk_id")
                if chunk_id in chunks_dict and chunk_id not in relevant_chunk_ids:
                    relevant_chunk_ids.append(chunk_id)

        # 3. LEGACY LOGIC: List of chunks directly
        elif isinstance(value, list):
            for chunk_info in value[:3]:
                chunk_id = (
                    chunk_info
                    if isinstance(chunk_info, int)
                    else chunk_info.get("chunk_id")
                )
                if chunk_id in chunks_dict and chunk_id not in relevant_chunk_ids:
                    relevant_chunk_ids.append(chunk_id)
    else:
        logger.warning(
            f"No matching module found for '{module}' in topic_mapping keys: "
            f"{list(topic_mapping.keys())}"
        )

    if not relevant_chunk_ids:
        return None

    # Preserve the score-ranked insertion order from the selection logic above.
    parts = [chunks_dict[cid] for cid in relevant_chunk_ids if cid in chunks_dict]

    context = " ".join(parts)
    logger.debug(
        f"[Context Window] topic '{topic}': "
        f"stitched {len(parts)} mapped chunks ({len(context)} chars)"
    )
    return context

```

### `backend/app/utils/question_constants.py`

```py
"""
Question generation constants — Bloom's taxonomy verbs, stopwords, valid openers,
and the Ollama scaffold template.

Extracted from question_service.py to keep the service file focused on orchestration.
"""

# =====================================================
# Bloom's Taxonomy Verb Map (Step 4 from upgrade plan)
# =====================================================
BLOOM_VERBS = {
    "Remember": ["define", "list", "identify"],
    "Understand": ["explain", "summarize"],
    "Apply": ["solve", "demonstrate"],
    "Analyze": ["compare", "differentiate"],
    "Evaluate": ["justify", "critique"],
    "Create": ["design", "formulate"],
}

GENERIC_SUBJECT_NAMES = {"", "unknown", "computer science"}

CONTEXT_STOPWORDS = {
    "about", "after", "again", "against", "algorithm", "algorithms", "also", "among",
    "and", "another", "apply", "approach", "approaches", "architecture", "because",
    "before", "between", "both", "can", "concept", "concepts", "consider", "course",
    "data", "define", "describe", "design", "detail", "different", "discuss", "each",
    "effect", "effects", "example", "examples", "explain", "feature", "features",
    "following", "from", "function", "functions", "how", "important", "importance",
    "include", "including", "into", "level", "marks", "module", "more", "most",
    "nature", "operating", "operation", "operations", "provide", "question", "real",
    "related", "role", "state", "system", "systems", "their", "these", "this",
    "through", "topic", "used", "using", "what", "when", "where", "which", "with",
}

VALID_OPENERS = {
    # Bloom's L1 – Remember
    "define", "state", "list", "name", "identify", "recall",
    "recognise", "recognize", "label", "select", "match",
    "outline", "enumerate", "mention", "specify", "reproduce",
    # Bloom's L2 – Understand
    "explain", "describe", "discuss", "summarise", "summarize",
    "interpret", "classify", "distinguish", "paraphrase",
    "illustrate", "clarify", "elaborate", "give", "provide",
    "differentiate", "justify", "represent", "translate",
    # Bloom's L3 – Apply
    "apply", "calculate", "compute", "solve", "determine",
    "find", "derive", "show", "demonstrate", "use",
    "implement", "execute", "construct", "sketch", "draw",
    "plot", "trace", "build", "develop", "formulate",
    "write", "obtain", "verify", "prove", "establish",
    # Bloom's L4 – Analyze
    "analyze", "analyse", "compare", "contrast", "examine",
    "inspect", "investigate", "differentiate", "distinguish",
    "separate", "categorize", "categorise", "deconstruct",
    "deduce", "infer", "relate", "correlate", "break",
    # Bloom's L5 – Evaluate
    "evaluate", "assess", "justify", "judge", "critique",
    "criticise", "criticize", "appraise", "argue", "defend",
    "support", "recommend", "prioritize", "prioritise", "rank",
    "rate", "validate", "review",
    # Bloom's L6 – Create
    "design", "propose", "create", "develop", "plan",
    "formulate", "devise", "generate", "compose", "produce",
    "synthesize", "synthesise", "construct", "assemble", "modify",
    # Interrogatives
    "what", "how", "why", "when", "where", "which", "who",
    "whom", "whose", "is", "are", "does", "do", "can",
    "could", "should", "would", "will", "may", "might",
    # Math / Engineering starters
    "consider", "suppose", "assume", "given", "let",
    "if", "for", "using", "with", "perform",
    "simulate", "model", "estimate", "approximate", "convert",
    "transform", "encode", "decode", "encrypt", "decrypt",
    "reduce", "simplify", "minimize", "maximize", "optimize",
    # General academic
    "briefly", "clearly", "critically", "concisely",
    "diagrammatically", "graphically", "mathematically",
    "systematically", "tabulate", "enlist", "highlight",
    "point", "note", "comment", "remark", "suggest",
    "express", "present", "depict", "map", "arrange",
}

SCAFFOLD_TEMPLATE = """\
You generate clean university exam questions from syllabus metadata and context.

### Instruction:
Create one appropriate exam question from the given academic prompt.

### Input:
Subject: {subject}
Module: {module}
Marks: {marks}
Bloom Level: {bloom_level}

{pyq_section}

Context:
{compressed_context}

Construct a relevant question for assessment about '{topic}' based on the context.

### Response:
"""

```

### `backend/app/utils/syllabus_extractors.py`

```py
"""
Syllabus metadata extractors — course title, code, and outcomes.

Extracted from syllabus_service.py to keep the service file focused on
module parsing and structured output assembly.
"""

import re
import logging
from typing import List

logger = logging.getLogger(__name__)


# =====================================================
# Course Title Extraction
# =====================================================

def extract_course_title(text: str) -> str:
    """
    Extract the course title from syllabus text using heuristics.

    Looks for common patterns like all-caps lines, lines after 'Course Title:',
    or the first substantial line.

    Args:
        text: Raw syllabus text.

    Returns:
        Extracted course title, or "Unknown" if not found.
    """
    lines = text.split("\n")

    # Pattern 1: Look for "Course Title:" or "Course Name:" label
    for line in lines[:30]:
        line = line.strip()
        match = re.match(
            r"(?:Course\s+(?:Title|Name))\s*[:\-–]\s*(.+)",
            line, re.IGNORECASE
        )
        if match:
            title = match.group(1).strip()
            if len(title) > 3:
                return _clean_title(title)

    # Pattern 2: Look for a prominent all-caps line (likely a title)
    for line in lines[:20]:
        line = line.strip()
        # Skip very short or very long lines
        if len(line) < 5 or len(line) > 100:
            continue
        # Skip lines that are clearly not titles
        lower = line.lower()
        if any(kw in lower for kw in [
            "module", "syllabus", "semester", "university", "department",
            "credit", "marks", "hours", "regulation", "scheme", "page",
            "textbook", "reference", "outcome"
        ]):
            continue
        # All-caps line with mostly alphabetic chars
        alpha_chars = sum(1 for c in line if c.isalpha())
        if alpha_chars > 5 and line == line.upper() and alpha_chars / max(len(line), 1) > 0.6:
            return _clean_title(line)

    # Pattern 2b: Line starting with a course code followed by all-caps title
    # e.g. "19-202-0504 OPERATING SYSTEM" or "CS301 DATA STRUCTURES"
    for line in lines[:20]:
        line = line.strip()
        if len(line) < 10:
            continue
        m = re.match(
            r"^(?:[A-Z]{0,4}\s*)?(\d{2}[\-]\d{3}[\-]\d{4}|\d{2}[A-Z]{2,4}\d{3,4}|[A-Z]{2,4}[\-]?\d{3,4})\s+(.+)$",
            line
        )
        if m:
            title_part = m.group(2).strip()
            # Must be mostly alphabetic and look like a title
            alpha_chars = sum(1 for c in title_part if c.isalpha())
            if alpha_chars > 5 and title_part == title_part.upper():
                return _clean_title(title_part)

    # Pattern 3: Look for subject/course name patterns
    for line in lines[:30]:
        line = line.strip()
        match = re.match(
            r"(?:Subject|Program|Paper)\s*[:\-–]\s*(.+)",
            line, re.IGNORECASE
        )
        if match:
            title = match.group(1).strip()
            if len(title) > 3:
                return _clean_title(title)

    return "Unknown"


def _clean_title(title: str) -> str:
    """Clean and normalize a course title string."""
    # Remove trailing course codes
    title = re.sub(r"\s*[\(\[]\s*[\w\-]+\s*[\)\]]$", "", title)
    # Title case if all-caps
    if title == title.upper() and len(title) > 3:
        title = title.title()
    return title.strip()


# =====================================================
# Course Code Extraction
# =====================================================

def extract_course_code(text: str) -> str:
    """
    Extract the course code from syllabus text using regex patterns.

    Looks for patterns like XX-XXX-XXXX, CSXXX, 19CS301, etc.

    Args:
        text: Raw syllabus text.

    Returns:
        Extracted course code, or "Unknown" if not found.
    """
    lines = text.split("\n")

    # Pattern 1: Look for "Course Code:" label
    for line in lines[:30]:
        line = line.strip()
        match = re.match(
            r"(?:Course\s+Code|Subject\s+Code|Paper\s+Code|Code)\s*[:\-–]\s*(.+)",
            line, re.IGNORECASE
        )
        if match:
            code = match.group(1).strip().split()[0]  # Take first word
            if len(code) >= 3:
                return code

    # Pattern 2: Common course code formats
    # Examples: 19-202-0703, CS301, 19CS301, CSE-301, BCS-401
    code_patterns = [
        r"\b(\d{2}[\-]\d{3}[\-]\d{4})\b",           # 19-202-0703
        r"\b([A-Z]{2,4}[\-]?\d{3,4})\b",             # CS301, CSE-301, BCS-401
        r"\b(\d{2}[A-Z]{2,4}\d{3,4})\b",             # 19CS301
        r"\b([A-Z]{2,4}\d{2,3}[A-Z]?\d{0,2})\b",    # CS50, CS50A
    ]
    for line in lines[:30]:
        for pattern in code_patterns:
            match = re.search(pattern, line)
            if match:
                return match.group(1)

    return "Unknown"


# =====================================================
# Course Outcomes Extraction
# =====================================================

def extract_course_outcomes(text: str) -> List[str]:
    """
    Extract course outcomes from the raw syllabus text.

    Handles multiple formats:
    - Numbered lists:  ``1.  Familiarize with …``
    - CO-prefix:       ``CO1:  Design a minimized …``
    - Bullet points:   ``•  Design a minimized …``
    - Plain sentences after "On completion … able to:"

    Stops when it hits a Module heading, References, or a blank-line gap
    after collecting at least one outcome.
    """
    lines = text.split("\n")
    outcomes: List[str] = []
    in_outcomes_section = False
    # Track intro line ("On completion...") so we skip it
    saw_intro = False
    blank_count = 0

    for line in lines:
        stripped = line.strip()

        lower_line = stripped.lower()

        # ---- Detect start of the section ----
        if not in_outcomes_section:
            if "course outcome" in lower_line:
                in_outcomes_section = True
            continue

        # ---- We are inside Course Outcomes now ----

        # Skip the intro sentence ("On completion of this course …")
        if not saw_intro and ("on completion" in lower_line or "will be able to" in lower_line):
            saw_intro = True
            continue

        # Handle blank lines – allow 1; 2 consecutive blanks → end section
        if not stripped:
            blank_count += 1
            if blank_count >= 2 and outcomes:
                break
            continue
        blank_count = 0

        # ---- Stop markers ----
        if re.match(r"^module\s+[ivx0-9]+", lower_line, re.IGNORECASE):
            break
        if lower_line.startswith("references"):
            break
        if lower_line.startswith("textbook"):
            break

        # ---- Capture patterns ----
        # Pattern A: numbered list  "1. Familiarize …" / "1) Familiarize …"
        m_num = re.match(r"^(\d+)\s*[.)]\s*(.+)", stripped)
        # Pattern B: CO-prefix  "CO1: …" / "CO 1 - …"
        m_co = re.match(r"^CO\s*(\d+)\s*[:\-.)]\s*(.+)", stripped, re.IGNORECASE)

        if m_co:
            idx = m_co.group(1)
            body = m_co.group(2).strip()
            outcomes.append(f"CO{idx}:  {body}")
        elif m_num:
            idx = m_num.group(1)
            body = m_num.group(2).strip()
            outcomes.append(f"CO{idx}:  {body}")
        elif re.match(r"^[•\-\*]\s+", stripped):
            # Bullet point without a number
            body = re.sub(r"^[•\-\*]\s+", "", stripped)
            outcomes.append(f"CO{len(outcomes)+1}:  {body}")
        elif outcomes:
            prev = outcomes[-1]
            prev_ends_sentence = prev.rstrip().endswith(".")
            starts_with_cap = stripped[0].isupper() if stripped else False
            looks_like_new_sentence = prev_ends_sentence and starts_with_cap and len(stripped) > 15

            if looks_like_new_sentence:
                # Previous CO ended with period, this starts a new sentence → new CO
                outcomes.append(f"CO{len(outcomes)+1}:  {stripped}")
            elif len(stripped) > 10 and not stripped.isupper():
                # Genuine continuation of a wrapped line
                outcomes[-1] = f"{prev} {stripped}"

    return outcomes

```

### `backend/app/utils/question_validation.py`

```py
"""
Question validation & hallucination filtering helpers.

Extracted from question_service.py to keep the service file focused on orchestration.
"""

import re
import logging
from typing import Tuple, Optional

from app.utils.question_constants import VALID_OPENERS

logger = logging.getLogger(__name__)


def validate_question(
    question: str,
    context: str,
    marks: int,
    sbert_model=None,
    spacy_nlp=None,
) -> Tuple[bool, str]:
    """
    Validate a generated question for length, structure, hallucination,
    and semantic coherence against the source context.
    """
    q = (question or "").strip()
    context = context or ""

    # 1. Length gate (10-65 words)
    words = q.split()
    if not (10 <= len(words) <= 65):
        return False, f"length {len(words)} out of range 10-65"

    # 2. Must end with "?"
    if not q.endswith("?"):
        return False, "does not end with ?"

    # 3. Opening verb whitelist
    if not words:
        return False, "empty question"

    if words[0].lower() not in VALID_OPENERS:
        return False, f"invalid opening word: {words[0]}"

    # 3b. Reject meta-answer / lecture-note references (common failure mode).
    lowered = q.lower()
    banned_phrases = [
        "example answer",
        "lecture notes",
        "in the book",
        "earlier in the book",
        "university lecture notes",
        "supported by relevant concepts",
        "answer should be",
        "provide an answer",
        "support your analysis",
        "show all steps of your calculations",
    ]
    for phrase in banned_phrases:
        if phrase in lowered:
            return False, f"banned meta phrase: {phrase}"

    # 4. Hallucination probe — check named entities against context vocab
    if spacy_nlp is not None:
        doc = spacy_nlp(q)
        normalized_context = re.sub(r"[^a-z0-9\s\-]+", " ", context.lower())
        context_vocab = set(normalized_context.split())
        alien_entities = [
            ent.text
            for ent in doc.ents
            if ent.text
            and not (
                re.sub(r"[^a-z0-9\s\-]+", " ", ent.text.lower()).strip() in normalized_context
                or all(
                    token in context_vocab
                    for token in re.findall(r"[a-z0-9\-]+", ent.text.lower())
                )
            )
        ]
        if len(alien_entities) > 2:
            return False, f"hallucinated entities: {alien_entities}"

    # 5. Semantic coherence — cosine similarity between question and context
    if sbert_model is not None:
        try:
            from sklearn.metrics.pairwise import cosine_similarity

            q_vec = sbert_model.encode([q])
            c_vec = sbert_model.encode([context])
            sim = float(cosine_similarity(q_vec, c_vec)[0][0])
            if sim < 0.55:
                return False, f"low coherence: cosine_sim={sim:.2f}"
        except Exception as e:
            return False, f"coherence_check_failed: {e}"

    return True, "ok"


def filter_hallucinations(text: str) -> str:
    """
    Regex-based safety net to remove suspected code or mathematical
    hallucinations that Flan-T5 occasionally generates.
    """
    # Patterns for code-like assignments and loops
    hallucination_patterns = [
        r"[\w\)]+\s?=\s?[\w\)]+\s?[-\+]\s?[\w\d]+;?",  # Assignments like x = y + 1
        r"for\s+\w+\s+in\s+range.*",       # Python loops
        r"\w+\[\w+\]\s?=\s?.*",            # Array assignments
        r"printf\(.*\);?",                 # C-style print
        r"print\(.*\)",                    # Python print
        r"import\s+\w+",                   # Imports
        r"def\s+\w+\(.*\):",              # Function defs
    ]

    filtered = text
    for pattern in hallucination_patterns:
        filtered = re.sub(pattern, "", filtered, flags=re.IGNORECASE).strip()

    # Clean up any resulting double spaces or hanging semicolons
    filtered = re.sub(r"\s+", " ", filtered).strip()
    filtered = filtered.rstrip(";").strip()

    # If the filter nuked too much of the text, return original
    if len(filtered.split()) < 3:
        return text

    return filtered

```

### `backend/app/models/schemas.py`

```py
"""
Pydantic schemas for the API request/response models.
Consolidated from the old pattern/ package.
"""

from pydantic import BaseModel
from typing import List, Optional


class SubQuestionPattern(BaseModel):
    """Schema for sub-questions within a question (e.g., a, b, c)."""
    label: str
    marks: int


class OrChoicePattern(BaseModel):
    """Schema for an alternative (OR) choice."""
    marks: int
    module: str
    sub_questions: Optional[List[SubQuestionPattern]] = None


class QuestionPattern(BaseModel):
    """Schema for a single question in the exam pattern."""
    question_no: int
    marks: int
    module: str
    has_internal_choice: bool = False
    or_choice: Optional[OrChoicePattern] = None
    sub_questions: Optional[List[SubQuestionPattern]] = None


class PartPattern(BaseModel):
    """Schema for a part of the exam (e.g., PART A, PART B)."""
    part_name: str
    answer_type: str               # "ALL" or "ANY"
    marks_per_question: int
    total_questions: int
    questions_to_answer: Optional[int] = None
    questions: Optional[List[QuestionPattern]] = None


class ExamPattern(BaseModel):
    """Top-level schema for the entire exam pattern."""
    exam_name: str
    parts: List[PartPattern]


class RegenerateRequest(BaseModel):
    """Schema for regenerating a single question."""
    module: str
    marks: int
    question_no: int
    sub_questions: Optional[List[SubQuestionPattern]] = None

```

### `backend/app/api/syllabus.py`

```py
"""
Syllabus API Router — endpoint for syllabus PDF upload and topic extraction.
"""

import json
import logging

from fastapi import APIRouter, UploadFile, File

from app.services.syllabus_service import (
    extract_syllabus_text,
    extract_module_topics,
    build_structured_syllabus,
)
from app.core.config import PROCESSED_DATA_DIR
from app.services.question_service import question_service

logger = logging.getLogger(__name__)
router = APIRouter(tags=["syllabus"])


@router.post("/extract-syllabus")
async def extract_syllabus(file: UploadFile = File(...)):
    """
    Upload a syllabus PDF and extract module-wise topics.

    Returns the structured syllabus with course title, course code,
    and modules containing topics, raw text, and embedding-ready text.
    Saves the result to processed_data/syllabus_topics.json.
    """
    pdf_bytes = await file.read()

    text = extract_syllabus_text(pdf_bytes)
    modules = extract_module_topics(text)

    # Build the enriched structured output
    structured = build_structured_syllabus(text, modules)

    # Persist for downstream pipeline steps
    syllabus_path = PROCESSED_DATA_DIR / "syllabus_topics.json"
    with open(syllabus_path, "w", encoding="utf-8") as f:
        json.dump(structured, f, indent=4)

    # Clear stale caches so next generation reads fresh data
    question_service.clear_caches()

    return {
        "message": "Syllabus topics extracted successfully",
        **structured,
    }

```

### `backend/app/api/textbook.py`

```py
"""
Textbook API Router — endpoint for textbook PDF upload, chunking, and image extraction.
"""

import json
import re
import shutil
import logging
from typing import Optional, Set

from fastapi import APIRouter, UploadFile, File, Form

from app.services.ingestion_service import extract_pages
from app.services.chunking_service import chunk_text_by_page
from app.utils.image_utils import extract_images_from_pdf, map_chunks_to_images
from app.core.config import PROCESSED_DATA_DIR
from app.services.question_service import question_service

logger = logging.getLogger(__name__)
router = APIRouter(tags=["textbook"])


def parse_page_range(page_range: str) -> Set[int]:
    """
    Parse an iLovePDF-style page range string into a set of page numbers.

    Supports formats like: "1-5, 8, 10-20"

    Args:
        page_range: Comma-separated ranges (e.g., "1-5, 8, 10-20").

    Returns:
        Set of page numbers.
    """
    pages = set()
    parts = page_range.split(",")
    for part in parts:
        part = part.strip()
        if not part:
            continue
        range_match = re.match(r"(\d+)\s*-\s*(\d+)", part)
        if range_match:
            start, end = int(range_match.group(1)), int(range_match.group(2))
            pages.update(range(start, end + 1))
        elif part.isdigit():
            pages.add(int(part))
    return pages


@router.post("/chunk-textbook")
async def chunk_textbook(
    file: UploadFile = File(...),
    page_range: Optional[str] = Form(None),
):
    """
    Upload a textbook PDF, extract text, chunk it, extract images,
    and map images to chunks by page number.

    Optionally accepts a page_range parameter (e.g., "1-5, 8, 10-20")
    to process only specific pages.

    Returns the total number of chunks and images created.
    """
    # Clear old images
    image_dir = PROCESSED_DATA_DIR / "images"
    if image_dir.exists():
        shutil.rmtree(image_dir)
    image_dir.mkdir(parents=True, exist_ok=True)

    # Read PDF bytes once
    pdf_bytes = await file.read()

    # Text extraction with page metadata
    pages_text = extract_pages(pdf_bytes)
    total_pdf_pages = len(pages_text)

    # Filter pages if a range is specified
    if page_range and page_range.strip():
        requested_pages = parse_page_range(page_range)
        if requested_pages:
            pages_text = [
                (page_num, text) for page_num, text in pages_text
                if page_num in requested_pages
            ]
            logger.info(
                f"Page range filter applied: {len(pages_text)} of {total_pdf_pages} pages selected"
            )

    # Chunking with page metadata
    chunks = chunk_text_by_page(pages_text)

    # Image extraction
    images = extract_images_from_pdf(pdf_bytes, str(image_dir))

    # Filter images to only include pages in range
    if page_range and page_range.strip():
        requested_pages = parse_page_range(page_range)
        if requested_pages:
            images = [img for img in images if img.get("page") in requested_pages]

    # Map chunks ↔ images using page number
    final_chunks = map_chunks_to_images(chunks, images)

    # Save output
    output_path = PROCESSED_DATA_DIR / "textbook_chunks.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(final_chunks, f, indent=4)

    # Clear stale caches so next generation reads fresh data
    question_service.clear_caches()

    return {
        "message": "Textbook processed successfully",
        "total_chunks": len(final_chunks),
        "total_images": len(images),
        "total_pdf_pages": total_pdf_pages,
        "pages_processed": len(pages_text),
    }

```

### `backend/app/api/questions.py`

```py
"""
Questions API Router — endpoints for exam pattern configuration and question generation.
"""

import json
import logging

from fastapi import APIRouter

from app.models.schemas import ExamPattern, RegenerateRequest
from app.services.question_service import question_service
from app.services.bloom_service import bloom_service
from app.core.config import PROCESSED_DATA_DIR

logger = logging.getLogger(__name__)
router = APIRouter(tags=["questions"])


@router.post("/set-question-pattern")
async def set_question_pattern(pattern: ExamPattern):
    """
    Save the exam question pattern configuration.

    Converts the pattern into a flat generation plan and persists it.
    """
    generation_plan = []

    for part in pattern.parts:
        if part.questions:
            for question in part.questions:
                generation_plan.append({
                    "question_no": question.question_no,
                    "part": part.part_name,
                    "marks": question.marks,
                    "module": question.module,
                    "answer_type": part.answer_type,
                    "has_internal_choice": question.has_internal_choice,
                })

    pattern_path = PROCESSED_DATA_DIR / "question_pattern.json"
    with open(pattern_path, "w", encoding="utf-8") as f:
        json.dump(generation_plan, f, indent=4)

    return {
        "message": "Question pattern saved successfully",
        "generation_plan": generation_plan,
    }


@router.post("/generate-questions")
async def generate_questions(pattern: ExamPattern):
    """
    Generate exam questions based on the given pattern.

    Uses the Flan-T5 model for question generation and the Bloom's
    classifier to verify/classify the cognitive level of each question.
    """
    try:
        generated = question_service.generate_questions_from_pattern(
            pattern, str(PROCESSED_DATA_DIR)
        )

        # 1. Collect all question texts for batch processing
        all_q_texts = []
        for part_name, part_questions in generated.items():
            for q in part_questions:
                all_q_texts.append(q.get("text", ""))
                if "or_question" in q:
                    all_q_texts.append(q["or_question"].get("text", ""))
                    if "sub_questions" in q["or_question"] and q["or_question"]["sub_questions"]:
                        for sq in q["or_question"]["sub_questions"]:
                            all_q_texts.append(sq.get("text", ""))
                if "sub_questions" in q and q["sub_questions"]:
                    for sq in q["sub_questions"]:
                        all_q_texts.append(sq.get("text", ""))

        # 2. Batch classify
        all_levels = bloom_service.classify_batch(all_q_texts)

        # 3. Assign back
        level_idx = 0
        for part_name, part_questions in generated.items():
            for q in part_questions:
                q["classified_bloom_level"] = all_levels[level_idx]
                level_idx += 1
                if "or_question" in q:
                    q["or_question"]["classified_bloom_level"] = all_levels[level_idx]
                    level_idx += 1
                    if "sub_questions" in q["or_question"] and q["or_question"]["sub_questions"]:
                        for sq in q["or_question"]["sub_questions"]:
                            sq["classified_bloom_level"] = all_levels[level_idx]
                            level_idx += 1
                if "sub_questions" in q and q["sub_questions"]:
                    for sq in q["sub_questions"]:
                        sq["classified_bloom_level"] = all_levels[level_idx]
                        level_idx += 1

        # Persist output
        questions_path = PROCESSED_DATA_DIR / "generated_questions.json"
        with open(questions_path, "w", encoding="utf-8") as f:
            json.dump(generated, f, indent=4)

        return {
            "message": "Questions generated successfully",
            "questions": generated,
        }

    except Exception as e:
        logger.error(f"Question generation failed: {e}")
        return {
            "error": str(e),
            "message": "Question generation failed. Please ensure syllabus and textbook have been uploaded.",
        }


@router.post("/regenerate-question")
async def regenerate_question(req: RegenerateRequest):
    """
    Regenerate a single question for a given module and mark allocation.

    Reuses the existing T5/template pipeline via _generate_single_question,
    then classifies the result with the Bloom's classifier.
    """
    import os
    from types import SimpleNamespace

    try:
        processed = str(PROCESSED_DATA_DIR)

        # Load required data files
        topic_mapping = question_service._load_json(
            os.path.join(processed, "topic_chunk_mapping.json")
        ) or {}

        if question_service._chunks_cache is None:
            question_service._chunks_cache = question_service._load_json(
                os.path.join(processed, "textbook_chunks.json")
            ) or []
            question_service._chunks_dict_cache = {
                chunk["chunk_id"]: chunk["text"]
                for chunk in question_service._chunks_cache
            }

        chunks_dict = question_service._chunks_dict_cache or {}

        syllabus_topics = question_service._load_json(
            os.path.join(processed, "selected_topics.json")
        )
        if not syllabus_topics:
            syllabus_topics = question_service._load_json(
                os.path.join(processed, "syllabus_topics.json")
            ) or {}

        question_service._load_model()

        # Build lightweight objects matching the interface _generate_single_question expects
        mock_question = SimpleNamespace(
            question_no=req.question_no,
            marks=req.marks,
            module=req.module,
            has_internal_choice=False,
            or_choice=None,
            sub_questions=req.sub_questions,
        )
        mock_part = SimpleNamespace(
            part_name="",
            answer_type="ALL",
        )

        generated_q = question_service._generate_single_question(
            question=mock_question,
            part=mock_part,
            topic_mapping=topic_mapping,
            chunks_dict=chunks_dict,
            syllabus_topics=syllabus_topics,
            seen_topics={},
        )

        # Classify with Bloom's
        # Classify with Bloom's
        q_texts = []
        if generated_q.get("text"):
            q_texts.append(generated_q["text"])
            
        sq_count = len(generated_q.get("sub_questions", []))
        if sq_count > 0:
            for sq in generated_q["sub_questions"]:
                q_texts.append(sq.get("text", ""))

        if q_texts:
            levels = bloom_service.classify_batch(q_texts)
            
            level_idx = 0
            if generated_q.get("text"):
                generated_q["classified_bloom_level"] = levels[level_idx]
                level_idx += 1
                
            if sq_count > 0:
                for sq in generated_q["sub_questions"]:
                    sq["classified_bloom_level"] = levels[level_idx]
                    level_idx += 1

        return {"question": generated_q}

    except Exception as e:
        logger.error(f"Question regeneration failed: {e}")
        return {
            "error": str(e),
            "message": "Question regeneration failed.",
        }

```

### `backend/app/api/mapping.py`

```py
"""
Mapping API Router — endpoint for semantic module-to-chunk mapping.
"""

import json
import logging

from typing import Optional, Dict, List
from pydantic import BaseModel
from fastapi import APIRouter

from app.services.mapping_service import mapping_service
from app.core.config import PROCESSED_DATA_DIR

logger = logging.getLogger(__name__)
router = APIRouter(tags=["mapping"])

class MappingRequest(BaseModel):
    # selected_modules maps module names to a list of selected topic strings
    selected_modules: Optional[Dict[str, List[str]]] = None

@router.post("/semantic-mapping")
async def semantic_mapping(request: MappingRequest = None):
    """
    Perform semantic mapping between syllabus modules and textbook chunks
    using the SBERT model.

    If selected_modules is provided in the request payload, only those 
    topics will be mapped and saved.
    """
    syllabus_path = PROCESSED_DATA_DIR / "syllabus_topics.json"
    chunks_path = PROCESSED_DATA_DIR / "textbook_chunks.json"

    if not syllabus_path.exists():
        return {"error": "Syllabus not processed yet. Upload a syllabus first."}

    if not chunks_path.exists():
        return {"error": "Textbook not processed yet. Upload a textbook first."}

    # Load structured syllabus
    with open(syllabus_path, "r", encoding="utf-8") as f:
        structured_syllabus = json.load(f)

    modules = structured_syllabus.get("modules", {})
    if not modules:
        return {"error": "No modules were extracted from the syllabus. Please check the uploaded syllabus PDF."}

    # Filter syllabus if the user passed specifically selected topics
    if request and request.selected_modules:
        filtered_modules = {}
        for mod_name, mod_data in modules.items():
            if mod_name in request.selected_modules:
                # Keep only selected topics
                selected = request.selected_modules[mod_name]
                if selected:
                    filtered_modules[mod_name] = {
                        "topics": [t for t in mod_data.get("topics", []) if t in selected]
                    }
        structured_syllabus["modules"] = filtered_modules

    # Save the selected/filtered topics to a new file so the question generator knows what to use
    selected_topics_path = PROCESSED_DATA_DIR / "selected_topics.json"
    with open(selected_topics_path, "w", encoding="utf-8") as f:
        json.dump(structured_syllabus, f, indent=4)

    # Load textbook chunks
    with open(chunks_path, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    if not chunks:
        return {"error": "No text chunks were generated from the textbook. Please check the uploaded textbook PDF."}

    # Perform module-level mapping using SBERT with the filtered syllabus
    module_mapping = mapping_service.map_modules_to_chunks(
        structured_syllabus, chunks
    )

    if not module_mapping:
        return {"error": "Semantic mapping failed to associate any modules with chunks. Please ensure the syllabus and textbook content are related."}

    # Persist mapping
    mapping_path = PROCESSED_DATA_DIR / "topic_chunk_mapping.json"
    with open(mapping_path, "w", encoding="utf-8") as f:
        json.dump(module_mapping, f, indent=4)

    return {
        "message": "Semantic mapping completed successfully",
        "mapping": module_mapping,
    }

```

### `backend/app/services/mapping_service.py`

```py
"""
Mapping Service — semantic topic-to-chunk mapping using SBERT.

Responsibilities:
- Load the custom fine-tuned SBERT model (or fallback to HuggingFace)
- Encode syllabus topics and textbook chunks
- Map each module to the most relevant chunks using cosine similarity
- Apply diversity filtering to avoid redundant chunk selection
- Deduplicate near-identical content within each module
"""

import os
import re
import glob
import pickle
import hashlib
import logging
from typing import List, Dict, Any

from app.core.config import (
    SBERT_MODEL_PATH,
    SBERT_FALLBACK_MODEL,
    SIMILARITY_THRESHOLD,
    DIVERSITY_THRESHOLD,
    MAX_CHUNKS_PER_TOPIC,
    PROCESSED_DATA_DIR,
)

logger = logging.getLogger(__name__)


class MappingService:
    """
    Encapsulates SBERT-based module-to-chunk semantic mapping.

    Loads the custom SBERT model from the local models/ directory.
    Falls back to a HuggingFace model if the local model is not found.
    """

    # Maximum number of embedding cache files to keep on disk
    _MAX_CACHE_FILES = 3

    def __init__(self):
        self._model = None
        self._cache_dir = os.path.join(str(PROCESSED_DATA_DIR), "cache")
        os.makedirs(self._cache_dir, exist_ok=True)

    @property
    def model(self):
        """Lazy-load the SBERT model on first use."""
        if self._model is None:
            from sentence_transformers import SentenceTransformer

            if os.path.exists(SBERT_MODEL_PATH):
                logger.info(f"Loading custom SBERT model from {SBERT_MODEL_PATH}")
                self._model = SentenceTransformer(SBERT_MODEL_PATH)
            else:
                logger.warning(
                    f"Custom SBERT model not found at {SBERT_MODEL_PATH}. "
                    f"Falling back to {SBERT_FALLBACK_MODEL}"
                )
                self._model = SentenceTransformer(SBERT_FALLBACK_MODEL)
        return self._model

    # =======================================================
    # Embedding Cache (hash-based with auto-cleanup)
    # =======================================================

    @staticmethod
    def _compute_hash(texts: List[str]) -> str:
        """Compute an MD5 hash of the concatenated text for cache keying."""
        text_blob = "".join(texts)
        return hashlib.md5(text_blob.encode()).hexdigest()

    def _encode_with_cache(self, texts: List[str], prefix: str = "emb"):
        """
        Encode texts with SBERT, using a hash-based disk cache.
        If embeddings for these exact texts already exist, load from pickle.
        Otherwise compute, save, and return.
        """
        import numpy as np  # noqa: local import to match existing pattern

        text_hash = self._compute_hash(texts)
        cache_path = os.path.join(self._cache_dir, f"{prefix}_{text_hash}.pkl")

        if os.path.exists(cache_path):
            logger.info(f"[Cache HIT] Loading embeddings from {cache_path}")
            with open(cache_path, "rb") as f:
                return pickle.load(f)

        logger.info(f"[Cache MISS] Computing embeddings for {len(texts)} texts...")
        embeddings = self.model.encode(texts)

        with open(cache_path, "wb") as f:
            pickle.dump(embeddings, f)
        logger.info(f"[Cache SAVE] Saved embeddings to {cache_path}")

        self._cleanup_cache(prefix)
        return embeddings

    def _cleanup_cache(self, prefix: str = "emb"):
        """Keep only the most recent N cache files per prefix."""
        pattern = os.path.join(self._cache_dir, f"{prefix}_*.pkl")
        cache_files = sorted(glob.glob(pattern), key=os.path.getmtime)
        while len(cache_files) > self._MAX_CACHE_FILES:
            oldest = cache_files.pop(0)
            os.remove(oldest)
            logger.info(f"[Cache Cleanup] Removed old cache: {oldest}")

    def map_modules_to_chunks(
        self,
        structured_syllabus: Dict[str, Any],
        chunks: List[Dict[str, Any]],
        similarity_threshold: float = SIMILARITY_THRESHOLD,
        diversity_threshold: float = DIVERSITY_THRESHOLD,
        chunks_per_topic: int = 4,
        dedup_threshold: float = 0.92,
    ) -> Dict[str, Any]:
        """
        Map each active syllabus topic directly to the most semantically relevant textbook chunks.
        
        This establishes strict, granular context bounds so large/hallucinated
        context mixing is prevented during question generation.
        """
        modules = structured_syllabus.get("modules", {})
        if not modules or not chunks:
            logger.warning("Empty modules or chunks — returning empty mapping")
            return {}

        from sklearn.metrics.pairwise import cosine_similarity
        import numpy as np

        # Encode all chunk texts (with caching)
        chunk_texts = [c["text"] for c in chunks]
        chunk_embeddings = self._encode_with_cache(chunk_texts, prefix="chunks")

        module_mapping: Dict[str, Any] = {}

        for module_name, module_data in modules.items():
            topics = module_data.get("topics", [])
            if not topics:
                continue

            topic_mappings = {}
            module_all_selected_indices = set()

            for topic in topics:
                # Fetch embedding per specific topic
                topic_emb = self._encode_with_cache([topic], prefix="topics")[0].reshape(1, -1)
                
                # Compare THIS specific topic to ALL chunks
                scores = cosine_similarity(topic_emb, chunk_embeddings)[0]

                # Filtering Candidates
                candidates = [
                    (idx, float(score))
                    for idx, score in enumerate(scores)
                    if score >= similarity_threshold
                ]

                # Fallback to top 4 if thresh fails to capture anything
                if not candidates:
                    top_indices = np.argsort(scores)[-4:][::-1]
                    candidates = [(int(idx), float(scores[idx])) for idx in top_indices]

                candidates.sort(key=lambda x: x[1], reverse=True)

                # Diversity filtering specifically for this topic
                selected_indices = []
                for idx, score in candidates:
                    if not selected_indices:
                        selected_indices.append(idx)
                        continue

                    # Assure diversity
                    is_diverse = all(
                        cosine_similarity(
                            [chunk_embeddings[idx]], [chunk_embeddings[sel_idx]]
                        )[0][0] < diversity_threshold
                        for sel_idx in selected_indices
                    )

                    if is_diverse:
                        selected_indices.append(idx)

                    if len(selected_indices) >= chunks_per_topic:
                        break

                # Deduplicate near-identical sentences within selected chunks
                selected_texts = [chunk_texts[idx] for idx in selected_indices]
                deduped_indices = self._deduplicate_chunks(
                    selected_indices, selected_texts, dedup_threshold
                )

                # Store deduplicated results for this specific topic
                topic_mappings[topic] = [
                    {
                        "chunk_id": chunks[idx]["chunk_id"],
                        "page": chunks[idx].get("page"),
                        "score": float(scores[idx]),
                    }
                    for idx in deduped_indices
                ]
                
                module_all_selected_indices.update(deduped_indices)

            # Build a generalized embedding_ready_text for the whole module just in case
            generalized_raw_text = " ".join([chunk_texts[idx] for idx in module_all_selected_indices])
            embedding_ready = self._build_embedding_text(generalized_raw_text)

            module_mapping[module_name] = {
                "topics": topics,
                "embedding_ready_text": embedding_ready,
                "topic_mappings": topic_mappings
            }

        logger.info(f"Mapped {len(module_mapping)} modules granularly by topics")
        return module_mapping

    def _deduplicate_chunks(
        self,
        indices: List[int],
        texts: List[str],
        threshold: float,
    ) -> List[int]:
        """
        Remove near-duplicate chunks based on text similarity.

        Args:
            indices: List of chunk indices.
            texts: Corresponding texts for those indices.
            threshold: Similarity above this = duplicate.

        Returns:
            Filtered list of indices with duplicates removed.
        """
        if len(indices) <= 1:
            return indices

        from sklearn.metrics.pairwise import cosine_similarity

        text_embeddings = self.model.encode(texts)
        sim_matrix = cosine_similarity(text_embeddings)

        keep = [0]  # Always keep the first (highest-scoring)
        for i in range(1, len(indices)):
            is_unique = all(
                sim_matrix[i][j] < threshold
                for j in keep
            )
            if is_unique:
                keep.append(i)

        return [indices[i] for i in keep]

    def _build_embedding_text(self, raw_text: str) -> str:
        """
        Clean raw text for use in semantic search / vector embeddings.

        Removes special characters, extra whitespace, and normalizes formatting.
        """
        # Remove special chars except basic punctuation
        cleaned = re.sub(r"[^\w\s]", " ", raw_text)
        # Collapse whitespace
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        return cleaned

    # Keep the old method for backward compatibility
    def map_topics_to_chunks(
        self,
        topics: List[str],
        chunks: List[Dict[str, Any]],
        similarity_threshold: float = SIMILARITY_THRESHOLD,
        diversity_threshold: float = DIVERSITY_THRESHOLD,
        max_chunks: int = MAX_CHUNKS_PER_TOPIC,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Legacy method: Map each syllabus topic to the most relevant chunks.
        Kept for backward compatibility.
        """
        if not topics or not chunks:
            logger.warning("Empty topics or chunks — returning empty mapping")
            return {}

        topic_embeddings = self.model.encode(topics)
        chunk_texts = [c["text"] for c in chunks]
        chunk_embeddings = self.model.encode(chunk_texts)

        from sklearn.metrics.pairwise import cosine_similarity

        similarity_matrix = cosine_similarity(topic_embeddings, chunk_embeddings)
        mapping: Dict[str, List[Dict[str, Any]]] = {}

        for i, topic in enumerate(topics):
            topic_key = str(topic).strip()
            scores = similarity_matrix[i]

            candidates = [
                (idx, float(score))
                for idx, score in enumerate(scores)
                if score >= similarity_threshold
            ]

            if not candidates:
                best_idx = int(scores.argmax())
                mapping[topic_key] = [{
                    "chunk_id": chunks[best_idx]["chunk_id"],
                    "page": chunks[best_idx].get("page"),
                    "score": float(scores[best_idx]),
                }]
                continue

            candidates.sort(key=lambda x: x[1], reverse=True)

            selected_indices = []
            for idx, score in candidates:
                if not selected_indices:
                    selected_indices.append(idx)
                    continue

                is_diverse = all(
                    cosine_similarity(
                        [chunk_embeddings[idx]], [chunk_embeddings[sel_idx]]
                    )[0][0] < diversity_threshold
                    for sel_idx in selected_indices
                )

                if is_diverse:
                    selected_indices.append(idx)

                if len(selected_indices) >= max_chunks:
                    break

            mapping[topic_key] = [
                {
                    "chunk_id": chunks[idx]["chunk_id"],
                    "page": chunks[idx].get("page"),
                    "score": float(scores[idx]),
                }
                for idx in selected_indices
            ]

        logger.info(f"Mapped {len(topics)} topics to chunks")
        return mapping


# Module-level singleton for reuse across requests
mapping_service = MappingService()

```

### `backend/app/services/bloom_service.py`

```py
"""
Bloom's Taxonomy Classification Service — classify questions by cognitive level.

Responsibilities:
- Classify a question text into one of 6 Bloom's taxonomy levels
- Use DistilBERT-based classification from the trained model at models/blooms_classifier
- Fall back to keyword-based heuristic classification otherwise

Bloom's Levels: Remember, Understand, Apply, Analyze, Evaluate, Create
"""

import os
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)

# Bloom's taxonomy levels in order
BLOOM_LEVELS = ["Remember", "Understand", "Apply", "Analyze", "Evaluate", "Create"]

# Map numeric LABEL_N → Bloom level (fallback if config.json still has generic labels)
LABEL_INDEX_MAP = {
    "LABEL_0": "Remember",
    "LABEL_1": "Understand",
    "LABEL_2": "Apply",
    "LABEL_3": "Analyze",
    "LABEL_4": "Evaluate",
    "LABEL_5": "Create",
}

# Keyword heuristics for fallback classification
BLOOM_KEYWORDS = {
    "Remember": [
        "define", "list", "state", "identify", "name", "recall",
        "recognize", "describe", "what is", "enumerate", "mention",
    ],
    "Understand": [
        "explain", "summarize", "paraphrase", "interpret", "classify",
        "discuss", "illustrate", "describe how", "distinguish",
    ],
    "Apply": [
        "apply", "demonstrate", "calculate", "solve", "use",
        "implement", "execute", "compute", "show how", "determine",
    ],
    "Analyze": [
        "analyze", "compare", "contrast", "differentiate", "examine",
        "break down", "categorize", "distinguish between", "investigate",
    ],
    "Evaluate": [
        "evaluate", "justify", "assess", "critique", "judge",
        "argue", "defend", "support", "recommend", "prioritize",
    ],
    "Create": [
        "design", "create", "develop", "propose", "construct",
        "formulate", "invent", "compose", "plan", "devise",
    ],
}

# Auto-discover the model path relative to the project root
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent  # backend -> AQPG
_DEFAULT_MODEL_PATH = _PROJECT_ROOT / "models" / "bloom_classifier" / "kaggle" / "working" / "blooms_classifier"


class BloomClassifierService:
    """
    Classifies question text into Bloom's taxonomy levels.

    Attempts to use a fine-tuned DistilBERT model for classification.
    Falls back to keyword-based heuristics if no model is available.
    """

    def __init__(self, model_path: Optional[str] = None):
        self._classifier = None
        self._model_path = model_path or str(_DEFAULT_MODEL_PATH)
        self._load_attempted = False

    def _load_model(self):
        """Attempt to load the DistilBERT classifier."""
        if self._load_attempted:
            return
        self._load_attempted = True

        try:
            from transformers import pipeline

            if self._model_path and os.path.exists(self._model_path):
                logger.info(f"Loading Bloom's DistilBERT classifier from {self._model_path}")
                self._classifier = pipeline(
                    "text-classification",
                    model=self._model_path,
                    tokenizer=self._model_path,
                )
                logger.info("Bloom's DistilBERT classifier loaded successfully")
            else:
                logger.info(
                    f"No fine-tuned Bloom classifier found at {self._model_path}. "
                    "Using keyword-based classification."
                )
        except Exception as e:
            logger.warning(f"Failed to load Bloom classifier model: {e}")

    def classify(self, question_text: str) -> str:
        """
        Classify a question into a Bloom's taxonomy level.

        Args:
            question_text: The text of the question.

        Returns:
            One of: Remember, Understand, Apply, Analyze, Evaluate, Create.
        """
        self._load_model()

        # Try model-based classification
        if self._classifier is not None:
            return self._classify_with_model(question_text)

        # Fallback to keyword heuristics
        return self._classify_with_keywords(question_text)

    def classify_batch(self, question_texts: List[str]) -> List[str]:
        """
        Classify a batch of questions into Bloom's taxonomy levels.
        MUCH faster than individual calls on CPU.
        """
        if not question_texts:
            return []
            
        self._load_model()
        
        # If model is not loaded, fallback to keywords for each
        if self._classifier is None:
            return [self._classify_with_keywords(t) for t in question_texts]
            
        try:
            # transformers pipeline handles lists efficiently
            results = self._classifier(question_texts, batch_size=4)
            labels = []
            for i, res in enumerate(results):
                label = res["label"]
                
                # Mapping logic (extracted to helper)
                labels.append(self._map_label_to_bloom(label, question_texts[i]))
            return labels
        except Exception as e:
            logger.warning(f"Batch classification failed: {e}")
            return [self._classify_with_keywords(t) for t in question_texts]

    def _map_label_to_bloom(self, label: str, original_text: str) -> str:
        """Helper to map model labels to BLOOM_LEVELS."""
        # If the label is already a Bloom level name, return it
        for level in BLOOM_LEVELS:
            if level.lower() == label.lower():
                return level

        # If it's a generic LABEL_N, map it
        if label in LABEL_INDEX_MAP:
            return LABEL_INDEX_MAP[label]

        # Last resort: try substring matching
        for level in BLOOM_LEVELS:
            if level.lower() in label.lower():
                return level

        return self._classify_with_keywords(original_text)

    def _classify_with_model(self, question_text: str) -> str:
        """Classify using the DistilBERT pipeline."""
        try:
            result = self._classifier(question_text[:512])
            if result and len(result) > 0:
                return self._map_label_to_bloom(result[0]["label"], question_text)
        except Exception as e:
            logger.warning(f"Model classification failed: {e}")

        return self._classify_with_keywords(question_text)

    def _classify_with_keywords(self, question_text: str) -> str:
        """
        Classify using keyword matching heuristics.
        Checks from highest-order (Create) to lowest (Remember).
        """
        text_lower = question_text.lower()

        # Check from highest to lowest Bloom level
        for level in reversed(BLOOM_LEVELS):
            keywords = BLOOM_KEYWORDS[level]
            for keyword in keywords:
                if keyword in text_lower:
                    return level

        # Default to Remember if no keywords match
        return "Remember"


# Module-level singleton — auto-discovers the model from the project's models/ directory
bloom_service = BloomClassifierService()


```

### `backend/app/services/chunking_service.py`

```py
"""
Chunking Service — split extracted textbook text into semantic chunks.

Responsibilities:
- Split page-level text into character-based chunks using LangChain's
  RecursiveCharacterTextSplitter (respects sentence boundaries)
- Filter out low-quality chunks via technical density and sentence count
- Preserve page number metadata on each chunk
"""

import re
import logging
from typing import List, Dict, Any, Tuple

from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core.config import CHUNK_SIZE_CHARS, CHUNK_OVERLAP_CHARS, MIN_CHUNK_LENGTH

logger = logging.getLogger(__name__)


# =====================================================
# Quality Filters (Step 5 from upgrade plan)
# =====================================================

def technical_density(text: str) -> float:
    """
    Measure the ratio of 'technical' words in a text.

    A word is considered technical if it:
    - Contains digits (e.g., SHA-256, AES-128)
    - Contains uppercase letters (e.g., RSA, DES)
    - Is longer than 6 characters (e.g., cryptography, authentication)

    Returns:
        Float between 0.0 and 1.0.
    """
    words = text.split()
    if not words:
        return 0.0
    technical_words = [
        w for w in words
        if (
            any(c.isdigit() for c in w)
            or any(c.isupper() for c in w)
            or len(w) > 6
        )
    ]
    return len(technical_words) / len(words)


def sentence_count(text: str) -> int:
    """Count the number of sentences in a text block."""
    # Split on sentence-ending punctuation followed by whitespace or end-of-string
    sentences = re.split(r'[.!?]+(?:\s|$)', text.strip())
    # Filter out empty strings from the split
    return len([s for s in sentences if s.strip()])


def _is_quality_chunk(text: str) -> bool:
    """
    Reject a chunk if:
    - sentence_count < 2
    - technical_density < 0.1
    """
    sc = sentence_count(text)
    td = technical_density(text)
    if sc < 2:
        return False
    if td < 0.1:
        return False
    return True


# =====================================================
# Main Chunking Function
# =====================================================

def chunk_text_by_page(
    pages_text: List[Tuple[int, str]],
    chunk_size: int = CHUNK_SIZE_CHARS,
    chunk_overlap: int = CHUNK_OVERLAP_CHARS,
    min_length: int = MIN_CHUNK_LENGTH,
) -> List[Dict[str, Any]]:
    """
    Split page-level text into character-based chunks using LangChain's
    RecursiveCharacterTextSplitter, with quality filtering.

    Args:
        pages_text: List of (page_number, page_text) tuples.
        chunk_size: Target chunk size in characters.
        chunk_overlap: Overlap between consecutive chunks in characters.
        min_length: Minimum character length for a chunk to be kept.

    Returns:
        List of chunk dicts with keys: chunk_id, page, text.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
        length_function=len,
    )

    chunks: List[Dict[str, Any]] = []
    chunk_id = 1
    rejected = 0

    for page_number, text in pages_text:
        if not text or not text.strip():
            continue

        # Split the page text into character-based chunks
        page_chunks = splitter.split_text(text)

        for chunk_text in page_chunks:
            chunk_text = chunk_text.strip()

            # Reject chunks that are too short
            if len(chunk_text) < min_length:
                rejected += 1
                continue

            # Reject chunks that fail quality filters
            if not _is_quality_chunk(chunk_text):
                rejected += 1
                continue

            chunks.append({
                "chunk_id": chunk_id,
                "page": page_number,
                "text": chunk_text,
            })
            chunk_id += 1

    logger.info(
        f"Created {len(chunks)} chunks from {len(pages_text)} pages "
        f"(rejected {rejected} low-quality chunks)"
    )
    return chunks

```

### `backend/app/services/question_service.py`

```py
"""
Question Generation Service — generate exam questions using Flan-T5 and Mistral.

Responsibility:
- Orchestrate the generation pipeline (Chunks -> Draft -> Evaluate/Refine -> Final).
- Manage model caching and loading (PyTorch, SentenceTransformers, spaCy).
- Provide the public API endpoint methods.
"""

import os
import re
import json
import random
import logging
import torch
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path

from app.core.config import (
    FLAN_T5_MODEL_PATH,
    FLAN_T5_FALLBACK_MODEL,
    SBERT_MODEL_PATH,
    SBERT_FALLBACK_MODEL,
    PROCESSED_DATA_DIR,
    PROJECT_ROOT,
)

# --- Imported Utilities ---
from app.utils.question_constants import (
    BLOOM_VERBS,
    GENERIC_SUBJECT_NAMES,
    SCAFFOLD_TEMPLATE,
    CONTEXT_STOPWORDS
)

from app.utils.ollama_client import (
    ollama_generate,
    extract_generated_question,
    refine_with_ollama
)

from app.utils.context_utils import (
    compress_context,
    get_relevant_chunks,
    find_matching_key,
    normalize_subject_name,
    mark_bucket,
    extract_topic_tokens
)

from app.utils.question_validation import (
    validate_question,
    filter_hallucinations
)


logger = logging.getLogger(__name__)


class QuestionService:
    """
    Generates exam questions using a fine-tuned Flan-T5 model and Mistral refinement.
    """

    def __init__(self):
        self._model = None
        self._tokenizer = None
        self._model_loaded = False
        self._load_attempted = False
        # Cache for textbook data
        self._chunks_cache: Optional[List[Dict[str, Any]]] = None
        self._chunks_dict_cache: Optional[Dict[int, str]] = None
        self._syllabus_cache: Optional[Dict[str, Any]] = None
        # High-mark (>5) pipeline caches
        self._pyq_dataset: Optional[List[Dict[str, Any]]] = None
        self._sbert_model = None
        self._spacy_nlp = None

        # Best-effort warmup 
        try:
            self._load_pyq_dataset()
        except Exception as e:
            logger.warning(f"[HighMark] PYQ warmup failed: {e}")

        try:
            self._get_spacy_nlp()
        except Exception as e:
            logger.warning(f"[HighMark] spaCy warmup failed: {e}")

    def clear_caches(self):
        """Reset all data caches so the next generation reads fresh files."""
        self._chunks_cache = None
        self._chunks_dict_cache = None
        self._syllabus_cache = None

    @staticmethod
    def _load_json(filepath: str) -> Optional[Any]:
        """Utility to safely load a JSON file."""
        import os, json
        if not os.path.exists(filepath):
            return None
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)

    def _get_sbert_model(self):
        if self._sbert_model is not None:
            return self._sbert_model

        from sentence_transformers import SentenceTransformer

        if os.path.exists(SBERT_MODEL_PATH):
            logger.info(f"[HighMark] Loading custom SBERT model from {SBERT_MODEL_PATH}")
            self._sbert_model = SentenceTransformer(SBERT_MODEL_PATH)
        else:
            logger.warning(
                f"[HighMark] Custom SBERT model not found at {SBERT_MODEL_PATH}. "
                f"Falling back to {SBERT_FALLBACK_MODEL}"
            )
            self._sbert_model = SentenceTransformer(SBERT_FALLBACK_MODEL)

        return self._sbert_model

    def _get_spacy_nlp(self):
        if self._spacy_nlp is not None:
            return self._spacy_nlp

        try:
            import spacy
            logger.info("[HighMark] Loading spacy model en_core_web_sm...")
            self._spacy_nlp = spacy.load("en_core_web_sm")
        except Exception as e:
            logger.warning(f"[HighMark] spaCy not available (entity checks skipped): {e}")
            self._spacy_nlp = None
        return self._spacy_nlp

    def _load_pyq_dataset(self) -> List[Dict[str, Any]]:
        if self._pyq_dataset is not None:
            return self._pyq_dataset

        pyq_path = Path(PROJECT_ROOT) / "pyq_mistral_train.jsonl"
        if not pyq_path.exists():
            logger.warning(f"[HighMark] pyq_mistral_train.jsonl not found at {pyq_path}.")
            self._pyq_dataset = []
            return self._pyq_dataset

        loaded: List[Dict[str, Any]] = []
        with open(pyq_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    loaded.append(json.loads(line))
                except Exception:
                    continue

        self._pyq_dataset = loaded
        logger.info(f"[HighMark] Loaded {len(self._pyq_dataset)} PYQ dataset rows.")
        return self._pyq_dataset


    def _parse_pyq_metadata(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """Internal helper for fetch_similar_pyqs."""
        input_text = row.get("input", "") or ""
        direct_subject = (row.get("subject") or "").strip()
        direct_module = (row.get("module") or "").strip()
        direct_marks = row.get("marks")
        direct_bloom = (row.get("bloom_level") or "").strip()

        subject_match = re.search(r"Subject:\s*(.+)", input_text)
        module_match = re.search(r"Module:\s*(.+)", input_text)
        marks_match = re.search(r"Marks:\s*(\d+)", input_text)
        bloom_match = re.search(r"Bloom\s+Level:\s*([^\n]+)", input_text)
        context_match = re.search(r"Context:\s*(.+?)\n\n", input_text, re.DOTALL)

        subject_raw = direct_subject or (subject_match.group(1).strip() if subject_match else "")
        module_raw = direct_module or (module_match.group(1).strip() if module_match else "")
        parsed_marks = None
        if direct_marks is not None:
            try:
                parsed_marks = int(direct_marks)
            except (TypeError, ValueError):
                parsed_marks = None
        if parsed_marks is None and marks_match:
            parsed_marks = int(marks_match.group(1))
            
        return {
            "subject": subject_raw,
            "normalized_subject": normalize_subject_name(subject_raw),
            "module": module_raw,
            "normalized_module": module_raw, # Handled externally
            "marks": parsed_marks,
            "mark_bucket": mark_bucket(parsed_marks) if parsed_marks is not None else "unknown",
            "bloom_level": direct_bloom or (bloom_match.group(1).strip() if bloom_match else ""),
            "context": context_match.group(1).strip() if context_match else "",
        }

    def fetch_similar_pyqs(
        self, topic: str, pyq_dataset: List[Dict[str, Any]], k: int = 3, subject: str = "", module: str = "", marks: Optional[int] = None,
    ) -> List[str]:
        candidates = []
        norm_subject = normalize_subject_name(subject)
        topic_tokens = extract_topic_tokens(topic)
        target_bucket = mark_bucket(marks)

        for row in pyq_dataset:
            output = (row.get("response") or row.get("output") or "").strip()
            if not output: continue

            meta = self._parse_pyq_metadata(row)
            haystack = " ".join([output.lower(), (meta.get("context") or "").lower(), (row.get("input") or "").lower()])
            token_overlap = sum(1 for token in topic_tokens if token in haystack)
            candidates.append({"output": output, "meta": meta, "token_overlap": token_overlap})

        if not candidates: return [""] * k

        filtered = [c for c in candidates if c["token_overlap"] > 0]
        if not filtered: filtered = candidates

        pyq_questions = [item["output"] for item in filtered]
        k = min(k, len(pyq_questions))
        sbert_model = self._get_sbert_model()
        from sentence_transformers import util

        topic_vec = sbert_model.encode(topic, convert_to_tensor=True)
        q_vecs = sbert_model.encode(pyq_questions, convert_to_tensor=True)
        scores = util.cos_sim(topic_vec, q_vecs)[0]
        top_indices = scores.topk(k).indices.tolist()
        return [pyq_questions[i] for i in top_indices]


    def generate_high_mark_question(
        self, topic: str, chunks: List[str], marks: int, subject: str = "Computer Science", module: str = "",
    ) -> str:
        try:
            sbert_model = self._get_sbert_model()
            context = compress_context(chunks, topic, max_tokens=400, sbert_model=sbert_model)
            expected_bloom = self._expected_bloom_for_marks(marks)
            
            # Fetch few-shot PYQ exemplars to improve stylistic quality
            if self._pyq_dataset:
                pyqs = self.fetch_similar_pyqs(topic, self._pyq_dataset, k=2, subject=subject, module=module, marks=marks)
            else:
                pyqs = []
                
            pyq_section = ""
            if pyqs:
                valid_pyqs = [q for q in pyqs if len(q.split()) > 10]
                if valid_pyqs:
                    formatted_pyqs = "\n".join([f"- {q}" for q in valid_pyqs])
                    pyq_section = f"Reference Stylistic Examples (do NOT copy content):\n{formatted_pyqs}\n"
            
            last_reason = ""
            for attempt in range(3):
                prompt = SCAFFOLD_TEMPLATE.format(
                    subject=subject, module=module or "Unknown", marks=marks,
                    bloom_level=expected_bloom, compressed_context=context, topic=topic,
                    pyq_section=pyq_section
                )

                if attempt > 0 and last_reason:
                    prompt += f"\nNote: Your previous attempt was rejected because: {last_reason}. Please correct this."

                full_output = ollama_generate(
                    prompt,
                    options={"num_predict": 120, "temperature": 0.65, "repeat_penalty": 1.3},
                    model="mistral-pyq"
                )

                question = extract_generated_question(full_output)
                question = (question or "").strip()
                if "?" in question: question = question[: question.index("?") + 1].strip()
                if question and not question.endswith("?"): question = question.rstrip(".") + "?"

                q_words = question.split() if question else []
                if len(q_words) > 60:
                    question = " ".join(q_words[:60]).rstrip(".")
                    if not question.endswith("?"): question = question.rstrip("?") + "?"

                spacy_nlp = self._get_spacy_nlp()
                valid, reason = validate_question(question, context, marks, sbert_model, spacy_nlp)
                if valid: return question

                last_reason = reason
                logger.info(f"[HighMark] Rejected attempt {attempt + 1}: {reason}")

            return self.fallback_t5_anchor_rewrite(topic, context, marks, subject)
        except Exception as e:
            logger.error(f"[HighMark] Generation crashed; falling back to template: {e}")
            context_str = locals().get("context")
            return self._generate_with_template(topic, context_str if isinstance(context_str, str) else None, marks=marks)

    def fallback_t5_anchor_rewrite(self, topic: str, context: str, marks: int, subject: str) -> str:
        try:
            t5_draft = self._generate_with_t5(topic, context, marks)
        except Exception as e:
            logger.warning(f"[HighMark] T5 draft failed; using template. Details: {e}")
            t5_draft = self._generate_with_template(topic, context, marks=marks)

        context_excerpt = (context or "").strip()
        if len(context_excerpt.split()) > 220:
            context_excerpt = " ".join(context_excerpt.split()[:220])

        rewrite_prompt = f"""\
You generate clean university exam questions from syllabus metadata and context.

### Instruction:
Rewrite the following draft into a clean, specific {marks}-mark exam question.
It must end with "?", be under 60 words, and be answerable from the provided context.
Do NOT reference any "book" or "lecture notes". Do NOT write an answer; write only the question.

### Input:
Context:
{context_excerpt}

Draft: {t5_draft}

### Response:
"""

        last_reason = ""
        sbert_model = self._get_sbert_model()
        spacy_nlp = self._get_spacy_nlp()
        
        for attempt in range(2):
            try:
                prompt = rewrite_prompt
                if attempt > 0 and last_reason:
                    prompt = prompt.rstrip() + f"\nNote: Your previous attempt was rejected because: {last_reason}. Please correct it.\n"

                full_output = ollama_generate(
                    prompt,
                    options={"num_predict": 100, "temperature": 0.5, "repeat_penalty": 1.2},
                    model="mistral"
                )
                result = extract_generated_question(full_output)
                result = (result or "").strip()
                if "?" in result: result = result[: result.index("?") + 1].strip()
                if result and not result.endswith("?"): result = result.rstrip(".") + "?"

                r_words = result.split() if result else []
                if len(r_words) > 60:
                    result = " ".join(r_words[:60]).rstrip(".")
                    if not result.endswith("?"): result = result.rstrip("?") + "?"

                valid, reason = validate_question(result, context, marks, sbert_model, spacy_nlp)
                if valid: return result

                last_reason = reason
                logger.info(f"[HighMark] Fallback attempt {attempt + 1} rejected: {reason}")
            except Exception as e:
                logger.error(f"[HighMark] Fallback rewrite failed: {e}")

        t5_draft_q = (t5_draft or "").strip()
        if t5_draft_q and not t5_draft_q.endswith("?"):
            t5_draft_q = t5_draft_q.rstrip(".") + "?"
        return t5_draft_q


    def _load_model(self):
        if self._load_attempted: return
        self._load_attempted = True

        try:
            from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
            model_path = FLAN_T5_MODEL_PATH
            if not os.path.exists(model_path):
                model_path = FLAN_T5_FALLBACK_MODEL
            logger.info(f"Loading T5 model from {model_path}...")
            self._tokenizer = AutoTokenizer.from_pretrained(model_path)
            self._model = AutoModelForSeq2SeqLM.from_pretrained(model_path)
            self._model_loaded = True
            logger.info("T5 model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load T5 model: {e}. Using template fallback.")
            self._model_loaded = False
            
        try:
            torch.set_num_threads(4) 
        except Exception:
            pass


    def generate_questions_from_pattern(
        self, exam_pattern: Any, processed_data_dir: Optional[str] = None
    ) -> Dict[str, List[Dict[str, Any]]]:

        if processed_data_dir is None: processed_data_dir = str(PROCESSED_DATA_DIR)

        topic_mapping = self._load_json(os.path.join(processed_data_dir, "topic_chunk_mapping.json")) or {}

        if self._chunks_cache is None:
            self._chunks_cache = self._load_json(os.path.join(processed_data_dir, "textbook_chunks.json")) or []
            self._chunks_dict_cache = {c["chunk_id"]: c["text"] for c in self._chunks_cache}
        
        chunks_dict = self._chunks_dict_cache

        syllabus_topics = self._load_json(os.path.join(processed_data_dir, "selected_topics.json"))
        if not syllabus_topics:
            syllabus_topics = self._load_json(os.path.join(processed_data_dir, "syllabus_topics.json")) or {}

        self._load_model()
        generated_questions: Dict[str, List[Dict[str, Any]]] = {}
        seen_topics: Dict[str, set] = {}

        for part in exam_pattern.parts:
            part_qs = []
            if part.questions:
                for question in part.questions:
                    gq = self._generate_single_question(
                        question=question, part=part, topic_mapping=topic_mapping,
                        chunks_dict=chunks_dict, syllabus_topics=syllabus_topics, seen_topics=seen_topics,
                    )
                    part_qs.append(gq)
            generated_questions[part.part_name] = part_qs

        return generated_questions

    def _resolve_course_subject(self, syllabus_topics: Optional[Dict[str, Any]]) -> str:
        if not syllabus_topics: return "Computer Science"
        course_title = str(syllabus_topics.get("course_title", "")).strip()
        if not course_title or normalize_subject_name(course_title) in GENERIC_SUBJECT_NAMES:
            return "Computer Science"
        return course_title

    def _generate_single_question(
        self, question: Any, part: Any, topic_mapping: Dict, chunks_dict: Dict, syllabus_topics: Dict, seen_topics: Dict
    ) -> Dict[str, Any]:
        subject = self._resolve_course_subject(syllabus_topics)
        topic = self._get_random_topic(question.module, syllabus_topics, seen_topics.get(question.module))
        
        if question.module not in seen_topics: seen_topics[question.module] = set()
        seen_topics[question.module].add(topic)

        chunk_text = get_relevant_chunks(str(question.module), topic, topic_mapping, chunks_dict or {})
        has_sub_qs = hasattr(question, 'sub_questions') and question.sub_questions

        question_text = ""
        if not has_sub_qs:
            question_text = self._generate_with_bloom_retry(topic=topic, context=chunk_text, marks=question.marks, module=str(question.module), subject=subject)

        base_q = {
            "question_no": question.question_no, "marks": question.marks, "module": question.module,
            "text": question_text, "has_internal_choice": question.has_internal_choice,
            "source_chunk": chunk_text[:80] if chunk_text else None,
        }

        if question.has_internal_choice and getattr(question, 'or_choice', None):
            or_marks = getattr(question.or_choice, 'marks', question.marks)
            or_module = getattr(question.or_choice, 'module', question.module)
            has_or_sub_qs = bool(getattr(question.or_choice, 'sub_questions', None))

            or_topic = self._get_random_topic(or_module, syllabus_topics, seen_topics.get(or_module))
            if or_module not in seen_topics: seen_topics[or_module] = set()
            seen_topics[or_module].add(or_topic)

            or_chunk_text = get_relevant_chunks(or_module, or_topic, topic_mapping, chunks_dict or {})
            
            or_question_text = ""
            if not has_or_sub_qs:
                or_question_text = self._generate_with_bloom_retry(topic=or_topic, context=or_chunk_text, marks=or_marks, module=str(or_module), subject=subject)
            
            base_q["or_question"] = {
                "marks": or_marks, "module": or_module, "text": or_question_text,
                "source_chunk": or_chunk_text[:80] if or_chunk_text else None,
            }

            if has_or_sub_qs:
                or_sub_qs = []
                for sq in question.or_choice.sub_questions:
                    sq_t = self._get_random_topic(or_module, syllabus_topics, seen_topics.get(or_module))
                    seen_topics[or_module].add(sq_t)
                    sq_m = getattr(sq, 'marks', or_marks)
                    sq_c = get_relevant_chunks(or_module, sq_t, topic_mapping, chunks_dict or {})
                    if self._model_loaded: sq_text = self._generate_with_bloom_retry(sq_t, sq_c, sq_m, str(or_module), subject)
                    else: sq_text = self._generate_with_template(sq_t, sq_c, sq_m)
                    or_sub_qs.append({"label": getattr(sq, 'label', '?'), "marks": sq_m, "text": sq_text, "source_chunk": sq_c[:80] if sq_c else None})
                base_q["or_question"]["sub_questions"] = or_sub_qs

        if has_sub_qs:
            sub_qs = []
            for sq in question.sub_questions:
                sq_t = self._get_random_topic(question.module, syllabus_topics, seen_topics.get(question.module))
                seen_topics[question.module].add(sq_t)
                sq_m = getattr(sq, 'marks', question.marks)
                sq_c = get_relevant_chunks(question.module, sq_t, topic_mapping, chunks_dict or {})
                if self._model_loaded: sq_text = self._generate_with_bloom_retry(sq_t, sq_c, sq_m, str(question.module), subject)
                else: sq_text = self._generate_with_template(sq_t, sq_c, sq_m)
                sub_qs.append({"label": getattr(sq, 'label', '?'), "marks": sq_m, "text": sq_text, "source_chunk": sq_c[:80] if sq_c else None})
            base_q["sub_questions"] = sub_qs

        return base_q


    @staticmethod
    def _expected_bloom_for_marks(marks: int) -> str:
        if marks <= 2: return "Remember"
        elif marks <= 5: return "Understand"
        return "Analyze"

    def _generate_with_bloom_retry(self, topic: str, context: Optional[str], marks: int, module: str = "", subject: str = "Computer Science") -> str:
        if marks > 5:
            try: return self.generate_high_mark_question(topic=topic, chunks=[context] if context else [], marks=marks, subject=subject, module=module)
            except Exception as e:
                logger.warning(f"[HighMark] Routing failed: {e}")
                return self._generate_with_template(topic, context, marks=marks)

        if not self._model_loaded: return self._generate_with_template(topic, context, marks=marks)

        expected = self._expected_bloom_for_marks(marks)
        for attempt in range(2):
            q = self._generate_with_t5(topic, context, marks, expected if attempt == 1 else None)
            from app.services.bloom_service import bloom_service
            predicted = bloom_service.classify(q)
            if predicted == expected: return q
        return q

    def _generate_with_t5(self, topic: str, context: Optional[str], marks: int, bloom_override: Optional[str] = None) -> str:
        styles = [
            f"Write a question about '{topic}'.",
            f"Ask a factual question on '{topic}'.",
        ]
        prompt = f"{random.choice(styles)}\n\nContext: {context[:600] if context else ''}\n\nQuestion:"
        
        if bloom_override:
            verbs = BLOOM_VERBS.get(bloom_override, [])
            prompt += f"\nIMPORTANT: Require: {bloom_override}. Use verbs like: {', '.join(verbs)}"

        if not self._tokenizer or not self._model:
            return self._generate_with_template(topic, context, marks)

        inputs = self._tokenizer(prompt, return_tensors="pt", truncation=True, max_length=768)
        with torch.inference_mode():
            outputs = self._model.generate(
                **inputs, max_new_tokens=80, do_sample=True, temperature=0.5,
                top_k=50, top_p=0.90, repetition_penalty=1.2, no_repeat_ngram_size=3,
            )
        
        ans = self._tokenizer.decode(outputs[0], skip_special_tokens=True).strip()
        ans = re.sub(r"^(Question|Output|Answer)[\s]*:[\s]*", "", ans, flags=re.IGNORECASE).strip()
        if ans and not ans.endswith("?"):
            if ' ' in ans: ans = ans.rsplit(' ', 1)[0]
            ans += "?"

        ans = filter_hallucinations(ans)
        
        # Pass extract_topic_tokens as lambda or function reference
        return refine_with_ollama(ans, marks, topic, extract_topic_tokens)

    def _generate_with_template(self, topic: str, context: Optional[str], marks: Optional[int] = None) -> str:
        words = re.findall(r"[A-Za-z]+", context or "")
        terms = [w.lower() for w in set(words) if len(w) > 4 and w.lower() not in set(extract_topic_tokens(topic))][:2]
        related = ", ".join(terms)

        if marks and marks <= 3: return f"What is {topic}, and how is it related to {related}?" if related else f"What is {topic}?"
        if marks and marks <= 5: return f"Explain {topic} with reference to {related}." if related else f"Explain how {topic} works."
        return f"Discuss {topic} in detail with reference to {related}." if related else f"Discuss {topic} in detail."

    def _get_random_topic(self, module: str, syllabus_topics: Optional[Dict], exclude_topics: Optional[set] = None) -> str:
        if not syllabus_topics: return module
        modules = syllabus_topics.get("modules", syllabus_topics)
        matched_key = find_matching_key(module, modules.keys())

        if matched_key:
            val = modules[matched_key]
            topics = val.get("topics", []) if isinstance(val, dict) else (val if isinstance(val, list) else [])
            if topics:
                available = [str(t) for t in topics if t not in (exclude_topics or set())]
                return random.choice(available if available else topics)
        return module


question_service = QuestionService()

```

### `backend/app/services/syllabus_service.py`

```py
"""
Syllabus Service — parse syllabus PDFs to extract module-wise topics.

Responsibility:
- Delegate metadata extraction (title, code, outcomes) to utils.
- Extract text from syllabus PDFs using ingestion service.
- Parse module headings and run semantic topic extraction via Mistral.
- Return structured module → topics mapping.
"""

import re
import logging
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from app.services.ingestion_service import extract_syllabus_raw
from app.core.config import OLLAMA_BASE_URL, LLM_MODEL

from app.utils.syllabus_extractors import (
    extract_course_title,
    extract_course_code,
    extract_course_outcomes
)

logger = logging.getLogger(__name__)


def extract_syllabus_text(pdf_bytes: bytes) -> str:
    """Extract text content from a syllabus PDF."""
    text = extract_syllabus_raw(pdf_bytes)
    logger.debug(f"Syllabus text length: {len(text)}")
    return text


# =====================================================
# Semantic Topic Extraction via Mistral
# =====================================================

class SyllabusTopicsList(BaseModel):
    topics: List[str] = Field(description="List of substantive technical topics extracted from the module")


def _extract_topics_from_module_text(module_text: str) -> List[str]:
    """Semantic extraction of topics using a local Mistral model via Ollama."""
    try:
        llm = ChatOllama(
            base_url=OLLAMA_BASE_URL,
            model=LLM_MODEL,
            temperature=0.0
        )
        parser = JsonOutputParser(pydantic_object=SyllabusTopicsList)
        prompt = PromptTemplate(
            template="""You are an expert academic taxonomy parser parsing a university syllabus.
Your task is to extract a clean, substantive list of topics from the provided raw text for a single syllabus module.

Rules:
1. Preserve technical terms and hyphenated names (e.g. keep "Diffie-Hellman" and "SHA-1" and "Secure e-mail" intact).
2. If a topic is listed as a sub-attribute (like "Characteristics", "Advantages", "Technical Description") of a parent technology, prefix it with the parent name (e.g. "Fingerprint Scanner Characteristics" instead of just "Characteristics").
3. Omit any administrative noise (e.g. "course outcomes", "12 marks", "students will learn").
4. Formulate the topics perfectly capitalized and ready to be used as embeddings for semantic search.
5. Return the result strictly in valid JSON matching the format instructions.

Format Instructions:
{format_instructions}

Raw Module Text:
"{text}"
""",
            input_variables=["text"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )
        chain = prompt | llm | parser

        logger.info("[Semantic Extractor] Initiating LLM syllabus parsing...")
        result = chain.invoke({"text": module_text})
        
        extracted_topics = []
        if isinstance(result, dict):
            extracted_topics = result.get("topics", [])
        elif isinstance(result, list):
            extracted_topics = result
        else:
            logger.warning(f"[Semantic Extractor] Unexpected response type: {type(result)}")
            
        logger.info(f"[Semantic Extractor] Successfully extracted {len(extracted_topics)} topics")
        return extracted_topics

    except Exception as e:
        logger.error(f"[Semantic Extractor] LLM generation failed: {e}")
        logger.warning("[Semantic Extractor] Falling back to returning full module block.")
        return [module_text.strip()]


def extract_module_topics(text: str) -> Dict[str, List[str]]:
    """Parse syllabus text to extract module-wise topics with context-aware parent-prefix grouping."""
    ignore_keywords = [
        "course outcome", "course outcomes", "edition",
        "publisher", "textbook", "syllabus", "marks",
        "on completion", "student will be able",
    ]

    lines = text.split("\n")
    logger.debug(f"Total syllabus lines: {len(lines)}")

    module_lines: Dict[str, List[str]] = {}
    current_module: Optional[str] = None

    for line in lines:
        line = line.strip()

        if line.lower().startswith("references"):
            logger.debug("Stopped parsing at References")
            break

        match = re.match(r"Module\s+([IVX0-9]+|[0-9]+)", line, re.IGNORECASE)
        if match:
            current_module = f"Module {match.group(1)}"
            module_lines[current_module] = []
            logger.debug(f"Found module: {current_module}")
            remainder = line[match.end():].strip()
            if remainder and len(remainder) > 5:
                module_lines[current_module].append(remainder)
            continue

        if not current_module or len(line) < 5:
            continue

        lower_line = line.lower()
        if any(kw in lower_line for kw in ignore_keywords):
            continue

        module_lines[current_module].append(line)

    modules: Dict[str, List[str]] = {}

    for module_name, raw_lines in module_lines.items():
        full_text = " ".join(raw_lines)
        topics = _extract_topics_from_module_text(full_text)
        modules[module_name] = [t for t in topics if len(t.strip()) > 3]

    if not modules:
        logger.warning("No explicit module headings found. Using generic topic grouping.")
        all_lines = []
        for line in lines:
            line = line.strip()
            if line.lower().startswith("references"):
                break
            if len(line) < 5:
                continue
            lower_line = line.lower()
            if any(kw in lower_line for kw in ignore_keywords):
                continue
            all_lines.append(line)
        full_text = " ".join(all_lines)
        topics = _extract_topics_from_module_text(full_text)
        modules["General Topics"] = [t for t in topics if len(t.strip()) > 3]

    logger.debug(f"Extracted {len(modules)} modules")
    return modules


def build_embedding_ready_text(topics: List[str]) -> str:
    """Create a cleaned, normalized text string from topics for semantic search."""
    combined = " ".join(topics)
    combined = re.sub(r"[^\w\s]", " ", combined)
    combined = re.sub(r"\s+", " ", combined).strip()
    return combined.title()


def build_structured_syllabus(text: str, modules: Dict[str, List[str]]) -> Dict:
    """Build the full structured syllabus output containing course metadata, modules with topics."""
    course_title = extract_course_title(text)
    course_code = extract_course_code(text)
    course_outcomes = extract_course_outcomes(text)

    structured_modules = {}
    for module_name, topics in modules.items():
        raw_text = ", ".join(topics)
        embedding_ready = build_embedding_ready_text(topics)
        structured_modules[module_name] = {
            "raw_text": raw_text,
            "topics": [t.strip().title() for t in topics],
            "embedding_ready_text": embedding_ready,
        }

    return {
        "course_title": course_title,
        "course_code": course_code,
        "course_outcomes": course_outcomes,
        "modules": structured_modules,
    }

```

### `backend/app/services/ingestion_service.py`

```py
"""
Ingestion Service — PDF text extraction with OCR fallback.

Responsibilities:
- Extract text from uploaded PDFs using PyMuPDF
- Fall back to OCR (Tesseract) for scanned/image-based PDFs
- Validate extracted text quality
- Clean noise from extracted text (TOC, page numbers, preface, etc.)
"""

import re
import logging
from typing import List, Tuple
from collections import Counter

from app.utils.pdf_utils import extract_full_text, extract_text_by_page, is_valid_extracted_text
from app.core.config import TESSERACT_CMD, POPPLER_PATH

logger = logging.getLogger(__name__)

# =====================================================
# Section headers that signal end-of-content
# =====================================================
_STOP_HEADERS = re.compile(
    r"^\s*(references|bibliography|index|appendix\s+[a-z]?\s*$)",
    re.IGNORECASE,
)

# =====================================================
# Noise patterns
# =====================================================
_TOC_DOTS = re.compile(r"^.*\.{5,}.*$")            # Lines with ".........."
_STANDALONE_NUMBER = re.compile(r"^\s*\d{1,4}\s*$") # Isolated page numbers
_SECTION_PREFIXES = re.compile(
    r"^\s*(preface|foreword|acknowledgements?|table\s+of\s+contents|about\s+the\s+author)",
    re.IGNORECASE,
)


def clean_extracted_text(text: str) -> str:
    """
    Remove noise from extracted PDF text.

    Rules applied (from aqpg_final_upgrade_plan.md):
    - Drop TOC lines (lines with ".....")
    - Drop standalone page numbers
    - Drop lines < 5 words
    - Stop parsing at "References" / "Index" / "Bibliography"
    - Remove repeated header lines (appearing > 3 times)
    - Merge broken lines (line doesn't end with punctuation + next starts lowercase)
    """
    lines = text.split("\n")

    # ---- Pass 1: detect repeated headers ----
    stripped_counts = Counter(line.strip() for line in lines if line.strip())
    repeated_headers = {
        line for line, count in stripped_counts.items()
        if count > 3 and len(line.split()) < 10
    }

    # ---- Pass 2: filter lines ----
    cleaned_lines: List[str] = []
    for line in lines:
        stripped = line.strip()

        # Stop at reference/index sections
        if _STOP_HEADERS.match(stripped):
            logger.info(f"[Noise Removal] Stopped at section header: '{stripped}'")
            break

        # Skip TOC dot-leader lines
        if _TOC_DOTS.match(stripped):
            continue

        # Skip standalone page numbers
        if _STANDALONE_NUMBER.match(stripped):
            continue

        # Skip section prefixes (preface, TOC header, acknowledgements)
        if _SECTION_PREFIXES.match(stripped):
            continue

        # Skip repeated headers
        if stripped in repeated_headers:
            continue

        # Skip lines with fewer than 5 words
        if len(stripped.split()) < 5:
            continue

        cleaned_lines.append(stripped)

    # ---- Pass 3: merge broken lines ----
    merged: List[str] = []
    for line in cleaned_lines:
        if (
            merged
            and merged[-1]
            and merged[-1][-1] not in ".?!:;\""
            and line
            and line[0].islower()
        ):
            # Join with previous line
            merged[-1] = merged[-1] + " " + line
        else:
            merged.append(line)

    result = "\n".join(merged)
    logger.info(
        f"[Noise Removal] {len(lines)} raw lines → {len(merged)} cleaned lines"
    )
    return result


def extract_text(pdf_bytes: bytes) -> str:
    """
    Extract text from a PDF, falling back to OCR if the PyMuPDF
    extraction yields low-quality or insufficient text.

    Args:
        pdf_bytes: Raw bytes of the uploaded PDF.

    Returns:
        Extracted text content.
    """
    # Try PyMuPDF first (fast, works on text-based PDFs)
    text = extract_full_text(pdf_bytes)

    if is_valid_extracted_text(text):
        logger.info("Text extracted successfully via PyMuPDF")
        return clean_extracted_text(text)

    # Fallback to OCR for scanned PDFs
    logger.info("PyMuPDF text insufficient — falling back to OCR")
    return clean_extracted_text(_ocr_extract(pdf_bytes))


def extract_pages(pdf_bytes: bytes) -> List[Tuple[int, str]]:
    """
    Extract text page-by-page with page number metadata.

    Args:
        pdf_bytes: Raw bytes of the uploaded PDF.

    Returns:
        List of (page_number, page_text) tuples.
    """
    raw_pages = extract_text_by_page(pdf_bytes)
    # Clean each page individually
    cleaned_pages = []
    for page_num, page_text in raw_pages:
        cleaned = clean_extracted_text(page_text)
        if cleaned.strip():
            cleaned_pages.append((page_num, cleaned))
    return cleaned_pages


def _ocr_extract(pdf_bytes: bytes) -> str:
    """
    Perform OCR on a PDF using Tesseract + pdf2image.
    Only called when PyMuPDF extraction fails quality checks.
    """
    try:
        import pytesseract
        from pdf2image import convert_from_bytes

        pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD

        convert_kwargs = {"dpi": 200}
        if POPPLER_PATH:
            convert_kwargs["poppler_path"] = POPPLER_PATH

        images = convert_from_bytes(pdf_bytes, **convert_kwargs)

        ocr_text = ""
        for i, img in enumerate(images):
            logger.debug(f"OCR processing page {i + 1}/{len(images)}")
            ocr_text += pytesseract.image_to_string(img, lang="eng") + "\n"

        return ocr_text

    except ImportError:
        logger.warning(
            "pytesseract or pdf2image not installed. "
            "OCR fallback unavailable — returning raw PyMuPDF text."
        )
        return extract_full_text(pdf_bytes)
    except Exception as e:
        logger.error(f"OCR extraction failed: {e}")
        return extract_full_text(pdf_bytes)


def extract_syllabus_raw(pdf_bytes: bytes) -> str:
    """
    Extract text from a syllabus PDF WITHOUT noise removal.

    The syllabus service has its own filtering (course outcomes, ignore keywords)
    in extract_module_topics(). Applying the textbook noise cleaner here would
    destroy short topic lines like 'Iris Scan', 'Palm Print', etc.

    Args:
        pdf_bytes: Raw bytes of the syllabus PDF.

    Returns:
        Raw extracted text content.
    """
    text = extract_full_text(pdf_bytes)

    if is_valid_extracted_text(text):
        logger.info("Syllabus text extracted successfully via PyMuPDF (raw)")
        return text

    logger.info("PyMuPDF text insufficient for syllabus — falling back to OCR")
    return _ocr_extract(pdf_bytes)

```

