from pydantic import BaseModel, Field
from typing import Optional, Literal


class MaterialItem(BaseModel):
    id: Optional[int] = None
    name: str


class SampleItem(BaseModel):
    id: Optional[int] = None
    product_name: str
    dosage: Optional[str] = None
    quantity: int = 1


class FormState(BaseModel):
    """Mirrors every field on the left-panel form."""
    interaction_id: Optional[int] = None
    hcp_name: Optional[str] = None
    interaction_date: Optional[str] = None
    topics_discussed: Optional[str] = None
    materials_shared: list[MaterialItem] = []
    samples_distributed: list[SampleItem] = []
    sentiment: Optional[Literal["positive", "neutral", "negative"]] = None
    outcomes: Optional[str] = None
    follow_up_actions: Optional[str] = None


class ChatMessage(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str


class ChatRequest(BaseModel):
    message: str
    conversation_history: list[ChatMessage] = []
    current_form_state: FormState = Field(default_factory=FormState)


class ToolCallInfo(BaseModel):
    tool_name: str
    tool_input: dict
    tool_output: str


class ChatResponse(BaseModel):
    ai_message: str
    updated_form_state: FormState
    tool_calls_made: list[ToolCallInfo] = []
