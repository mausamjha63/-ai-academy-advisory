# AI Academic Advisor

AI Academic Advisor — University Academic Decision-Support System

## Project Purpose
This project is an AI-powered academic advisor that acts as a decision-support system for a university. It uses provided structured academic data (course offerings, prerequisites) and RAG (policies, handbook) to answer student queries, explain decisions, and provide direct evidence/provenance for its reasoning.

## Assignment Scope
This repository implements **Assignment #1 Only**. 
It focuses on the baseline, structured data, RAG implementation, decision logic, and comprehensive evaluation. Assignment #2 features (multimodal, real-time university API hooks, complex autonomous agents) are explicitly excluded from this phase.

## Architecture
- **Framework**: Django (Python 3)
- **Database**: SQLite (Development) / PostgreSQL (Production)
- **AI/LLM**: Google Gemini API via standard SDK
- **Vector DB**: ChromaDB for local document embedding storage
- **Data Ingestion**: pandas, openpyxl, pypdf

## Setup Instructions

1. Clone the repository and navigate into the `AI_Academic_Advisor` folder.
2. Create and activate a Python virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create your `.env` file (copy `.env.example`):
   ```bash
   cp .env.example .env
   ```
   *Edit `.env` to include your valid `SECRET_KEY` and `GEMINI_API_KEY`.*

5. Run migrations:
   ```bash
   python manage.py migrate
   ```

## Running the Application
To run the local Django development server:
```bash
python manage.py runserver
```
Visit `http://localhost:8000` to access the Dashboard.
Visit `http://localhost:8000/health/` for system health check.

## Testing & Evaluation (Phase 4)

To run the automated test suite:
```bash
python manage.py test core
```

## Testing & Evaluation (Phase 4 & Phase 5)

To formally evaluate the AI Academic Advisor using the structured 25-case dataset against all 4 prompt configurations (V1-V4), run the Phase 4 Evaluation Runner:

```bash
python manage.py run_phase4_evaluation
```

### Phase 4 Evaluation Output
The evaluation runner isolates test contexts (e.g., hiding RAG or Student Data) and calculates formal metrics under a **MOCK/FALLBACK structural evaluation**:
- Overall Accuracy
- Hallucination Classification Rate
- Missing-Information Correct Hits
- Average Response Time

Results are stored structurally in `evaluation/results/phase4_results.json`.

### Phase 5 Comparative Analysis
To calculate structural architecture breakdown across approaches without rerunning the heavy LLM pipeline, run the Phase 5 analysis:
```bash
python manage.py run_phase5_analysis
```
Results mapping the configurations are saved to `evaluation/results/phase5_comparison.json`. A deep dive architectural report is located at `docs/PHASE_5_FINAL_REPORT.md`.

**Note:** If the `GEMINI_API_KEY` is not present, the evaluation pipeline falls back to **MOCKED** semantic execution. The resulting scores evaluate solely the architectural routing, deterministic evaluation overrides, and context extraction mapping. They are NOT live Gemini semantic performance metrics.

## Current Status
**Phase 1 Completed:** Base Django project foundation, UI templates, model definitions, and database migrations are operational.
**Phase 2 Completed:** The core AI Academic Advisor logic is implemented:
- Full PDF RAG pipeline indexing the Student Handbook and SOPs (via ChromaDB).
- Idempotent Excel ingestion loading Structured Courses, Offerings, and Prerequisites.
- Deterministic Decision Engine to handle ELIGIBLE/NOT_ELIGIBLE and MISSING_INFORMATION states.
- Advisor service connecting RAG, Structured Data, and LLM via Gemini API.
- Fully-featured chat interface displaying Grounded Answers alongside Source Evidence.
