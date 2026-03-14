# Frontend (`frontend/`)

> **For developers & agents:** This document covers the entire React frontend — entry points, all components, styling, and how it communicates with the backend.

---

## Directory Overview

```
frontend/
├── package.json               # Dependencies, scripts
├── public/
│   ├── index.html             # HTML shell
│   └── favicon.ico
└── src/
    ├── index.js               # React root render
    ├── index.css              # Minimal (intentionally empty)
    ├── App.js                 # Main app component + state + API handlers
    ├── App.css                # Full design system (577 lines)
    └── components/
        ├── Stepper.js         # 5-step progress indicator
        ├── SyllabusUpload.js  # Step 1: upload syllabus PDF
        ├── TextbookUpload.js  # Step 2: upload textbook PDF
        ├── SemanticMapping.js # Step 3: trigger SBERT mapping
        ├── PatternConfig.js   # Step 4: exam pattern configuration
        └── GeneratedQuestions.js # Step 5: display generated questions
```

**Tech stack:** React 19, Create React App, vanilla CSS.  
**No routing library** — single-page app with step-based navigation.

---

## Entry Points

### `index.js`
Standard React 18+ entry point. Renders `<App />` wrapped in `<React.StrictMode>`.

### `index.css`
Intentionally minimal — contains only a comment. All styling lives in `App.css`.

### `public/index.html`
Standard CRA HTML shell. Title: `"React App"` (should be updated to `"AQPG"` if deployed).

---

## `App.js` — Main Application Component

The root component that manages all application state, API communication, and step navigation.

### State Variables

| State | Type | Purpose |
|-------|------|---------|
| `step` | `number` (1–5) | Current active step |
| `topics` | `object \| null` | Extracted syllabus topics from API |
| `syllabusLoading` | `boolean` | Loading indicator for syllabus upload |
| `chunkCount` | `number` | Number of chunks created from textbook |
| `textbookLoading` | `boolean` | Loading indicator for textbook upload |
| `examName` | `string` | User-entered exam name |
| `parts` | `Array<PartPattern>` | Exam parts configuration |
| `expandedParts` | `Array<number>` | Indices of expanded parts in UI |
| `patternLoading` | `boolean` | Loading indicator for pattern save |
| `generationLoading` | `boolean` | Loading indicator for question generation |
| `generatedQuestions` | `object \| null` | Generated questions from API |
| `generationError` | `string \| null` | Error message from generation |

### API Communication

All API calls use the `fetch` API. Base URL:
```js
const API_BASE_URL = process.env.REACT_APP_API_URL || "http://127.0.0.1:8000";
```

| Handler | Endpoint | Method | Content Type |
|---------|----------|--------|--------------|
| `uploadSyllabus(e)` | `/extract-syllabus` | POST | `multipart/form-data` |
| `uploadTextbook(e)` | `/chunk-textbook` | POST | `multipart/form-data` |
| `savePattern()` | `/set-question-pattern` | POST | `application/json` |
| `generateQuestions()` | `/generate-questions` | POST | `application/json` |

> **Agent note:** `SemanticMapping.js` has its own API call to `/semantic-mapping` (not handled in `App.js`). It defines its own `API_BASE_URL`.

### Step Flow

```
Step 1: SyllabusUpload  → uploads PDF → shows extracted topics → "Continue"
Step 2: TextbookUpload  → uploads PDF → shows chunk count → "Continue"
Step 3: SemanticMapping  → triggers SBERT mapping → shows results → "Continue"
Step 4: PatternConfig    → configure exam pattern → "Generate Questions"
Step 5: GeneratedQuestions → displays generated questions
```

### `defaultPattern()` — Factory Function

Creates a default exam paper pattern configured automatically for standard university rules:
- **Part A:** 8 questions, Answer ALL, 3 marks each.
- **Part B:** 4 questions, Answer ALL, 12 marks each, grouped by **Internal Choice (OR)**.
- Pre-fills modules using Roman numerals (`"Module I"`, `"Module II"`, etc.).

---

## Components

### `Stepper.js`

A 5-step horizontal progress indicator.

| Prop | Type | Description |
|------|------|-------------|
| `currentStep` | `number` | Currently active step (1–5) |
| `onStepClick` | `function` | Callback when user clicks a step |

**Steps displayed:**
1. Upload Syllabus
2. Upload Textbook
3. Semantic Mapping
4. Configure Pattern
5. Generate Questions

Steps show a checkmark (✓) when completed, a highlighted circle when active, and a muted circle when future.

---

### `SyllabusUpload.js` (Step 1)

Handles syllabus PDF upload and displays extracted module-wise topics.

| Prop | Type | Description |
|------|------|-------------|
| `topics` | `object \| null` | API response containing `{ modules: { "Module 1": ["topic1", ...] } }` |
| `syllabusLoading` | `boolean` | Show loading state |
| `onUpload` | `function` | File input change handler |
| `onNext` | `function` | Navigate to step 2 |

**Renders:** File upload button → loading text → module grid (module badges + topic lists) → "Continue" button.

---

### `TextbookUpload.js` (Step 2)

Handles textbook PDF upload and displays the resulting chunk count.

| Prop | Type | Description |
|------|------|-------------|
| `chunkCount` | `number` | Number of chunks created |
| `textbookLoading` | `boolean` | Show loading state |
| `onUpload` | `function` | File input change handler |
| `onNext` | `function` | Navigate to step 3 |

**Renders:** File upload button → loading text → chunk count badge → "Continue" button.

---

### `SemanticMapping.js` (Step 3)

Triggers the SBERT semantic mapping and displays results. **This component manages its own API call** (unlike other components which delegate to `App.js`).

| Prop | Type | Description |
|------|------|-------------|
| `onNext` | `function` | Navigate to step 4 |

**Internal state:** `loading`, `mapping`, `error`.

**API call:** `POST /semantic-mapping` — called when user clicks "Run Semantic Mapping".

**Renders:** Run button → loading state → stats (topics mapped, chunks linked) → mapping results (up to 8 topics shown, each with chunk tags showing chunk ID and similarity %). → "Continue" button.

---

### `PatternConfig.js` (Step 4)

Complex form for configuring the exam pattern. This is the most interactive component.

| Prop | Type | Description |
|------|------|-------------|
| `examName` / `setExamName` | `string` / setter | Exam name |
| `parts` / `setParts` | `Array` / setter | Exam parts array |
| `expandedParts` / `setExpandedParts` | `Array` / setter | Expanded parts state |
| `patternLoading` | `boolean` | Save loading state |
| `onSavePattern` | `function` | Save pattern handler |
| `onGenerateQuestions` | `function` | Generate questions handler |
| `generationLoading` | `boolean` | Generation loading state |
| `generationError` | `string \| null` | Generation error |
| `availableModules` | `Array` | List of actual modules parsed from the syllabus |

**Constants:**
```js
const MODULES = availableModules || ["Module I", "Module II", "Module III", "Module IV"];
```

> **Agent note:** The `MODULES` array correctly defaults to Roman numerals matching the syllabus parser output. This fixes prior context bleeding issues.

**Features:**
- Summary bar showing total questions and marks (with total M calculation).
- Exam name text input.
- Expandable per-part blocks with individual name and "Answer ALL/ANY" configuration.
- Per-question configuration: marks, module dropdown, and an **Internal Choice (OR) Toggle**.
- *OR Choice Sub-panel:* If toggled, shows a secondary module and marks selector to generate the alternative internal choice question `or_choice`.
- Add/remove questions per part (auto-numbered array mapping).
- Action buttons: + Add Part, 💾 Save Pattern, 🚀 Generate Questions.

---

### `GeneratedQuestions.js` (Step 5)

Displays the final generated questions grouped by exam part and provides a PDF export option.

| Prop | Type | Description |
|------|------|-------------|
| `questions` | `object \| null` | `{ "PART A": [question_dicts], "PART B": [...] }` |

**Per question, displays:**
- Main question text with inline brackets `[Bloom's Level: ...]`.
- `.gen-q-footer`: On-screen visually appealing colored tags (Bloom level, module) and a marks pill. These tags are hidden during print via `.no-print`.
- **OR blocks:** If the question has an internal choice, a `— OR —` divider separates the primary question from its generated sibling. Both siblings display their separate context tags and marks.
- Print-only CSS layout to ensure clean formatting when printed.

Returns `null` if no questions are present.

---

## `App.css` — Design System

Complete design system in a single CSS file (944 lines). Key design characteristics:

| Aspect | Detail |
|--------|--------|
| **Theme** | Dark glassmorphic — dark indigo background, translucent cards |
| **Font** | Inter (system font stack fallback) |
| **Layout** | Max-width 960px, centered |
| **Colors** | Purple/indigo gradients, green for success, amber/yellow for accents |
| **Print Output** | `@media print` rules strip backgrounds and set black text format suitable for PDF generation. Classes `.no-print`, `.print-only`. |
| **Responsive** | Mobile breakpoint at 640px |

### CSS Architecture

| Section | Class Prefix | Purpose |
|---------|-------------|---------|
| Reset & Base | `body, *` | Box-sizing reset, background gradient |
| App Layout | `.app`, `.app-header` | Centered layout, gradient title |
| Stepper | `.stepper-*` | Step indicators with active/done states |
| Cards | `.card`, `.card-title` | Glassmorphic content containers |
| Buttons | `.upload-btn`, `.btn`, `.btn-sm` | Color variants: blue, purple, green, amber, indigo, red |
| Semantic Mapping | `.mapping-*`, `.stat-pill`, `.chunk-tag` | Mapping results display |
| Pattern Config | `.part-block`, `.question-row`, `.or-choice-panel` | Part and question config UI (including indented OR panel) |
| Generated Questions | `.generated-card`, `.gen-*`, `.tag` | Final output display with colored tags and clean PDF layouts |
| Responsive | `@media (max-width: 640px)` | Mobile-friendly adjustments |

---

## Agent Notes

- **No state management library** — all state lives in `App.js` via `useState`. This is fine for the current scale but would need React Context or a state manager (Zustand, Redux) if the app grows.
- **No error boundaries** — unhandled component errors will crash the entire app.
- **API URL is configurable** via `REACT_APP_API_URL` environment variable.
- **PDF Export:** Triggered via `window.print()` leveraging the `@media print` CSS block.
- Scripts: `npm start` (dev server on port 3000), `npm run build` (production build), `npm test` (jest).
