from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas import ChatRequest, ChatResponse, FormState, ToolCallInfo
from app.database import get_db
from app.agent.graph import run_agent

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest, db: Session = Depends(get_db)):
    """Main chat endpoint — sends user message to LangGraph agent, returns AI reply + updated form state."""
    result = await run_agent(
        message=request.message,
        conversation_history=request.conversation_history,
        current_form_state=request.current_form_state.model_dump(),
        db=db,
    )
    
    # Convert tool_calls_made dicts to ToolCallInfo
    tool_calls = [
        ToolCallInfo(
            tool_name=tc.get("tool_name", ""),
            tool_input=tc.get("tool_input", {}),
            tool_output=tc.get("tool_output", "")
        )
        for tc in result.get("tool_calls_made", [])
    ]
    
    return ChatResponse(
        ai_message=result["ai_message"],
        updated_form_state=FormState(**result["updated_form_state"]),
        tool_calls_made=tool_calls,
    )
