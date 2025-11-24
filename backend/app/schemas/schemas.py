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
    llm_provider: Optional[str] = None  # openai, ollama, custom
    llm_base_url: Optional[str] = None  # Custom base URL for LLM
    inputs: Optional[Dict[str, Any]] = None
    selected_tasks: Optional[List[str]] = None  # Optional list of task descriptions to execute


class ExecutionResponse(BaseModel):
    """Schema for execution response"""
    id: int
    flow_id: int
    status: ExecutionStatus
    model_override: Optional[str] = None
    llm_provider: Optional[str] = None
    llm_base_url: Optional[str] = None
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
    llm_provider: Optional[str] = None  # openai, ollama, custom
    llm_base_url: Optional[str] = None  # Custom base URL for LLM
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
    llm_provider: Optional[str] = None
    llm_base_url: Optional[str] = None
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


# MCP Server Schemas
class MCPServerBase(BaseModel):
    """Base MCP Server schema"""
    name: str = Field(..., min_length=1, max_length=255)
    command: str = Field(..., min_length=1)
    args: Optional[List[str]] = None
    env: Optional[Dict[str, str]] = None
    type: str = Field(default="stdio")
    url: Optional[str] = None
    is_active: bool = True


class MCPServerCreate(MCPServerBase):
    """Schema for creating an MCP server"""
    pass


class MCPServerUpdate(BaseModel):
    """Schema for updating an MCP server"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    command: Optional[str] = Field(None, min_length=1)
    args: Optional[List[str]] = None
    env: Optional[Dict[str, str]] = None
    type: Optional[str] = None
    url: Optional[str] = None
    is_active: Optional[bool] = None


class MCPServerResponse(MCPServerBase):
    """Schema for MCP server response"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class MCPServersImport(BaseModel):
    """Schema for importing MCP servers"""
    servers: Dict[str, Dict[str, Any]]


# MCP Tools Schema
class MCPTool(BaseModel):
    """Schema for MCP tool"""
    name: str
    description: str
    server: str  # Server name that provides this tool
    parameters: Optional[Dict[str, Any]] = None


class MCPToolsResponse(BaseModel):
    """Schema for MCP tools response"""
    tools: List[MCPTool]
    count: int
    servers: List[str]  # List of server names


# Flow Import/Export Schemas
class FlowExport(BaseModel):
    """Schema for exporting a flow"""
    name: str
    description: Optional[str] = None
    yaml_content: str


class FlowsExport(BaseModel):
    """Schema for exporting multiple flows"""
    flows: List[FlowExport]


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
