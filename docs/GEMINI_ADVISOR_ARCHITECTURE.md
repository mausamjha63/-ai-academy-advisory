# Gemini Academic Advisor Architecture

This document outlines the final architecture of the AI Academic Advisor for Vidyashilp University. The system is designed to use the Gemini API (gemini-3.6-flash) as a natural-language reasoning and answer-generation engine, while strictly confining its knowledge to verified university sources and deterministic backend logic.

## Core Objective
The core objective is to ensure that **Gemini answers ONLY from the university academic information supplied by our existing RAG/structured-data pipeline.** The Django backend serves as the orchestration layer; Gemini is NOT the source of truth.

## System Components

### 1. Django Orchestration Layer (`AdvisorService`)
The central orchestrator that manages the flow of every user query.
- Receives the user query from the frontend.
- Executes the deterministic scope gate.
- Queries the RAG and Structured Data services.
- Queries the Decision Engine.
- Packages the verified context and system prompt.
- Sends the payload to the Gemini API.
- Validates and parses the strict JSON response.
- Enforces backend state overrides (DecisionEngine authority).
- Handles API failures gracefully.
- Returns the organized response to the UI.

### 2. Deterministic Scope Gate
Before expensive API calls are made, a lightweight, rule-based gate intercepts the query.
- Identifies **Greetings** (e.g., "Hi", "Hello") and returns a predefined academic introduction.
- Identifies **Out-of-Scope** topics (e.g., "weather", "Python", "tell me a joke") and instantly returns an academic domain redirect.
- Identifies **Ambiguous/Missing Info** queries (e.g., "What is the prerequisite?") and returns a `NEEDS_MORE_INFORMATION` state asking for clarification.
This reduces API latency, controls costs, and blocks prompt injection/jailbreak attempts at the boundary.

### 3. RAG Grounding (`RetrievalService`)
For qualitative academic policies and regulations, the system queries the Chroma vector database.
- Retrieves relevant text chunks solely from approved university sources (e.g., *Student Handbook Aug 2026.pdf*).
- Extracts and preserves source filenames and page numbers for UI provenance.
- If RAG and structured DB both return nothing, the backend returns `INFORMATION_UNAVAILABLE` and prevents Gemini from guessing.

### 4. Structured Academic Data (`AcademicDataService`)
For quantitative/course-specific data, the system queries the relational database.
- Detects course codes in the query.
- Retrieves Course details, Prerequisites, and Course Offerings.
- Formats this deterministic data into text for the LLM context.
- Gemini uses this data to generate natural language explanations without guessing credits, titles, or prerequisites.

### 5. Decision Engine
The authoritative component for evaluating student eligibility.
- Receives student context and requested course codes.
- Deterministically evaluates if prerequisites are met based on student history and current rules.
- Outputs states like `ELIGIBLE`, `NOT_ELIGIBLE`, `NEEDS_MORE_INFORMATION`, or `CONFLICTING_INFORMATION`.
- **Authority Rule:** Gemini CANNOT override this state. If the LLM generates a conflicting state, the `AdvisorService` forcibly restores the Decision Engine's state before returning to the UI.

### 6. Gemini Generation (gemini-3.6-flash)
The natural-language engine.
- Driven by a strict `v4_full_academic.py` prompt.
- Confined to the provided context.
- Must preserve provenance.
- Must handle prompt injections by defaulting to academic redirects.
- Outputs a strictly defined JSON schema containing `state`, `answer`, `reason`, `missing_information`, and `evidence`.

## Error Handling & Security
- **API Key:** `GEMINI_API_KEY` is securely stored in `.env` (gitignored). It is never exposed to the frontend or logs.
- **API Failures:** Network errors, `404 Not Found` (model deprecations), or `503 Unavailable` (high demand) are caught by the `AdvisorService`. A clean user-facing fallback message ("The AI service is temporarily unavailable. Please try again.") is returned, ensuring the application never crashes and stack traces are never exposed.
- **Malformed JSON:** Handled safely by falling back to the API error message.

## Conflicting and Missing Information
- **Conflicts:** If institutional sources disagree, the system does NOT silently pick a winner. It returns `CONFLICTING_INFORMATION` and presents both sources.
- **Missing Information:** If the user fails to provide necessary context (e.g., student ID for an eligibility check, or a course code for a prerequisite check), the system returns `NEEDS_MORE_INFORMATION` and specifies exactly what is required.
