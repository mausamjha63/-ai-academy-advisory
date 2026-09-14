from .base import BasePromptBuilder

class V2StructuredPrompt(BasePromptBuilder):
    """
    PROMPT V2 — Structured Academic Advisor Prompt
    Explicitly defines roles, rules, and structured output formatting.
    """
    def build_prompt(self, query: str, evidence: list, decision_state: str, decision_reason: str, student_data: dict = None) -> str:
        context = ""
        for i, ev in enumerate(evidence):
            context += f"Source {i+1}: {ev['content']}\n"
            
        return f"""ROLE: You are an official Academic Advisor for the university.
TASK: Answer the student's query based ONLY on the provided evidence.
RULES: 
1. Do not invent any values.
2. Output must be strictly valid JSON.
3. If information is unavailable, clearly state so.

EVIDENCE:
{context}

USER QUERY: {query}

OUTPUT FORMAT: Return only a JSON object matching this structure:
{{
  "state": "ANSWERED",
  "answer": "string",
  "reason": "string or null",
  "missing_information": ["list of strings"],
  "evidence": ["list of sources"],
  "recommendation": "string or null",
  "uncertainty": "string or null"
}}
"""
