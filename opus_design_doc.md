# AI-First CRM HCP Module — Log Interaction Screen
## Comprehensive Design Document

---

## 1. System Architecture Overview

### 1.1 High-Level Architecture

```mermaid
graph TB
    subgraph Frontend ["Frontend (React + Redux)"]
        UI["SplitScreenLayout"]
        Form["InteractionForm (Read-Only)"]
        Chat["ChatPanel"]
        Store["Redux Store"]
        Form --> Store
        Chat --> Store
        UI --> Form
        UI --> Chat
    end

    subgraph Backend ["Backend (Python FastAPI)"]
        API["FastAPI Server"]
        Agent["LangGraph Agent"]
        Tools["Tool Suite (5 Tools)"]
        API --> Agent
        Agent --> Tools
    end

    subgraph External ["External Services"]
        LLM["Groq API (gemma2-9b-it)"]
        DB["PostgreSQL"]
    end

    Chat -- "POST /api/chat\n{message, form_state}" --> API
    API -- "SSE / JSON Response\n{ai_reply, updated_form_state}" --> Chat
    Store -- "Dispatches formSlice updates" --> Form
    Agent --> LLM
    Tools --> DB
```

### 1.2 Data Flow — Chat-Driven Form Population

This is the critical flow that makes the application AI-first:

```mermaid
sequenceDiagram
    participant User
    participant ChatPanel
    participant Redux as Redux Store
    participant FastAPI
    participant LangGraph as LangGraph Agent
    participant Groq as Groq LLM
    participant DB as PostgreSQL

    User->>ChatPanel: Types natural language message
    ChatPanel->>Redux: dispatch(addUserMessage)
    ChatPanel->>FastAPI: POST /api/chat {message, conversation_history, current_form_state}
    FastAPI->>LangGraph: invoke(state)
    LangGraph->>Groq: LLM call with tools bound
    Groq-->>LangGraph: Tool call decision (e.g., log_interaction)
    LangGraph->>LangGraph: Execute tool node
    LangGraph->>DB: Persist/query data
    DB-->>LangGraph: Result
    LangGraph-->>FastAPI: {ai_message, updated_form_state, tool_calls_made}
    FastAPI-->>ChatPanel: JSON Response
    ChatPanel->>Redux: dispatch(addAIMessage)
    ChatPanel->>Redux: dispatch(updateFormState(updated_form_state))
    Redux-->>ChatPanel: Re-render chat
    Redux-->>ChatPanel: Re-render form with new data
```

### 1.3 Key Architectural Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Form is read-only | ✅ Enforced | Video transcript mandate: "You must not fill the left form manually" |
| State ownership | Redux (frontend) | Form state lives in Redux; backend returns deltas on each chat turn |
| Communication | REST + JSON | Simple request/response; SSE optional for streaming |
| Agent framework | LangGraph | Mandatory per assignment; provides graph-based tool orchestration |
| LLM provider | Groq (gemma2-9b-it) | Mandatory per assignment; fast inference |
| Database | PostgreSQL | Robust relational DB for structured CRM data |

---

## 2. Database Schema

### 2.1 Entity Relationship Diagram

```mermaid
erDiagram
    hcp_profiles {
        int id PK
        varchar first_name
        varchar last_name
        varchar specialty
        varchar institution
        varchar phone
        varchar email
        varchar npi_number
        text notes
        timestamp created_at
        timestamp updated_at
    }

    interactions {
        int id PK
        int hcp_id FK
        date interaction_date
        text topics_discussed
        varchar sentiment
        text outcomes
        text follow_up_actions
        varchar status
        timestamp created_at
        timestamp updated_at
    }

    materials {
        int id PK
        varchar name
        varchar type
        text description
        boolean is_active
        timestamp created_at
    }

    interaction_materials {
        int id PK
        int interaction_id FK
        int material_id FK
        timestamp shared_at
    }

    samples {
        int id PK
        varchar product_name
        varchar dosage
        int quantity_available
        boolean is_active
        timestamp created_at
    }

    interaction_samples {
        int id PK
        int interaction_id FK
        int sample_id FK
        int quantity_distributed
        timestamp distributed_at
    }

    product_knowledge {
        int id PK
        varchar product_name
        text description
        text indications
        text contraindications
        text key_studies
        text competitive_advantages
        boolean is_active
        timestamp created_at
        timestamp updated_at
    }

    conversation_history {
        int id PK
        int interaction_id FK
        varchar role
        text content
        json tool_calls
        timestamp created_at
    }

    hcp_profiles ||--o{ interactions : "has many"
    interactions ||--o{ interaction_materials : "has many"
    materials ||--o{ interaction_materials : "shared in"
    interactions ||--o{ interaction_samples : "has many"
    samples ||--o{ interaction_samples : "distributed in"
    interactions ||--o{ conversation_history : "has conversation"
```

### 2.2 SQL DDL

```sql
-- HCP Profiles
CREATE TABLE hcp_profiles (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    specialty VARCHAR(100),
    institution VARCHAR(200),
    phone VARCHAR(50),
    email VARCHAR(100),
    npi_number VARCHAR(50),
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Interactions
CREATE TABLE interactions (
    id SERIAL PRIMARY KEY,
    hcp_id INTEGER REFERENCES hcp_profiles(id) ON DELETE SET NULL,
    interaction_date DATE DEFAULT CURRENT_DATE,
    topics_discussed TEXT,
    sentiment VARCHAR(20) CHECK (sentiment IN ('positive', 'neutral', 'negative')),
    outcomes TEXT,
    follow_up_actions TEXT,
    status VARCHAR(20) DEFAULT 'draft' CHECK (status IN ('draft', 'submitted')),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Materials catalog
CREATE TABLE materials (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    type VARCHAR(50) DEFAULT 'other',
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Junction: interaction <-> materials
CREATE TABLE interaction_materials (
    id SERIAL PRIMARY KEY,
    interaction_id INTEGER REFERENCES interactions(id) ON DELETE CASCADE,
    material_id INTEGER REFERENCES materials(id) ON DELETE CASCADE,
    shared_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(interaction_id, material_id)
);

-- Samples catalog
CREATE TABLE samples (
    id SERIAL PRIMARY KEY,
    product_name VARCHAR(200) NOT NULL,
    dosage VARCHAR(50),
    quantity_available INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Junction: interaction <-> samples
CREATE TABLE interaction_samples (
    id SERIAL PRIMARY KEY,
    interaction_id INTEGER REFERENCES interactions(id) ON DELETE CASCADE,
    sample_id INTEGER REFERENCES samples(id) ON DELETE CASCADE,
    quantity_distributed INTEGER DEFAULT 1,
    distributed_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(interaction_id, sample_id)
);

-- Product knowledge base
CREATE TABLE product_knowledge (
    id SERIAL PRIMARY KEY,
    product_name VARCHAR(200) NOT NULL,
    description TEXT,
    indications TEXT,
    contraindications TEXT,
    key_studies TEXT,
    competitive_advantages TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Conversation history
CREATE TABLE conversation_history (
    id SERIAL PRIMARY KEY,
    interaction_id INTEGER REFERENCES interactions(id) ON DELETE SET NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    tool_calls JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Seed data for materials
INSERT INTO materials (name, type, description) VALUES
('Product X Brochure', 'brochure', 'Detailed brochure for Product X with efficacy data'),
('Product X Clinical Study', 'study', 'Phase III clinical study results for Product X'),
('Product Y Whitepaper', 'whitepaper', 'Comprehensive whitepaper on Product Y mechanism of action'),
('Product Z Presentation', 'presentation', 'Sales presentation deck for Product Z'),
('Dosing Guide - Product X', 'brochure', 'Quick reference dosing guide for Product X');

-- Seed data for samples
INSERT INTO samples (product_name, dosage, quantity_available) VALUES
('Product X', '10mg', 100),
('Product X', '25mg', 75),
('Product Y', '50mg', 50),
('Product Z', '100mg', 30);

-- Seed data for HCP profiles
INSERT INTO hcp_profiles (first_name, last_name, specialty, institution) VALUES
('Sarah', 'Smith', 'Cardiology', 'City General Hospital'),
('John', 'Williams', 'Oncology', 'Memorial Cancer Center'),
('Emily', 'Chen', 'Neurology', 'University Medical Center'),
('Michael', 'Johnson', 'Internal Medicine', 'Community Health Clinic'),
('Priya', 'Patel', 'Endocrinology', 'Metro Healthcare System');

-- Seed data for product knowledge
INSERT INTO product_knowledge (product_name, description, indications, contraindications, key_studies, competitive_advantages) VALUES
('Product X', 'A novel cardiovascular drug targeting hypertension.', 'Hypertension, Heart Failure', 'Pregnancy, Severe Renal Impairment', 'HEART-1 Trial: 40% reduction in systolic BP. CARDIO-SAFE Study: Superior safety profile.', 'Once-daily dosing, fewer side effects than ACE inhibitors, proven CV outcomes benefit.'),
('Product Y', 'An advanced oncology therapy for solid tumors.', 'Non-small cell lung cancer, Melanoma', 'Autoimmune disorders, Organ transplant recipients', 'TUMOR-HALT Trial: 35% improvement in PFS. ONCO-LIFE Study: Improved overall survival.', 'Oral formulation, combination-friendly, manageable toxicity profile.'),
('Product Z', 'A breakthrough neurological treatment for migraine prevention.', 'Chronic Migraine, Episodic Migraine', 'Cardiovascular disease, Hepatic impairment', 'MIGRAINE-FREE Trial: 50% reduction in monthly migraine days. NEURO-SAFE Study: Minimal cognitive side effects.', 'Monthly injection, rapid onset of action, no drug interactions.');
```

---

## 3. API Specification (FastAPI)

### 3.1 Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry point
│   ├── config.py             # Settings / env vars
│   ├── database.py           # SQLAlchemy engine & session
│   ├── models.py             # SQLAlchemy ORM models
│   ├── schemas.py            # Pydantic request/response models
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── chat.py           # /api/chat endpoint
│   │   └── data.py           # /api/materials, /api/samples, etc.
│   └── agent/
│       ├── __init__.py
│       ├── graph.py           # LangGraph graph definition
│       ├── state.py           # AgentState TypedDict
│       ├── tools.py           # All 5 tool definitions
│       └── prompts.py         # System prompt
├── requirements.txt
├── .env
└── alembic/                   # (optional) migrations
```

### 3.2 Pydantic Schemas

```python
# app/schemas.py
from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import date

# ── Form State (the single source of truth for the left panel) ──

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
    interaction_date: Optional[str] = None          # ISO date string
    topics_discussed: Optional[str] = None
    materials_shared: list[MaterialItem] = []
    samples_distributed: list[SampleItem] = []
    sentiment: Optional[Literal["positive", "neutral", "negative"]] = None
    outcomes: Optional[str] = None
    follow_up_actions: Optional[str] = None

# ── Chat Message ──

class ChatMessage(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str

# ── Request / Response ──

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
```

### 3.3 API Endpoints

| Method | Path | Description | Request Body | Response Body |
|--------|------|-------------|--------------|---------------|
| `POST` | `/api/chat` | Main chat endpoint. Sends user message, receives AI reply + updated form state | `ChatRequest` | `ChatResponse` |
| `GET` | `/api/materials` | List all available materials (for autocomplete) | — | `list[MaterialItem]` |
| `GET` | `/api/samples` | List all available samples | — | `list[SampleItem]` |
| `GET` | `/api/hcp-profiles` | List HCP profiles | — | `list[HCPProfile]` |
| `GET` | `/api/hcp-profiles/{id}/history` | Get interaction history for an HCP | — | `list[InteractionSummary]` |
| `POST` | `/api/interactions/submit` | Finalize/submit a drafted interaction | `FormState` | `{success, interaction_id}` |
| `GET` | `/api/health` | Health check | — | `{status: "ok"}` |

### 3.4 Core Endpoint Detail — `POST /api/chat`

```python
# app/routers/chat.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas import ChatRequest, ChatResponse
from app.database import get_db
from app.agent.graph import run_agent

router = APIRouter(prefix="/api", tags=["chat"])

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest, db: Session = Depends(get_db)):
    """
    1. Receive user message + current form state + conversation history
    2. Invoke LangGraph agent
    3. Agent decides which tool(s) to call based on user intent
    4. Return AI response text + updated form state + tool call info
    """
    result = await run_agent(
        message=request.message,
        conversation_history=request.conversation_history,
        current_form_state=request.current_form_state,
        db=db,
    )
    return ChatResponse(
        ai_message=result["ai_message"],
        updated_form_state=result["updated_form_state"],
        tool_calls_made=result.get("tool_calls_made", []),
    )
```

---

## 4. LangGraph Agent Design (Deep Dive)

### 4.1 Agent State Definition

```python
# app/agent/state.py
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from app.schemas import FormState

class AgentState(TypedDict):
    """
    The state that flows through every node in the LangGraph graph.
    """
    # Conversation messages (auto-appended via add_messages reducer)
    messages: Annotated[list[BaseMessage], add_messages]
    
    # Current form state — updated by tools, returned to frontend
    form_state: FormState
    
    # Track which tools were called in this turn
    tool_calls_made: list[dict]
```

### 4.2 Graph Structure

```mermaid
graph TD
    START(["__start__"]) --> Agent["agent node\n(LLM with tools bound)"]
    Agent --> ShouldContinue{"should_continue?"}
    ShouldContinue -- "tool_calls present" --> Tools["tools node\n(ToolNode executor)"]
    ShouldContinue -- "no tool_calls" --> END(["__end__"])
    Tools --> Agent
```

### 4.3 Graph Implementation

```python
# app/agent/graph.py
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_groq import ChatGroq
from app.agent.state import AgentState
from app.agent.tools import get_all_tools
from app.agent.prompts import SYSTEM_PROMPT
from app.schemas import FormState, ChatMessage
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
import json

def create_agent_graph():
    tools = get_all_tools()
    
    # Initialize Groq LLM with tool binding
    llm = ChatGroq(
        model="gemma2-9b-it",
        temperature=0.1,
        max_tokens=4096,
    )
    llm_with_tools = llm.bind_tools(tools)
    
    # Agent node: calls the LLM
    def agent_node(state: AgentState) -> dict:
        response = llm_with_tools.invoke(state["messages"])
        return {"messages": [response]}
    
    # Routing function
    def should_continue(state: AgentState) -> str:
        last_message = state["messages"][-1]
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"
        return END
    
    # Build graph
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

# Compiled graph (singleton)
agent_graph = create_agent_graph()

async def run_agent(
    message: str,
    conversation_history: list[ChatMessage],
    current_form_state: FormState,
    db,
) -> dict:
    """Entry point called by the FastAPI endpoint."""
    
    # Build messages list
    messages = [SystemMessage(content=SYSTEM_PROMPT)]
    
    # Add conversation history
    for msg in conversation_history:
        if msg.role == "user":
            messages.append(HumanMessage(content=msg.content))
        elif msg.role == "assistant":
            messages.append(AIMessage(content=msg.content))
    
    # Add current form state as context
    form_context = f"\n\n[CURRENT FORM STATE]\n{current_form_state.model_dump_json(indent=2)}"
    messages.append(HumanMessage(content=message + form_context))
    
    # Prepare initial state
    initial_state: AgentState = {
        "messages": messages,
        "form_state": current_form_state,
        "tool_calls_made": [],
    }
    
    # Run the graph
    final_state = await agent_graph.ainvoke(initial_state)
    
    # Extract the final AI message
    ai_message = ""
    for msg in reversed(final_state["messages"]):
        if isinstance(msg, AIMessage) and msg.content and not msg.tool_calls:
            ai_message = msg.content
            break
    
    return {
        "ai_message": ai_message,
        "updated_form_state": final_state["form_state"],
        "tool_calls_made": final_state.get("tool_calls_made", []),
    }
```

### 4.4 All 5 Tools — Detailed Specification

#### Tool 1: `log_interaction` (Mandatory)

| Property | Detail |
|----------|--------|
| **Name** | `log_interaction` |
| **Description** | Extracts structured entities from a natural language interaction summary and populates the form fields. Use this when the user describes a new interaction with an HCP. |
| **Input Schema** | See below |
| **Behavior** | Parses the user's message to extract HCP name, date, topics, sentiment, materials, samples, outcomes, and follow-up actions. Creates/updates the form state. Persists a draft interaction to the database. |

```python
class LogInteractionInput(BaseModel):
    hcp_name: str = Field(description="Full name of the healthcare professional (e.g., 'Dr. Smith')")
    interaction_date: Optional[str] = Field(default=None, description="Date of interaction in YYYY-MM-DD format. Use today if not specified.")
    topics_discussed: Optional[str] = Field(default=None, description="Topics discussed during the interaction")
    materials_shared: Optional[list[str]] = Field(default=None, description="Names of materials shared (e.g., ['brochure', 'clinical study'])")
    samples_distributed: Optional[list[dict]] = Field(default=None, description="Samples given, each with product_name, dosage, quantity")
    sentiment: Optional[Literal["positive", "neutral", "negative"]] = Field(default=None, description="Observed HCP sentiment")
    outcomes: Optional[str] = Field(default=None, description="Key outcomes or agreements from the interaction")
    follow_up_actions: Optional[str] = Field(default=None, description="Planned follow-up actions")
```

**Output:** Returns the fully populated `FormState` as a JSON string. The graph updates `state["form_state"]` accordingly.

---

#### Tool 2: `edit_interaction` (Mandatory)

| Property | Detail |
|----------|--------|
| **Name** | `edit_interaction` |
| **Description** | Modifies specific fields of the current interaction form. Use this when the user wants to correct or update specific details without changing everything else. Only updates fields that are explicitly provided. |
| **Input Schema** | See below |
| **Behavior** | Takes only the fields the user wants to change. Merges them into the existing form state. Persists updates to the database. |

```python
class EditInteractionInput(BaseModel):
    hcp_name: Optional[str] = Field(default=None, description="Updated HCP name")
    interaction_date: Optional[str] = Field(default=None, description="Updated date in YYYY-MM-DD format")
    topics_discussed: Optional[str] = Field(default=None, description="Updated topics")
    materials_shared: Optional[list[str]] = Field(default=None, description="Updated materials list (replaces current)")
    samples_distributed: Optional[list[dict]] = Field(default=None, description="Updated samples list (replaces current)")
    sentiment: Optional[Literal["positive", "neutral", "negative"]] = Field(default=None, description="Updated sentiment")
    outcomes: Optional[str] = Field(default=None, description="Updated outcomes")
    follow_up_actions: Optional[str] = Field(default=None, description="Updated follow-up actions")
```

**Output:** Returns the merged `FormState` with only the specified fields overwritten.

---

#### Tool 3: `suggest_follow_up` (Custom)

| Property | Detail |
|----------|--------|
| **Name** | `suggest_follow_up` |
| **Description** | Analyzes the current interaction context (topics discussed, sentiment, materials shared) and suggests contextually relevant follow-up actions for the sales representative. Use this when the user asks for follow-up suggestions or when the interaction has been logged. |
| **Input Schema** | See below |
| **Behavior** | Reads the current form state, applies sales best-practice heuristics (e.g., negative sentiment → schedule educational meeting; positive sentiment → send trial samples), and returns 2–3 actionable follow-up suggestions. Can optionally auto-populate the follow_up_actions field if the user approves. |

```python
class SuggestFollowUpInput(BaseModel):
    hcp_name: str = Field(description="Name of the HCP")
    topics_discussed: Optional[str] = Field(default=None, description="Topics from the interaction")
    sentiment: Optional[str] = Field(default=None, description="HCP sentiment")
    auto_populate: bool = Field(default=False, description="If true, automatically populate the follow-up actions field")
```

**Output:** A list of 2–3 suggested follow-up actions as a formatted string. If `auto_populate=True`, also updates `form_state.follow_up_actions`.

---

#### Tool 4: `get_hcp_history` (Custom)

| Property | Detail |
|----------|--------|
| **Name** | `get_hcp_history` |
| **Description** | Retrieves the interaction history and profile information for a specific HCP. Use this when the user asks about past interactions, an HCP's preferences, or needs context before a meeting. |
| **Input Schema** | See below |
| **Behavior** | Queries the database for the HCP's profile and their past interactions (last 10). Returns a formatted summary including specialty, institution, past topics, sentiment trends, and materials previously shared. |

```python
class GetHCPHistoryInput(BaseModel):
    hcp_name: str = Field(description="Name of the HCP to look up (partial match supported)")
```

**Output:** A formatted string containing:
- HCP profile info (specialty, institution, contact)
- Last N interactions (date, topics, sentiment, materials)
- Sentiment trend (e.g., "Trending positive over last 3 visits")

---

#### Tool 5: `search_product_knowledge` (Custom)

| Property | Detail |
|----------|--------|
| **Name** | `search_product_knowledge` |
| **Description** | Searches the product knowledge base for information about pharmaceutical products. Use this when the user asks about product details, indications, competitive advantages, or needs talking points for an HCP meeting. |
| **Input Schema** | See below |
| **Behavior** | Performs a keyword/fuzzy search against the `product_knowledge` table. Returns structured product information including indications, key studies, and competitive advantages. |

```python
class SearchProductKnowledgeInput(BaseModel):
    query: str = Field(description="Product name or keyword to search for")
```

**Output:** Formatted product information including description, indications, contraindications, key clinical studies, and competitive advantages.

---

### 4.5 System Prompt

```python
# app/agent/prompts.py

SYSTEM_PROMPT = """You are an AI assistant for a pharmaceutical CRM system, 
specifically designed to help field sales representatives log and manage their 
interactions with Healthcare Professionals (HCPs).

## Your Role
You control a form on the user's screen. The user CANNOT fill out the form 
manually — they interact with you via chat, and you populate the form for them 
using your tools.

## Available Tools
1. **log_interaction** — Use when the user describes a new interaction. Extract 
   ALL relevant entities (HCP name, date, topics, sentiment, materials, samples, 
   outcomes, follow-ups) from their message and populate the form.
2. **edit_interaction** — Use when the user wants to correct or modify specific 
   fields. Only update the fields they mention; leave everything else intact.
3. **suggest_follow_up** — Use when the user asks for follow-up suggestions, or 
   proactively offer after logging an interaction.
4. **get_hcp_history** — Use when the user asks about an HCP's past interactions, 
   profile, or history.
5. **search_product_knowledge** — Use when the user asks about product details, 
   indications, studies, or competitive positioning.

## Rules
- ALWAYS use tools when the user's message implies an action. NEVER just 
  describe what you would do — actually do it by calling the tool.
- When logging a new interaction, extract as many fields as possible from the 
  user's message. If the date is not mentioned, use today's date.
- When editing, ONLY update the fields the user explicitly mentions. Do NOT 
  overwrite other fields.
- For sentiment, map natural language to: "positive", "neutral", or "negative".
- For materials, try to match against known materials in the system. If no exact 
  match, use the user's description.
- After logging or editing, confirm what was populated and offer to suggest 
  follow-up actions.
- Be conversational, professional, and concise.
- If the user's message is ambiguous, ask a clarifying question instead of 
  guessing.

## Response Format
After calling a tool, provide a brief confirmation of what was done, listing the 
fields that were populated or changed. Use checkmark emojis (✅) for populated 
fields.
"""
```

---

## 5. Frontend Architecture (React & Redux)

### 5.1 Project Structure

```
frontend/
├── public/
│   └── index.html
├── src/
│   ├── index.js
│   ├── App.jsx
│   ├── App.css
│   ├── store/
│   │   ├── index.js             # Redux store configuration
│   │   ├── formSlice.js         # Form state slice
│   │   └── chatSlice.js         # Chat state slice
│   ├── components/
│   │   ├── SplitScreenLayout.jsx
│   │   ├── InteractionForm/
│   │   │   ├── InteractionForm.jsx
│   │   │   ├── InteractionForm.css
│   │   │   ├── TopicsField.jsx
│   │   │   ├── MaterialsField.jsx
│   │   │   ├── SamplesField.jsx
│   │   │   ├── SentimentField.jsx
│   │   │   ├── OutcomesField.jsx
│   │   │   └── FollowUpField.jsx
│   │   └── ChatPanel/
│   │       ├── ChatPanel.jsx
│   │       ├── ChatPanel.css
│   │       ├── MessageBubble.jsx
│   │       └── ChatInput.jsx
│   └── services/
│       └── api.js               # Axios API client
├── package.json
└── .env
```

### 5.2 Component Tree

```mermaid
graph TD
    App["App"]
    App --> SSL["SplitScreenLayout"]
    SSL --> IF["InteractionForm (read-only)"]
    SSL --> CP["ChatPanel"]
    IF --> TF["TopicsField"]
    IF --> MF["MaterialsField"]
    IF --> SF["SamplesField"]
    IF --> SENT["SentimentField"]
    IF --> OF["OutcomesField"]
    IF --> FUF["FollowUpField"]
    CP --> MB["MessageBubble (×n)"]
    CP --> CI["ChatInput"]
```

### 5.3 Redux Store — Slice Definitions

#### `formSlice.js`

```javascript
// src/store/formSlice.js
import { createSlice } from '@reduxjs/toolkit';

const initialFormState = {
  interaction_id: null,
  hcp_name: '',
  interaction_date: '',
  topics_discussed: '',
  materials_shared: [],       // [{id, name}]
  samples_distributed: [],    // [{id, product_name, dosage, quantity}]
  sentiment: null,            // 'positive' | 'neutral' | 'negative' | null
  outcomes: '',
  follow_up_actions: '',
};

const formSlice = createSlice({
  name: 'form',
  initialState: initialFormState,
  reducers: {
    /**
     * Full replacement of form state — used after log_interaction tool
     */
    setFormState: (state, action) => {
      return { ...state, ...action.payload };
    },
    
    /**
     * Partial update — used after edit_interaction tool.
     * Only overwrites keys present in the payload.
     */
    updateFormFields: (state, action) => {
      const updates = action.payload;
      Object.keys(updates).forEach(key => {
        if (updates[key] !== null && updates[key] !== undefined) {
          state[key] = updates[key];
        }
      });
    },
    
    /**
     * Reset form to initial empty state
     */
    resetForm: () => initialFormState,
  },
});

export const { setFormState, updateFormFields, resetForm } = formSlice.actions;
export default formSlice.reducer;
```

#### `chatSlice.js`

```javascript
// src/store/chatSlice.js
import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { sendChatMessage } from '../services/api';
import { setFormState } from './formSlice';

// Async thunk: sends message to backend, dispatches form updates
export const sendMessage = createAsyncThunk(
  'chat/sendMessage',
  async (message, { getState, dispatch }) => {
    const state = getState();
    const response = await sendChatMessage({
      message,
      conversation_history: state.chat.messages.map(m => ({
        role: m.role,
        content: m.content,
      })),
      current_form_state: state.form,
    });
    
    // Update form state from backend response
    dispatch(setFormState(response.updated_form_state));
    
    return response;
  }
);

const chatSlice = createSlice({
  name: 'chat',
  initialState: {
    messages: [],    // [{role, content, timestamp}]
    isLoading: false,
    error: null,
  },
  reducers: {
    addUserMessage: (state, action) => {
      state.messages.push({
        role: 'user',
        content: action.payload,
        timestamp: new Date().toISOString(),
      });
    },
    clearChat: (state) => {
      state.messages = [];
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(sendMessage.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(sendMessage.fulfilled, (state, action) => {
        state.isLoading = false;
        state.messages.push({
          role: 'assistant',
          content: action.payload.ai_message,
          timestamp: new Date().toISOString(),
          tool_calls: action.payload.tool_calls_made,
        });
      })
      .addCase(sendMessage.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.error.message;
      });
  },
});

export const { addUserMessage, clearChat } = chatSlice.actions;
export default chatSlice.reducer;
```

#### `store/index.js`

```javascript
// src/store/index.js
import { configureStore } from '@reduxjs/toolkit';
import formReducer from './formSlice';
import chatReducer from './chatSlice';

export const store = configureStore({
  reducer: {
    form: formReducer,
    chat: chatReducer,
  },
});
```

### 5.4 API Service Layer

```javascript
// src/services/api.js
import axios from 'axios';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' },
});

export const sendChatMessage = async (chatRequest) => {
  const response = await apiClient.post('/api/chat', chatRequest);
  return response.data;
};

export const getMaterials = async () => {
  const response = await apiClient.get('/api/materials');
  return response.data;
};

export const getSamples = async () => {
  const response = await apiClient.get('/api/samples');
  return response.data;
};

export const submitInteraction = async (formState) => {
  const response = await apiClient.post('/api/interactions/submit', formState);
  return response.data;
};
```

### 5.5 Key UI Behavior

| Behavior | Implementation |
|----------|---------------|
| **Form is read-only** | All form inputs have `readOnly` or `disabled` attributes. No `onChange` handlers modify Redux state directly. |
| **Form reacts to Redux** | Components use `useSelector(state => state.form)` and render current values. When Redux updates (from backend response), React re-renders the form. |
| **Chat sends message** | `ChatInput` dispatches `addUserMessage(text)` then `sendMessage(text)`. The thunk POSTs to `/api/chat`, receives response, and dispatches `setFormState`. |
| **Loading state** | While `isLoading`, the chat shows a typing indicator. The send button is disabled. |
| **Sentiment with emojis** | Radio buttons display 😊 Positive, 😐 Neutral, 😟 Negative, styled with colored backgrounds. Read-only. |
| **Materials & Samples** | Displayed as tag/chip lists. New items appear with a slide-in animation when the AI adds them. |

---

## 6. Implementation Plan — 7-Phase Execution

### Phase 1: Project Scaffolding & Database Setup
**Goal:** Set up the monorepo, initialize both frontend and backend projects, create the PostgreSQL database, and define all tables with seed data.

**Tasks:**
1. Create project directory structure (`backend/`, `frontend/`)
2. Initialize Python virtual environment, install dependencies (`fastapi`, `uvicorn`, `sqlalchemy`, `langchain-groq`, `langgraph`, `langchain-core`, `python-dotenv`, `psycopg2-binary`, `asyncpg`)
3. Initialize React app with Create React App, install dependencies (`@reduxjs/toolkit`, `react-redux`, `axios`)
4. Create `.env` files for both backend (DB URL, Groq API key) and frontend (API URL)
5. Implement `backend/app/database.py` — SQLAlchemy engine, session factory, `get_db` dependency
6. Implement `backend/app/models.py` — All ORM models matching the schema in Section 2
7. Create database initialization script that creates tables + inserts seed data
8. Implement `backend/app/main.py` — FastAPI app with CORS middleware, startup event for DB init
9. Verify: Backend starts, database is created with seed data

### Phase 2: FastAPI Endpoints & Pydantic Schemas
**Goal:** Build all API endpoints and validate request/response contracts.

**Tasks:**
1. Implement `backend/app/schemas.py` — All Pydantic models from Section 3.2
2. Implement `backend/app/routers/data.py` — CRUD endpoints for materials, samples, HCP profiles
3. Implement `backend/app/routers/chat.py` — Chat endpoint (initially return a mock response)
4. Register routers in `main.py`
5. Verify: All endpoints return correct mock data, Swagger UI works at `/docs`

### Phase 3: LangGraph Agent & Tools
**Goal:** Implement the LangGraph agent with all 5 tools, connected to the Groq LLM.

**Tasks:**
1. Implement `backend/app/agent/state.py` — `AgentState` TypedDict
2. Implement `backend/app/agent/prompts.py` — System prompt from Section 4.5
3. Implement `backend/app/agent/tools.py` — All 5 tools using `@tool` decorator:
   - `log_interaction` — Extracts entities, creates form state, persists draft to DB
   - `edit_interaction` — Merges partial updates into existing form state
   - `suggest_follow_up` — Generates context-aware follow-up suggestions
   - `get_hcp_history` — Queries DB for HCP profile + past interactions
   - `search_product_knowledge` — Queries product knowledge base
4. Implement `backend/app/agent/graph.py` — StateGraph with agent node, tool node, conditional edges
5. Wire the `run_agent` function into the `/api/chat` endpoint
6. Verify: Send test messages via Swagger/curl, confirm tool calls are made and form state is returned

### Phase 4: React Frontend — Scaffold & Redux Store
**Goal:** Build the React app skeleton, Redux store, and API service layer.

**Tasks:**
1. Set up Google Inter font in `public/index.html`
2. Implement `src/store/formSlice.js` — Form state slice with `setFormState`, `updateFormFields`, `resetForm`
3. Implement `src/store/chatSlice.js` — Chat state slice with `sendMessage` async thunk
4. Implement `src/store/index.js` — Configure store
5. Implement `src/services/api.js` — Axios client
6. Wrap `App` with Redux `Provider`
7. Implement `src/components/SplitScreenLayout.jsx` — CSS Grid/Flexbox split-screen container
8. Verify: App renders with empty split-screen layout, Redux DevTools show state shape

### Phase 5: React Frontend — Form Panel (Left Side)
**Goal:** Build the read-only interaction form that renders from Redux state.

**Tasks:**
1. Implement `InteractionForm.jsx` — Container reading from `useSelector(state => state.form)`
2. Implement `TopicsField.jsx` — Read-only textarea
3. Implement `MaterialsField.jsx` — Tag/chip display with "Search/Add" button (visual only)
4. Implement `SamplesField.jsx` — Card list with "+ Add Sample" button (visual only)
5. Implement `SentimentField.jsx` — Read-only radio buttons with emoji icons
6. Implement `OutcomesField.jsx` — Read-only textarea
7. Implement `FollowUpField.jsx` — Read-only textarea
8. Style all components to match the reference screenshot (clean, professional, light theme)
9. Verify: Dispatching `setFormState` from Redux DevTools populates the form correctly

### Phase 6: React Frontend — Chat Panel (Right Side)
**Goal:** Build the conversational AI assistant panel.

**Tasks:**
1. Implement `ChatPanel.jsx` — Container with message list + input
2. Implement `MessageBubble.jsx` — User messages (right-aligned, blue/dark) and AI messages (left-aligned, light green)
3. Implement `ChatInput.jsx` — Text input + "Log" button, dispatches `addUserMessage` + `sendMessage`
4. Add typing indicator (animated dots) while `isLoading`
5. Add welcome message / instruction bubble at top of chat
6. Auto-scroll to latest message
7. Style to match reference screenshot (header with 🤖 AI Assistant, subtitle "Log Interaction details here via chat")
8. Verify: Full flow — type message → AI responds → form populates

### Phase 7: Polish, Integration Testing & README
**Goal:** End-to-end testing, UI polish, error handling, and documentation.

**Tasks:**
1. Test all 5 tools via chat:
   - Log a new interaction with full details
   - Edit specific fields
   - Request follow-up suggestions
   - Query HCP history
   - Search product knowledge
2. Add error handling: network errors display in chat, loading states, empty states
3. Add smooth CSS transitions for form field updates (highlight briefly when AI populates)
4. Add a "Submit Interaction" button at the bottom of the form (calls `/api/interactions/submit`)
5. Responsive design adjustments (mobile: stack vertically)
6. Create `README.md` with setup instructions, environment variables, and demo screenshots
7. Final verification: Clean install, `npm start` + `uvicorn`, full demo flow

---

## Appendix A: Environment Variables

### Backend (`.env`)
```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/hcp_crm
GROQ_API_KEY=gsk_your_api_key_here
LLM_MODEL=gemma2-9b-it
```

### Frontend (`.env`)
```env
REACT_APP_API_URL=http://localhost:8000
```

## Appendix B: Key Dependencies

### Backend (`requirements.txt`)
```
fastapi==0.115.0
uvicorn[standard]==0.30.0
sqlalchemy==2.0.35
psycopg2-binary==2.9.9
python-dotenv==1.0.1
langchain-groq==0.2.0
langgraph==0.2.34
langchain-core==0.3.10
pydantic==2.9.0
```

### Frontend (`package.json` dependencies)
```json
{
  "@reduxjs/toolkit": "^2.2.0",
  "react-redux": "^9.1.0",
  "axios": "^1.7.0",
  "react": "^18.3.0",
  "react-dom": "^18.3.0"
}
```

## Appendix C: Critical Constraints Checklist

- [ ] Form is read-only — user CANNOT type into form fields
- [ ] All form population happens via AI chat → tool calls → Redux updates
- [ ] LangGraph is used (not raw LLM calls)
- [ ] Groq API with `gemma2-9b-it` model
- [ ] Exactly 5 tools implemented
- [ ] `log_interaction` and `edit_interaction` are mandatory tools
- [ ] React + Redux for frontend
- [ ] FastAPI for backend
- [ ] PostgreSQL/MySQL database
- [ ] Google Inter font
