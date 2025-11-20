"""
Database models for CrewAI Flow Manager
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.db.database import Base


class ExecutionStatus(str, enum.Enum):
    """Execution status enum"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Flow(Base):
    """Flow model - stores CrewAI flow definitions"""
    __tablename__ = "flows"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    yaml_content = Column(Text, nullable=False)
    is_valid = Column(Boolean, default=False)
    validation_errors = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    executions = relationship("Execution", back_populates="flow", cascade="all, delete-orphan")
    schedules = relationship("Schedule", back_populates="flow", cascade="all, delete-orphan")


class Execution(Base):
    """Execution model - tracks flow execution runs"""
    __tablename__ = "executions"
    
    id = Column(Integer, primary_key=True, index=True)
    flow_id = Column(Integer, ForeignKey("flows.id"), nullable=False)
    status = Column(Enum(ExecutionStatus), default=ExecutionStatus.PENDING, index=True)
    model_override = Column(String(255), nullable=True)
    llm_provider = Column(String(50), nullable=True)  # openai, ollama, custom
    llm_base_url = Column(String(500), nullable=True)  # Custom base URL for LLM
    inputs = Column(JSON, nullable=True)
    outputs = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    logs = Column(Text, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    flow = relationship("Flow", back_populates="executions")


class Schedule(Base):
    """Schedule model - manages scheduled flow executions"""
    __tablename__ = "schedules"
    
    id = Column(Integer, primary_key=True, index=True)
    flow_id = Column(Integer, ForeignKey("flows.id"), nullable=False)
    name = Column(String(255), nullable=False)
    cron_expression = Column(String(100), nullable=False)
    model_override = Column(String(255), nullable=True)
    llm_provider = Column(String(50), nullable=True)  # openai, ollama, custom
    llm_base_url = Column(String(500), nullable=True)  # Custom base URL for LLM
    inputs = Column(JSON, nullable=True)
    is_active = Column(Boolean, default=True)
    last_run_at = Column(DateTime, nullable=True)
    next_run_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    flow = relationship("Flow", back_populates="schedules")
