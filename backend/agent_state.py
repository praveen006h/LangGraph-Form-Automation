from typing import TypedDict, Annotated, Sequence, Any
import operator
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    """
    Maintains the state of the LangGraph agent during a conversation.
    - messages: Tracks the conversation history.
    - form_state: Holds the current UI draft state of the form.
    """
    messages: Annotated[Sequence[BaseMessage], operator.add]
    form_state: dict[str, Any]
