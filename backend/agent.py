from langgraph.graph import StateGraph, START, END
from langchain_core.messages import SystemMessage, ToolMessage, AIMessage
from langchain_groq import ChatGroq
import os
import json
from agent_state import AgentState
from tools import log_interaction, edit_interaction, suggest_follow_up, get_hcp_history, search_knowledge_base

# The tools list
tools = [log_interaction, edit_interaction, suggest_follow_up, get_hcp_history, search_knowledge_base]
tool_map = {tool.name: tool for tool in tools}

# Initialize Groq LLM with the requested llama-3.1-8b-instant model
llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)
llm_with_tools = llm.bind_tools(tools)

SYSTEM_PROMPT = """You are an AI assistant strictly designed to log interactions for pharmaceutical sales reps. 
You control a form interface. The user cannot edit the form themselves; they rely on you.

CRITICAL INSTRUCTIONS:
1. You MUST ONLY discuss topics directly related to logging or editing Healthcare Professional (HCP) interactions, product details, or pharmaceutical CRM tasks.
2. If the user asks you to write an essay, write a story, or answer general knowledge questions (e.g., about nature), you MUST REFUSE immediately. Reply with a short, polite sentence stating that you are a specialized CRM assistant and cannot process off-topic requests. Do not generate the requested off-topic content under any circumstances.
3. Keep all responses concise and strictly related to the form state. Avoid lengthy conversational filler to conserve tokens.

When the user describes an interaction, use the 'log_interaction' tool to populate the form.
If the user corrects a mistake, use the 'edit_interaction' tool.
Always confirm to the user what fields you updated in 1-2 short sentences.
Current Form State: {form_state}"""

from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from groq import RateLimitError

@retry(
    stop=stop_after_attempt(3), 
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type(RateLimitError)
)
def invoke_with_retry(msgs_to_send):
    return llm_with_tools.invoke(msgs_to_send)

def call_model(state: AgentState):
    messages = state.get('messages', [])
    form_state = state.get('form_state', {}) or {}
    
    # Inject dynamic system prompt with current form state
    sys_msg = SystemMessage(content=SYSTEM_PROMPT.format(form_state=json.dumps(form_state)))
    
    # Check if system message is already present
    if not messages or not isinstance(messages[0], SystemMessage):
        msgs_to_send = [sys_msg] + list(messages)
    else:
        msgs_to_send = [sys_msg] + list(messages[1:])
        
    try:
        response = invoke_with_retry(msgs_to_send)
        return {"messages": [response], "form_state": form_state}
    except Exception as e:
        error_msg = str(e)
        # Handle specific Groq Rate Limit errors (TPD or RPM)
        if "tokens per day (TPD)" in error_msg:
            clean_msg = "You have exhausted your daily token limit for this Groq model. Please switch to a lighter model (like llama-3.1-8b-instant) or try again later."
        elif "Rate limit reached" in error_msg:
            clean_msg = "I am currently experiencing high traffic rate limits. Please wait a moment and try again."
        else:
            clean_msg = "I'm sorry, I encountered an internal error processing that request. Please try again."
            
        fallback = AIMessage(content=clean_msg)
        return {"messages": [fallback], "form_state": form_state}

def execute_tools(state: AgentState):
    messages = state.get('messages', [])
    form_state = state.get('form_state', {}).copy() if state.get('form_state') else {}
    
    if not messages:
        return {"messages": [], "form_state": form_state}
        
    last_message = messages[-1]
    tool_messages = []
    
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        for tool_call in last_message.tool_calls:
            tool_name = tool_call.get("name")
            tool_args = tool_call.get("args", {})
            
            tool = tool_map.get(tool_name)
            if tool:
                try:
                    result = tool.invoke(tool_args)
                    
                    # Handle state mutation tools returning dicts safely
                    if isinstance(result, dict) and "action" in result:
                        if result["action"] == "update_form":
                            updates = result.get("updates", {})
                            if isinstance(updates, dict):
                                form_state.update(updates)
                        elif result["action"] == "edit_field":
                            field = result.get("field")
                            if field:
                                form_state[field] = result.get("value")
                        
                        tool_messages.append(ToolMessage(content=str(result.get("message", "Success")), tool_call_id=tool_call["id"]))
                    else:
                        # String return from other tools
                        tool_messages.append(ToolMessage(content=str(result), tool_call_id=tool_call["id"]))
                except Exception as e:
                    # Catch malformed tool inputs gracefully
                    tool_messages.append(ToolMessage(content=f"Error executing tool: {str(e)}", tool_call_id=tool_call["id"]))
            else:
                tool_messages.append(ToolMessage(content=f"Tool {tool_name} not found.", tool_call_id=tool_call["id"]))
                
    return {"messages": tool_messages, "form_state": form_state}

def should_continue(state: AgentState):
    messages = state.get('messages', [])
    if not messages:
        return END
        
    last_message = messages[-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    return END

# Build the state graph
workflow = StateGraph(AgentState)
workflow.add_node("agent", call_model)
workflow.add_node("tools", execute_tools)

workflow.add_edge(START, "agent")
workflow.add_conditional_edges("agent", should_continue, ["tools", END])
workflow.add_edge("tools", "agent")

app_agent = workflow.compile()
