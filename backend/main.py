from fastapi import FastAPI, Depends
from sqlmodel import Session
from database import create_db_and_tables, get_session
from models import ChatRequest, ChatResponse, HCP, Interaction, Material
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="AI-First CRM HCP API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

from langchain_core.messages import HumanMessage
from agent import app_agent

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    # Initialize the state graph with the incoming message and current form state
    initial_state = {
        "messages": [HumanMessage(content=request.message)],
        "form_state": request.current_form_state
    }
    
    # Execute the agent graph
    result = app_agent.invoke(initial_state)
    
    # Extract the AI's final natural language response and the mutated form state
    ai_reply_msg = result["messages"][-1].content
    updated_form = result["form_state"]
    
    return ChatResponse(
        ai_reply=ai_reply_msg,
        updated_form_state=updated_form
    )

@app.get("/api/hcps")
def read_hcps(session: Session = Depends(get_session)):
    from sqlmodel import select
    hcps = session.exec(select(HCP)).all()
    return hcps

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
