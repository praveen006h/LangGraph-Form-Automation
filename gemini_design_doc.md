# AI-First CRM HCP Module: Technical Design Document

This document outlines the architecture, data models, AI agent structure, and implementation plan for the AI-First CRM HCP Module (Log Interaction Screen). The application uses a split-screen design where an AI chat assistant entirely controls a structured logging form.

---

## 1. System Architecture Overview

The system operates on a state-driven architecture where the AI Assistant is the sole mutation engine for the form's data.

*   **Frontend (React + Redux):** Renders the UI and maintains two core states: the `chatHistory` and the `draftFormState`. Form input fields are strictly `readOnly` to prevent manual entry. The "Log" button in the chat panel acts as the message submission trigger.
*   **Backend (FastAPI):** Acts as the orchestrator. It receives chat messages alongside the current `draftFormState`. It invokes the LangGraph agent, passing the conversation history and form state.
*   **AI Agent (LangGraph + Groq Gemma2-9b-it):** Analyzes the user's input. It decides whether to converse natively or invoke tools. When tools like `log_interaction` or `edit_interaction` are called, they return a JSON patch/update for the form state.
*   **Data Flow:**
    1. User types in the chat: *"Met Dr. Smith, sentiment was positive."*
    2. React dispatches the message and current form state to FastAPI `/api/chat`.
    3. LangGraph agent processes the state, calls the `log_interaction` tool.
    4. Tool updates the internal state graph.
    5. Agent generates a natural language reply.
    6. FastAPI returns both the `ai_reply` and the `updated_form_state` to React.
    7. Redux updates the UI automatically.

---

## 2. Database Schema (PostgreSQL/MySQL)

We will use an ORM (like SQLAlchemy or SQLModel) to manage the schema.

### Table: `hcps`
Stores Healthcare Professional details.
*   `id` (UUID, Primary Key)
*   `name` (String, e.g., "Dr. Smith")
*   `specialty` (String)
*   `created_at` (DateTime)

### Table: `interactions`
Stores the finalized logs.
*   `id` (UUID, Primary Key)
*   `hcp_id` (UUID, Foreign Key -> `hcps.id`)
*   `date` (Date)
*   `sentiment` (Enum: 'Positive', 'Neutral', 'Negative')
*   `topics_discussed` (Text)
*   `outcomes` (Text)
*   `follow_up_actions` (Text)
*   `created_at` (DateTime)

### Table: `materials`
*   `id` (UUID, Primary Key)
*   `interaction_id` (UUID, Foreign Key -> `interactions.id`)
*   `material_type` (Enum: 'Brochure', 'Sample', 'Digital Asset')
*   `material_name` (String)

---

## 3. API Specification (FastAPI)

### `POST /api/chat`
The core endpoint driving the split-screen interaction.
**Request (Pydantic Schema):**
```python
class ChatRequest(BaseModel):
    session_id: str
    message: str
    current_form_state: dict # The current draft state from Redux
```

**Response (Pydantic Schema):**
```python
class ChatResponse(BaseModel):
    ai_reply: str
    updated_form_state: dict # The modified state after tool execution
```

### `POST /api/interactions`
Saves the finalized draft form to the database once the user confirms it's complete.

---

## 4. LangGraph Agent Design (Deep Dive)

### State Graph Structure
The agent's memory must track both the conversation and the evolving form.
```python
from typing import TypedDict, Annotated, Sequence
import operator
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    form_state: dict
```

### Nodes and Edges
*   **Agent Node:** Calls the LLM (`gemma2-9b-it` via Groq) bound with the 5 tools.
*   **Tool Node:** Executes the requested tool, passing in the current `form_state` and returning the mutated `form_state`.
*   **Edges:** Conditional edge from Agent Node -> Tool Node if `tool_calls` are present. Tool Node always routes back to Agent Node to generate the final chat response summarizing the action.

### The 5 Tools Specification

1.  **`log_interaction` (Mandatory)**
    *   *Description:* Extracts entities from a new interaction summary and completely populates the form state.
    *   *Input:* `hcp_name`, `date`, `sentiment`, `topics`, `materials_shared`, `samples_distributed`
    *   *Behavior:* Merges extracted data into the `form_state` dict.

2.  **`edit_interaction` (Mandatory)**
    *   *Description:* Modifies specific fields based on user corrections.
    *   *Input:* `field_to_update` (Enum), `new_value`
    *   *Behavior:* Specifically targets a key in `form_state` and replaces its value, leaving others untouched.

3.  **`suggest_follow_up` (Custom Tool 1)**
    *   *Description:* Analyzes the `topics_discussed` and `sentiment` to suggest tactical next steps.
    *   *Input:* None (reads from `form_state`)
    *   *Behavior:* Returns a list of suggested actions which the AI then relays to the user via chat, asking if they want to add it to the form.

4.  **`get_hcp_history` (Custom Tool 2)**
    *   *Description:* Retrieves past interaction summaries for a mentioned HCP from the DB.
    *   *Input:* `hcp_name`
    *   *Behavior:* Queries the database and returns past context to the LLM to personalize the conversation.

5.  **`search_knowledge_base` (Custom Tool 3)**
    *   *Description:* Searches clinical guidelines or product details if the rep asks a question during logging.
    *   *Input:* `search_query`
    *   *Behavior:* Performs a vector search (or mock text search) on a static knowledge base and returns facts to the LLM.

### System Prompt Strategy
```text
You are an AI assistant designed to log interactions for pharmaceutical sales reps. 
You control a form interface. The user cannot edit the form themselves; they rely on you.
When the user describes an interaction, use the 'log_interaction' tool to populate the form.
If the user corrects a mistake, use the 'edit_interaction' tool.
Always confirm to the user what fields you updated.
Current Form State: {form_state}
```

---

## 5. Frontend Architecture (React & Redux)

### Component Tree
*   `<App>`
    *   `<SplitScreenLayout>` (CSS Grid / Flexbox)
        *   `<FormPanel>` (Left side)
            *   `<TopicsTextarea readOnly />`
            *   `<MaterialsList />`
            *   `<SentimentRadioGroup disabled />`
            *   `<OutcomesTextarea readOnly />`
        *   `<ChatPanel>` (Right side)
            *   `<MessageList />`
            *   `<ChatInput>` + `<LogButton>`

### Redux Slices
1.  **`formSlice`:** 
    ```typescript
    interface FormState {
      hcpName: string | null;
      sentiment: 'Positive' | 'Neutral' | 'Negative' | null;
      topics: string;
      materials: string[];
      samples: string[];
      outcomes: string;
      followUp: string;
    }
    ```
2.  **`chatSlice`:** Tracks an array of `{ role: 'user' | 'assistant', content: string }`.

**Sync Flow:** When the API returns a response, Redux dispatches `updateForm(response.updated_form_state)` and `addMessage(response.ai_reply)`.

---

## 6. Implementation Plan / Step-by-Step AI Prompts

*Pass these exact prompts one by one to an AI coding assistant to build the project.*

**Phase 1: DB & Backend Scaffold**
> "Set up a FastAPI project in Python. Create a SQLAlchemy (or SQLModel) database schema matching this design doc: `hcps`, `interactions`, and `materials` tables. Include a SQLite or Postgres connection setup. Create Pydantic schemas for the `/api/chat` request (session_id, message, form_state) and response (ai_reply, updated_form_state)."

**Phase 2: LangGraph State & Tools Definition**
> "Using the FastAPI project from Phase 1, install LangGraph, LangChain, and `langchain-groq`. Define the `AgentState` TypedDict containing `messages` and `form_state`. Create Python functions with `@tool` decorators for the 5 tools defined in the design doc: `log_interaction`, `edit_interaction`, `suggest_follow_up`, `get_hcp_history`, and `search_knowledge_base`. Ensure they are designed to mutate or read the `form_state` dict."

**Phase 3: LangGraph Node/Edge Wiring**
> "Now, wire the LangGraph agent. Create the `call_model` node that binds the 5 tools to the Groq `gemma2-9b-it` model and injects the system prompt. Create the `tool_node` that executes the tools and passes the mutated `form_state` back. Compile the graph and integrate it into the `/api/chat` FastAPI route so it processes the incoming request and returns the final AI reply and updated form state."

**Phase 4: React Scaffold & Redux Setup**
> "Initialize a new React (Vite) project. Install Redux Toolkit and TailwindCSS (or setup vanilla CSS for styling). Create two Redux slices: `formSlice` (with fields for topics, materials, samples, sentiment, outcomes, follow_up) and `chatSlice` (for message history). Set up the Redux store and create an async thunk `sendMessage` that POSTs to the FastAPI `/api/chat` endpoint and updates both slices with the response."

**Phase 5: Split-Screen UI Layout**
> "Build the main UI layout in React. Create a split-screen design. On the left, create the `FormPanel` component containing read-only form elements that reflect the Redux `formSlice` state exactly. Ensure it uses the Google Inter font and looks clean and professional. On the right, build the `ChatPanel` displaying the Redux `chatSlice` messages, with an input box and a 'Log' (send) button at the bottom."

**Phase 6: Integration & Polish**
> "Run both the frontend and backend servers. Fix any CORS issues. Ensure that when a natural language prompt is sent via the chat panel, the LangGraph backend accurately extracts entities, calls the tools, and the React UI dynamically populates the read-only form fields in real-time. Add a final 'Save Interaction' button on the frontend that sends the completed form to a new `/api/interactions` endpoint to save in the database."
