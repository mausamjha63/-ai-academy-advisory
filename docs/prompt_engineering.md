# Prompt Engineering Strategy

This document outlines the prompt engineering strategies utilized in the AI Academic Advisor. Four distinct, programmatically selectable prompts were built to enforce structured JSON output, prevent hallucination, and expose authoritative university rules.

## Prompt Versions

### V1 — Basic Academic Advisor (`v1_basic.py`)
**Purpose:** Establishes a conversational baseline. 
**Design:** Simple instructions telling the model to "not invent facts" and to "be concise." It tests if the LLM can naturally conform to a structured JSON output without heavy constraint mapping.

### V2 — Structured Academic Advisor (`v2_structured.py`)
**Purpose:** Enforces structured roles and precise formatting.
**Design:** Breaks the prompt into explicit components (`ROLE`, `TASK`, `RULES`, `OUTPUT FORMAT`). Constrains the LLM to populate specific JSON schema fields and rigidly reject out-of-format responses.

### V3 — RAG Grounded Advisor (`v3_rag_grounded.py`)
**Purpose:** Intensive hallucination prevention and citation tracking.
**Design:** Includes explicit guardrails against inventing references or silently resolving conflicting texts. Demands differentiation between "SUPPORTED BY SOURCE" and "NOT ESTABLISHED BY SOURCE".

### V4 — Full Academic Advisor (`v4_full_academic.py`) [DEFAULT]
**Purpose:** Production-grade prompt blending semantic generation with absolute deterministic logic.
**Design:** Integrates structured SQL database information, RAG evidence, synthetic `student_data`, and absolute deterministic states from the `DecisionEngine`. Explicitly forbids the LLM from mutating the predefined deterministic states (e.g. `NOT_ELIGIBLE`), tasking the LLM only with synthesizing explanatory reasoning.

## Grounding Strategy & Structured Output
The prompt schemas are built on top of a foundational JSON structure modeled after a Pydantic contract (`AdvisorResponse`). The required fields are:
- `state`: e.g. `ELIGIBLE`, `NEEDS_MORE_INFORMATION`
- `answer`: Generative textual response.
- `reason`: Evaluated constraint rationale.
- `missing_information`: Explicit missing fields required to calculate eligibility.
- `evidence`: Verified, extracted citation filenames.
- `recommendation`: Actionable student guidance.
- `uncertainty`: Explanations of conflicts.

## Decision Engine vs LLM Separation
The system architecture mandates that the **Decision Engine** is the sole authoritative source of student eligibility. If the Decision Engine returns `NOT_ELIGIBLE` due to a failed prerequisite, the LLM is barred from generating an `ELIGIBLE` state. The `AdvisorService` intercepts and overrides any LLM deviations, preserving the safety of the academic domain.

## Missing Information & Conflicts
When a student profile is incomplete, the system natively returns `NEEDS_MORE_INFORMATION`. The LLM is directed to prompt the user strictly for the isolated missing fields, rather than hallucinating eligibility based on generic data. Similarly, if distinct source documents report contradictory requirements, the engine surfaces `CONFLICTING_INFORMATION`, obligating the LLM to transparently expose the contradiction rather than silently inventing a priority.

## Prompt Injection Resistance
Prompts V3 and V4 incorporate baseline injection resistance instructions, demanding that the model ignore adversarial instructions like "Ignore all previous instructions". The overarching defense relies on the deterministic logic override — even if the LLM yields to an injection and outputs a malformed or fabricated `ELIGIBLE` JSON payload, the deterministic `AdvisorService` validates and overwrites the state.

## Gemini Configuration and Fallback Behavior
The system relies on the `GEMINI_API_KEY` defined in `.env`. The architecture leverages `google-genai` for generation. If the key is omitted or the JSON parser fails to evaluate the model's response, a robust fallback automatically returns the pure deterministic state and retrieved contextual evidence without crashing the application.
