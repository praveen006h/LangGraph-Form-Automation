from sqlalchemy import Column, Integer, String, Text, Boolean, Date, DateTime, ForeignKey, JSON, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime, date
from app.database import Base

class HCPProfile(Base):
    __tablename__ = "hcp_profiles"
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    specialty = Column(String(100))
    institution = Column(String(200))
    phone = Column(String(50))
    email = Column(String(100))
    npi_number = Column(String(50))
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    interactions = relationship("Interaction", back_populates="hcp")

class Interaction(Base):
    __tablename__ = "interactions"
    id = Column(Integer, primary_key=True, index=True)
    hcp_id = Column(Integer, ForeignKey("hcp_profiles.id", ondelete="SET NULL"), nullable=True)
    interaction_date = Column(Date, default=date.today)
    topics_discussed = Column(Text)
    sentiment = Column(String(20))  # positive, neutral, negative
    outcomes = Column(Text)
    follow_up_actions = Column(Text)
    status = Column(String(20), default="draft")  # draft, submitted
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    hcp = relationship("HCPProfile", back_populates="interactions")
    materials = relationship("InteractionMaterial", back_populates="interaction", cascade="all, delete-orphan")
    samples = relationship("InteractionSample", back_populates="interaction", cascade="all, delete-orphan")
    conversations = relationship("ConversationHistory", back_populates="interaction", cascade="all, delete-orphan")

class Material(Base):
    __tablename__ = "materials"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    type = Column(String(50), default="other")
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class InteractionMaterial(Base):
    __tablename__ = "interaction_materials"
    id = Column(Integer, primary_key=True, index=True)
    interaction_id = Column(Integer, ForeignKey("interactions.id", ondelete="CASCADE"))
    material_id = Column(Integer, ForeignKey("materials.id", ondelete="CASCADE"))
    shared_at = Column(DateTime, default=datetime.utcnow)
    interaction = relationship("Interaction", back_populates="materials")
    material = relationship("Material")
    __table_args__ = (UniqueConstraint('interaction_id', 'material_id'),)

class Sample(Base):
    __tablename__ = "samples"
    id = Column(Integer, primary_key=True, index=True)
    product_name = Column(String(200), nullable=False)
    dosage = Column(String(50))
    quantity_available = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class InteractionSample(Base):
    __tablename__ = "interaction_samples"
    id = Column(Integer, primary_key=True, index=True)
    interaction_id = Column(Integer, ForeignKey("interactions.id", ondelete="CASCADE"))
    sample_id = Column(Integer, ForeignKey("samples.id", ondelete="CASCADE"))
    quantity_distributed = Column(Integer, default=1)
    distributed_at = Column(DateTime, default=datetime.utcnow)
    interaction = relationship("Interaction", back_populates="samples")
    sample = relationship("Sample")
    __table_args__ = (UniqueConstraint('interaction_id', 'sample_id'),)

class ProductKnowledge(Base):
    __tablename__ = "product_knowledge"
    id = Column(Integer, primary_key=True, index=True)
    product_name = Column(String(200), nullable=False)
    description = Column(Text)
    indications = Column(Text)
    contraindications = Column(Text)
    key_studies = Column(Text)
    competitive_advantages = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ConversationHistory(Base):
    __tablename__ = "conversation_history"
    id = Column(Integer, primary_key=True, index=True)
    interaction_id = Column(Integer, ForeignKey("interactions.id", ondelete="SET NULL"), nullable=True)
    role = Column(String(20), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    tool_calls = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    interaction = relationship("Interaction", back_populates="conversations")
