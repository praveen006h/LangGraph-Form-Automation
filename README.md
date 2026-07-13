# AI-First CRM HCP Module – Log Interaction Screen

This project is an AI-first Customer Relationship Management (CRM) system focusing on the Healthcare Professional (HCP) module. It provides a "Log Interaction Screen" allowing users to log interactions with HCPs via a structured form or a conversational chat interface powered by an AI Agent.

## Technologies Used
- **Frontend:** React UI with Redux (Vite/Bun)
- **Backend:** Python with FastAPI
- **AI Agent Framework:** LangGraph
- **LLM:** Groq API (gemma2-9b-it)
- **Database:** SQLite (SQLAlchemy)

## Project Structure
- `/frontend`: React application.
- `/backend`: FastAPI backend and LangGraph agent.

## Getting Started

### Prerequisites
- Node.js & Bun (for frontend)
- Python 3.x & uv (for backend)
- Groq API Key

### Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Set up environment variables. Create a `.env` file and add your Groq API key:
   ```env
   GROQ_API_KEY=your_api_key_here
   ```
3. Install dependencies:
   ```bash
   uv pip install -r requirements.txt
   ```
   *(or use your preferred Python virtual environment manager)*
4. Run the FastAPI server:
   ```bash
   uvicorn main:app --reload
   ```

### Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies using bun (or npm/yarn):
   ```bash
   bun install
   ```
3. Run the development server:
   ```bash
   bun run dev
   ```

## LangGraph Tools
The LangGraph agent is equipped with the following tools for sales-related activities:
1. **Log Interaction:** Captures interaction data, extracting entities and summarizing conversations using LLM.
2. **Edit Interaction:** Allows modification of existing logged interaction data.
3. **Get HCP Interactions:** Retrieves past interactions for a specific HCP.
4. **Search Interactions:** Searches across interactions.
5. **Get HCP Details:** Retrieves details about an HCP.
