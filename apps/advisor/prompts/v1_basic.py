from .base import BasePromptBuilder

class V1BasicPrompt(BasePromptBuilder):
    """
    PROMPT V1 — Basic Grounded Prompt
    Establishes a baseline prompt that answers academic questions concisely and acknowledges uncertainty without inventing facts.
    """
    def build_prompt(self, query: str, evidence: list, decision_state: str, decision_reason: str, student_data: dict = None) -> str:
        context = ""
        for i, ev in enumerate(evidence):
            context += f"- {ev['content']}\n"
            
        return f"""You are an academic advisor. Answer the user's question using the provided evidence.
Do not invent facts. Be concise and acknowledge if you are uncertain.

Evidence:
{context}

Question: {query}

Provide a JSON response matching this schema exactly:
{{
  "state": "ANSWERED",
  "answer": "your answer here",
  "reason": "optional reason",
  "missing_information": [],
  "evidence": [],
  "recommendation": null,
  "uncertainty": null
}}
"""
