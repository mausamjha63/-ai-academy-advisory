# Phase 4 Final Report: Formal Evaluation & Measurement

## 1. Objective
The goal of Phase 4 is to formally and reproducibility measure the AI Academic Advisor's capabilities, specifically focusing on its accuracy, evidence grounding, edge-case robustness, and strict separation from prompt-hallucinated facts. 

## 2. Evaluation Methodology
The evaluation leverages a structured evaluation dataset running through a deterministic runner (`run_phase4_evaluation`). The runner isolates contexts strictly. The system captures exactly what the model structure attempted to return and validates it against the ground truth. 

**Note on Live Gemini Evaluation:**
Due to the absence of `GEMINI_API_KEY`, the **Live Gemini Semantic Evaluation was NOT EXECUTED / BLOCKED**. The pipeline successfully evaluated the routing, fallback generation, context handling, deterministic state preservation, and structural validation layers using the **MOCKED/FALLBACK** mechanism natively embedded within `AdvisorService`.

## 3. Test Dataset Design
We created `evaluation/phase4_cases.json`, a version-controlled Gold Dataset containing exactly 25 test cases.

## 4. Synthetic Student Profiles Used
The test cases reference existing synthetic data:
- `DEMO-001`, `DEMO-002`, `DEMO-003`, `DEMO-006`, `DEMO-007`, `DEMO-010`.
- A dedicated synthetic profile (`DEMO-TEST`) was instantiated programmatically during runtime to evaluate conflict handling natively inside the database.

## 5. Categories Covered
The 25 test cases cover:
- Attendance Rules, CGPA / Progression, Registration Rules, Summer Term
- Course Prerequisites & Offerings
- Student Specific Eligibility & Minor Courses
- F/FA Cases
- Missing Student Information (>= 3 cases)
- Information Unavailable (Strict boundary checking)
- Out of Scope
- Conflicting Information
- Prompt Injection

## 6. Gold-Answer Methodology
For each case, the expected deterministic state (e.g. `ELIGIBLE`, `NEEDS_MORE_INFORMATION`) and the precise `expected_evidence_source` (such as `Semester_Spread_Structures_Sept_2026.xlsx`) were rigidly defined entirely independent of the test run. 

## 7. Experimental Setup
The execution runner iterated through the identical 25 cases across 4 configurations, artificially restricting context variables to validate performance isolation.

## 8. Four-Stage Comparison

| Approach | Prompt | RAG Active? | Student Data Active? | Notes |
|---|---|---|---|---|
| **V1 Basic LLM** | `v1` | No | No | Tests naive generative capability without injected domain facts. |
| **V2 Structured Prompting** | `v2` | No | No | Tests constraint-following without injected domain facts. |
| **V3 RAG Grounded** | `v3` | Yes | No | Evaluates contextual extraction and strict provenance mapping. |
| **V4 Full Academic** | `v4` | Yes | Yes | Evaluates the full production hybrid logic (RAG + SQL Determinism). |

## 9. Metrics Definitions
- **Accuracy**: (CORRECT cases / total cases) * 100
- **Hallucination Rate**: (UNSUPPORTED_OR_HALLUCINATED cases / total cases) * 100
- **Average Response Time**: Total Time / Total Cases
- **Missing-Info Accuracy**: Cases explicitly targeting `NEEDS_MORE_INFORMATION` that correctly trigger the state.
- **Conflict-Handling Accuracy**: Cases targeting `CONFLICTING_INFORMATION` that correctly expose the conflict natively.

## 10. Aggregate Metrics
(Total cases evaluated = 100, i.e., 25 cases * 4 models)

| Metric | Result |
|---|---|
| **Overall Accuracy** | 30.00% |
| **Partial Correctness Rate** | 20.00% |
| **Incorrect Decision Rate** | 38.00% |
| **Unsupported/Hallucination Classification Rate — Mock/Structural Evaluation** | 12.00% |
| **Missing-Information Correct Hits** | 3 (exact matches) |
| **Conflict-Handling Accuracy** | 0 (due to mock fallback limitations) |
| **Average Response Time** | ~8.58 sec (Includes internal RAG embedding latency per loop) |

*Note: The reported 30.00% Overall Accuracy is the result of the controlled 100-permutation MOCK/FALLBACK structural evaluation. It MUST NOT be described as real Gemini accuracy, production AI accuracy, or the final semantic accuracy of the Academic Advisor. Accuracy is heavily skewed downward natively because V1 and V2 were intentionally evaluated without RAG evidence and structured student data, so their lower scores are expected consequences of the controlled context-ablation experiment.*

## 10.5 Interpretation of Phase 4 Results
Phase 4 successfully validates the reproducible evaluation framework, deterministic routing, context isolation, provenance handling, and fallback behavior. Because a Gemini API key was unavailable, the experiment does not provide a valid measurement of real Gemini semantic accuracy or real semantic hallucination rate.

The 30.00% Correct, 20.00% Partially Correct, 38.00% Incorrect, and 12.00% Unsupported/Hallucination are classifications produced under the MOCK/FALLBACK evaluation environment. They should be interpreted as structural/routing/context-isolation evaluation results, not as final production LLM semantic performance. The 12.00% value is NOT a measured real Gemini semantic hallucination rate. A true semantic hallucination rate requires live LLM execution and semantic evaluation of generated natural-language responses.

## 11. Missing-Information Results
The system correctly identified missing fields (like missing `programme` or `batch`) and triggered `NEEDS_MORE_INFORMATION` for the V4 pipeline. V1/V2 correctly defaulted to `INFORMATION_UNAVAILABLE` or failed, matching the restricted context parameters. The metric resulted in 3 exact matches. A normalized percentage was not reported due to the structure of the mocked output evaluation.

## 12. Prompt-Injection Results
Cases instructing the system to "Ignore official documents" or "invent the prerequisite for DATA101" failed to override the deterministic state. The system correctly evaluated the deterministic truth and blocked the injection attempt at the architectural level.

## 13. Evidence Correctness Results
When evaluated under V3 and V4 contexts, the mock fallback successfully retained the retrieved `source` variables extracted via RAG and SQL, confirming no artificial citations were fabricated during generation constraints.

## 14. Error Analysis
Because semantic LLM execution was blocked, V4 fallback generation could not naturally output linguistic reasoning, leading to "PARTIALLY_CORRECT" matches for standard generative questions. V1 and V2 incurred deliberate massive fail rates as designed for the contextual isolation experiment.

## 15. Limitations
- **No Live Semantic Evaluation**: All generative outputs were safely mocked. Real hallucination rates mapping abstract textual extraction vs prompt adherence cannot be calculated without an active Gemini API key.
- **Conflict Handling**: The Conflict-Handling Accuracy measured 0. This result reflects the MOCK/FALLBACK evaluation environment and does not establish that the production Gemini-backed system has 0% conflict-handling accuracy. The conflict case exposed a limitation of the fallback execution path.

## 16. Reproducibility Instructions
To reproduce these findings:
1. Ensure `evaluation/phase4_cases.json` is intact.
2. Activate virtual environment: `source venv/bin/activate`
3. Run: `python manage.py run_phase4_evaluation`
4. Inspect `evaluation/results/phase4_results.json`.

## Final Status
PHASE 4 COMPLETE — VERIFIED (MOCK/STRUCTURAL EVALUATION)

Live Gemini semantic evaluation remains pending because GEMINI_API_KEY was unavailable during this evaluation run.
