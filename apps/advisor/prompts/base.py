from pydantic import BaseModel, Field
from typing import List, Optional

class AdvisorResponse(BaseModel):
    state: str = Field(..., description="The decision state, e.g. ELIGIBLE, NOT_ELIGIBLE, NEEDS_MORE_INFORMATION, INFORMATION_UNAVAILABLE, CONFLICTING_INFORMATION, OUT_OF_SCOPE")
    answer: str = Field(..., description="The main explanatory text of the response. Should be concise.")
    reason: Optional[str] = Field(None, description="The core reason for the decision, if applicable.")
    missing_information: List[str] = Field(default_factory=list, description="List of specific fields or details missing from the student profile.")
    evidence: List[str] = Field(default_factory=list, description="List of exact source filenames or sheet names used to formulate the answer.")
    recommendation: Optional[str] = Field(None, description="Actionable recommendation if supported by evidence, else null.")
    uncertainty: Optional[str] = Field(None, description="Explanation of any uncertainty or conflicting information.")

class BasePromptBuilder:
    def build_prompt(self, query: str, evidence: list, decision_state: str, decision_reason: str, student_data: dict = None) -> str:
        raise NotImplementedError("Subclasses must implement build_prompt")
