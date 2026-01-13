from pydantic import BaseModel, Field
from typing import Any

class ChatPromptResponse(BaseModel):
    answer: Any = Field(..., description="GPT 응답")
