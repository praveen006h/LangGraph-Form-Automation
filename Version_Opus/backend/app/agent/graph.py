from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from app.agent.state import AgentState
from app.agent.tools import create_tools
from app.agent.prompts import SYSTEM_PROMPT
from app.config import settings
import json
import os


def create_agent_graph(db, form_state: dict):
    """Create a new agent graph with injected db session and form state."""
    tools = create_tools(db, form_state)
    
    llm = ChatGroq(
        model=settings.llm_model,
        temperature=0.1,
        max_tokens=4096,
        api_key=settings.groq_api_key,
    )
    llm_with_tools = llm.bind_tools(tools)
    
    def agent_node(state: AgentState) -> dict:
        response = llm_with_tools.invoke(state["messages"])
        return {"messages": [response]}
    
    def should_continue(state: AgentState) -> str:
        last_message = state["messages"][-1]
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"
        return END
    
    graph = StateGraph(AgentState)
    graph.add_node("agent", agent_node)
    graph.add_node("tools", ToolNode(tools))
    graph.set_entry_point("agent")
    graph.add_conditional_edges("agent", should_continue, {
        "tools": "tools",
        END: END,
    })
    graph.add_edge("tools", "agent")
    
    return graph.compile()


async def run_agent(message: str, conversation_history: list, current_form_state: dict, db) -> dict:
    """Entry point called by the FastAPI endpoint."""
    # Make a mutable copy of form state
    form_state = dict(current_form_state)
    
    # Convert materials_shared and samples_distributed if they're Pydantic models
    if "materials_shared" in form_state:
        form_state["materials_shared"] = [
            item if isinstance(item, dict) else item.model_dump() 
            for item in form_state.get("materials_shared", [])
        ]
    if "samples_distributed" in form_state:
        form_state["samples_distributed"] = [
            item if isinstance(item, dict) else item.model_dump() 
            for item in form_state.get("samples_distributed", [])
        ]
    
    # Create graph with injected dependencies
    agent_graph = create_agent_graph(db, form_state)
    
    # Inject the current LLM model into the prompt so the agent knows what it's running on
    current_prompt = SYSTEM_PROMPT.replace("{LLM_MODEL}", settings.llm_model)
    
    # Build messages
    messages = [SystemMessage(content=current_prompt)]
    
    # Keep only the last 10 messages to avoid token limits
    recent_history = conversation_history[-10:] if len(conversation_history) > 10 else conversation_history
    for msg in recent_history:
        role = msg.role if hasattr(msg, 'role') else msg.get('role', 'user')
        content = msg.content if hasattr(msg, 'content') else msg.get('content', '')
        if role == "user":
            messages.append(HumanMessage(content=content))
        elif role == "assistant":
            messages.append(AIMessage(content=content))
    
    # Add current form state as context in the user message
    form_context = f"\n\n<context>\nCurrent Form State:\n{json.dumps(form_state, indent=2, default=str)}\n</context>"
    messages.append(HumanMessage(content=message + form_context))
    
    initial_state = {
        "messages": messages,
        "form_state": form_state,
        "tool_calls_made": [],
    }
    
    try:
        final_state = await agent_graph.ainvoke(initial_state)
        
        # Extract the final AI message (the last AIMessage without tool_calls)
        ai_message = ""
        tool_calls_info = []
        
        for msg in final_state["messages"]:
            if isinstance(msg, AIMessage):
                if hasattr(msg, "tool_calls") and msg.tool_calls:
                    for tc in msg.tool_calls:
                        tool_calls_info.append({
                            "tool_name": tc["name"],
                            "tool_input": tc["args"],
                            "tool_output": ""
                        })
                elif msg.content:
                    ai_message = msg.content
        
        return {
            "ai_message": ai_message or "I've processed your request.",
            "updated_form_state": form_state,
            "tool_calls_made": tool_calls_info,
        }
    except Exception as e:
        print(f"Agent error: {e}")
        error_msg = str(e).lower()
        
        if "tokens per minute (tpm)" in error_msg or "rate_limit_exceeded" in error_msg or "413" in error_msg or "429" in error_msg:
            clean_msg = "You have hit the token rate limit for this model. Please wait a couple of minutes before sending your next message, or click 'Clear' to reset the chat history."
        elif "tokens per day (tpd)" in error_msg:
            clean_msg = "You have exhausted your daily token limit for this Groq model. Please try again tomorrow, or switch to a different model in the backend configuration."
        elif "model_decommissioned" in error_msg:
            clean_msg = "The currently selected AI model is no longer supported. Please ask your administrator to update the model in the backend configuration."
        elif "tool_use_failed" in error_msg:
            clean_msg = "I got a little confused trying to log that information. Could you try rephrasing your request?"
        else:
            # Fallback for generic unexpected errors, keep it clean
            clean_msg = "I encountered an unexpected error processing your request. Please try again."
            
        return {
            "ai_message": clean_msg,
            "updated_form_state": form_state,
            "tool_calls_made": [],
        }
