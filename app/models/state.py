from pydantic import BaseModel
from typing import List

class AgentState(BaseModel):
    user_input: str = ""
    extracted_text: str = ""
    extracted: bool = False
    intent: str = ""
    intent_confidence: float = 0.0
    requires_clarification: bool = False
    clarification_question: str = ""
    final_result: str = ""
    clarifications: List[str] = []
