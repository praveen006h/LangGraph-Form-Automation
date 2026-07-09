from typing import Optional, List, Any
from datetime import date as Date, datetime
from sqlmodel import SQLModel, Field, Relationship
from pydantic import BaseModel
import uuid

# --- Database Models ---

class HCP(SQLModel, table=True):
    __tablename__ = "hcps"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str
    specialty: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    interactions: List["Interaction"] = Relationship(back_populates="hcp")

class Interaction(SQLModel, table=True):
    __tablename__ = "interactions"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hcp_id: Optional[uuid.UUID] = Field(default=None, foreign_key="hcps.id")
    date: Optional[Date] = None
    sentiment: Optional[str] = None
    topics_discussed: Optional[str] = None
    outcomes: Optional[str] = None
    follow_up_actions: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    hcp: Optional[HCP] = Relationship(back_populates="interactions")
    materials: List["Material"] = Relationship(back_populates="interaction")

class Material(SQLModel, table=True):
    __tablename__ = "materials"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    interaction_id: uuid.UUID = Field(foreign_key="interactions.id")
    material_type: str
    material_name: str

    interaction: Interaction = Relationship(back_populates="materials")

# --- API Schemas ---

class ChatRequest(BaseModel):
    session_id: Optional[str] = "default_session"
    message: Optional[str] = ""
    current_form_state: Optional[dict[str, Any]] = Field(default_factory=dict)

class ChatResponse(BaseModel):
    ai_reply: str
    updated_form_state: dict
