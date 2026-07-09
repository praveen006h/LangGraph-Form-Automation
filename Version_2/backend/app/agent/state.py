from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """State that flows through every node in the LangGraph graph."""
    messages: Annotated[list[BaseMessage], add_messages]
    form_state: dict
    tool_calls_made: list
