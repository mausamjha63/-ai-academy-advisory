# Development Log

## Phase 1: Foundation Setup

### Date: 2026-09-13
**Development Step:** Initialize Project Structure and Django Foundation
**What was implemented:**
- Created the root directory `AI_Academic_Advisor`
- Set up a virtual environment and installed initial dependencies (Django, pandas, openpyxl, pypdf, python-dotenv, chromadb, google-genai).
- Initialized Django project `config` and core apps: `core`, `students`, `academics`, `advisor`, `rag`, `evaluation`.
- Prepared the directory structure for docs and source data.

**Files changed:**
- Created `/docs/DEVELOPMENT_LOG.md`
- Created `/requirements.txt`, `/.env.example`, `/.env`
- Configured `/config/settings.py` for apps, static files, and environment variables
- Created `core/urls.py` and `config/urls.py`
- Defined database models in `academics/models.py` and `students/models.py`
- Setup admin interface in `academics/admin.py` and `students/admin.py`
- Built initial UI in `templates/base.html`, `templates/core/dashboard.html`, `templates/core/health.html`
- Wrote tests in `core/tests.py`
- Created `README.md`

**Technology/architecture decisions:**
- Created modular Django apps in `apps/` directory (`core`, `academics`, `students`, `advisor`, `rag`, `evaluation`).
- Adjusted `sys.path` in `settings.py` for clean app imports.
- SQLite is set for initial local development as requested, but `Course` and `Student` structures are extensible.
- UI styling utilizes TailwindCSS for a quick, glassmorphic professional base.

**Problems encountered:**
- Initial app module loading failed because `django-admin startapp` inside `apps/` without matching name caused an `ImproperlyConfigured` exception.
**Fixes applied:**
- Manually fixed `apps.py` inside `academics` and `students` to set correct module names. Added `apps` to Python path.
**Tests performed:** 
- Successfully applied all Django migrations.
- Ran `python manage.py test core`, which passed all 2 tests (Dashboard and Health Check page render checks).
**Current status:** Completed (Phase 1)
**Next step:** Await Phase 2 start for data ingestion.

---
### Phase 2: Core Data Ingestion & Advisor Architecture
**Date:** 2026-09-13

**Files changed:**
- `rag/models.py`, `rag/admin.py`: Created `AcademicDocument` and `DocumentChunk`
- `academics/management/commands/import_academic_data.py`: Added idempotent Excel data ingestion logic using pandas.
- `rag/management/commands/build_rag_index.py`: Added PDF parsing using `pypdf` and ChromaDB persistent storage integration.
- `students/management/commands/load_synthetic_students.py`: Fixture loader for synthetic students.
- `advisor/services/...`: Implemented `AcademicDataService`, `RetrievalService`, `DecisionEngine`, and `AdvisorService`.
- `advisor/views.py`, `advisor/urls.py`, `templates/advisor/chat.html`: Implemented a modern advisor interface with evidence side panel.
- `academics/tests.py`, `advisor/tests.py`, `rag/tests.py`: Extensive unit tests.

**Technology/architecture decisions:**
- Used ChromaDB for local persistent vector storage to avoid external API dependency for local dev testing.
- Separated RAG orchestration, deterministic logical checks (DecisionEngine), and generative synthesis to prevent LLM hallucination and ensure accurate decisions based solely on source data.
- Built a UI mimicking a professional university portal.

**Current status:** Completed (Phase 2)
**Next step:** Ready for user review of Phase 2 core logic.

---
### Phase 2: Corrective Pass
**Date:** 2026-09-13

**Changes:**
- Expanded synthetic profiles from 4 to 10 diverse cases including complete, incomplete, missing history, passed and failed prerequisites (`load_synthetic_students.py`).
- Integrated a deterministic conflict checking logic within `DecisionEngine.check_prerequisite_eligibility` that returns `CONFLICTING_INFORMATION` when authoritative sources disagree on prerequisites.
- Demonstrated robust RAG chunk querying from persistent ChromaDB matching 5 exact real test cases.
- Validated `AdvisorService` stripping punctuation properly for robust SQL course lookups.
- Passed full Django test suite (`python manage.py test`) including conflict simulations and all edge cases.

**Current status:** Verified (Phase 2 Corrective Pass)
**Next step:** Await user approval for Phase 3.

---
### Phase 3: Prompt Engineering & Grounded Advisor Quality
**Date:** 2026-09-13

**Changes:**
- Implemented four distinct prompt engineering strategies (V1-V4) in `apps/advisor/prompts/`.
- Updated `AdvisorService` to enforce structured JSON adherence and intercept LLM state modifications, ensuring the deterministic `DecisionEngine` remains perfectly authoritative.
- Added prompt-injection robustness rules for edge-case filtering and out-of-scope querying.
- Redesigned `chat.html` to visually render structured response properties with state-bound badging aligned with the university portal aesthetic constraints.
- Generated `docs/prompt_engineering.md` to document implementation differences and grounding approaches.
- Mocked Gemini validation pipelines within `apps/advisor/tests_prompts.py` achieving 100% test pass rates across Django suite.

**Current status:** Completed and Verified (Phase 3)
**Next step:** Await explicit user approval to commence Phase 4 formal evaluation.

---
### Phase 4: Formal Evaluation & Measurement
**Date:** 2026-09-13

**Changes:**
- Generated `evaluation/phase4_cases.json`, a 25-case Gold Dataset explicitly mapping questions to expected states, sources, and missing information.
- Authored a dynamic test runner: `apps/evaluation/management/commands/run_phase4_evaluation.py`.
- Conducted the four-stage comparison isolated test against V1 (Basic LLM), V2 (Structured), V3 (RAG Grounded), and V4 (RAG + Structured Data).
- Documented methodology, deterministic/semantic boundaries, metrics computation, and mock status inside `docs/PHASE_4_FINAL_REPORT.md`.
**Current status:** Completed and Verified (Phase 4 - MOCK/STRUCTURAL EVALUATION)
**Next step:** Await Phase 5.

---
### Phase 5: Compare / Analyze
**Date:** 2026-09-13

**Changes:**
- Created `apps/evaluation/management/commands/run_phase5_analysis.py` to securely parse and calculate comparative structural metrics from `phase4_results.json` without mutating the data.
- Generated `evaluation/results/phase5_comparison.json`.
- Wrote `docs/PHASE_5_FINAL_REPORT.md` exploring architectural findings, missing-information intercept handling, and mock fallback limitations mapping V1 through V4.
- Added comprehensive analysis testing via `apps/evaluation/tests_analysis.py`.
- Preserved the Gemini Live Semantic Evaluation pending limitation securely throughout the reporting phase.

**Current status:** Completed and Verified (Phase 5)
**Next step:** Project complete. Wait for further instructions.

---
### Phase 6: Real Gemini Semantic Evaluation
**Date:** 2026-09-14

**Changes:**
- Integrated live `gemini-3.6-flash` API, replacing mock structural generation.
- Hardened deterministic Scope Gate preventing unnecessary LLM invocation for out-of-scope and greeting queries.
- Ensured authoritative mapping where `DecisionEngine` strictly overrides any LLM hallucinations regarding eligibility.
- Built a robust 503 fallback intercept intercepting Gemini High Demand errors without crashing the backend or exposing stack traces.
- Finalized architecture restricting LLM answers exclusively to provided RAG contexts and structured data feeds.
- Documented final verified configurations inside `docs/GEMINI_ADVISOR_ARCHITECTURE.md`.

**Current status:** Verified implementation of Real Gemini API. (Phase 6)
**Next step:** Await further instructions.
