"""
Pydantic schemas for API request/response validation
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class ExecutionStatus(str, Enum):
    """Execution status enum"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"


# Flow Schemas
class FlowBase(BaseModel):
    """Base flow schema"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    yaml_content: str = Field(..., min_length=1)


class FlowCreate(FlowBase):
    """Schema for creating a flow"""
    pass


class FlowUpdate(BaseModel):
    """Schema for updating a flow"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    yaml_content: Optional[str] = Field(None, min_length=1)


class FlowResponse(FlowBase):
    """Schema for flow response"""
    id: int
    is_valid: bool
    validation_errors: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Execution Schemas
class ExecutionCreate(BaseModel):
    """Schema for creating an execution"""
    flow_id: int
    model_override: Optional[str] = None
    inputs: Optional[Dict[str, Any]] = None


class ExecutionResponse(BaseModel):
    """Schema for execution response"""
    id: int
    flow_id: int
    status: ExecutionStatus
    model_override: Optional[str] = None
    inputs: Optional[Dict[str, Any]] = None
    outputs: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    logs: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# Schedule Schemas
class ScheduleBase(BaseModel):
    """Base schedule schema"""
    flow_id: int
    name: str = Field(..., min_length=1, max_length=255)
    cron_expression: str = Field(..., min_length=1, max_length=100)
    model_override: Optional[str] = None
    inputs: Optional[Dict[str, Any]] = None
    is_active: bool = True


class ScheduleCreate(ScheduleBase):
    """Schema for creating a schedule"""
    pass


class ScheduleUpdate(BaseModel):
    """Schema for updating a schedule"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    cron_expression: Optional[str] = Field(None, min_length=1, max_length=100)
    model_override: Optional[str] = None
    inputs: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class ScheduleResponse(ScheduleBase):
    """Schema for schedule response"""
    id: int
    last_run_at: Optional[datetime] = None
    next_run_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# MCP Tools Schema
class MCPTool(BaseModel):
    """Schema for MCP tool"""
    name: str
    description: str
    parameters: Optional[Dict[str, Any]] = None


class MCPToolsResponse(BaseModel):
    """Schema for MCP tools response"""
    tools: List[MCPTool]
    count: int


# WebSocket Messages
class WSMessage(BaseModel):
    """WebSocket message schema"""
    type: str
    data: Dict[str, Any]


# Validation Result
class ValidationResult(BaseModel):
    """Schema for validation result"""
    is_valid: bool
    errors: Optional[List[str]] = None
