"""
Execution management API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
import asyncio

from app.db.database import get_db
from app.models.models import Execution, Flow
from app.schemas.schemas import ExecutionCreate, ExecutionResponse
from app.services.flow_executor import flow_executor
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


def run_execution_in_background(
    db: Session,
    execution_id: int,
    flow: Flow,
    model_override: str = None,
    llm_provider: str = None,
    llm_base_url: str = None,
    inputs: dict = None
):
    """Run execution in background"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(
        flow_executor.execute_flow(db, execution_id, flow, model_override, llm_provider, llm_base_url, inputs)
    )
    loop.close()


@router.get("/", response_model=List[ExecutionResponse])
def list_executions(
    skip: int = 0,
    limit: int = 100,
    flow_id: int = None,
    db: Session = Depends(get_db)
):
    """List all executions, optionally filtered by flow_id"""
    query = db.query(Execution)
    
    if flow_id is not None:
        query = query.filter(Execution.flow_id == flow_id)
    
    executions = query.order_by(Execution.created_at.desc()).offset(skip).limit(limit).all()
    return executions


@router.get("/{execution_id}", response_model=ExecutionResponse)
def get_execution(execution_id: int, db: Session = Depends(get_db)):
    """Get a specific execution by ID"""
    execution = db.query(Execution).filter(Execution.id == execution_id).first()
    if not execution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Execution with id {execution_id} not found"
        )
    return execution


@router.post("/", response_model=ExecutionResponse, status_code=status.HTTP_201_CREATED)
def create_execution(
    execution_data: ExecutionCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Create and start a new execution"""
    # Get flow
    flow = db.query(Flow).filter(Flow.id == execution_data.flow_id).first()
    if not flow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Flow with id {execution_data.flow_id} not found"
        )
    
    # Check if flow is valid
    if not flow.is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot execute invalid flow. Please fix validation errors first."
        )
    
    # Create execution record
    execution = Execution(
        flow_id=execution_data.flow_id,
        model_override=execution_data.model_override,
        llm_provider=execution_data.llm_provider,
        llm_base_url=execution_data.llm_base_url,
        inputs=execution_data.inputs
    )
    
    db.add(execution)
    db.commit()
    db.refresh(execution)
    
    # Start execution in background
    background_tasks.add_task(
        run_execution_in_background,
        db,
        execution.id,
        flow,
        execution_data.model_override,
        execution_data.llm_provider,
        execution_data.llm_base_url,
        execution_data.inputs
    )
    
    logger.info(f"Created execution {execution.id} for flow {flow.id}")
    return execution


@router.delete("/{execution_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_execution(execution_id: int, db: Session = Depends(get_db)):
    """Delete an execution"""
    execution = db.query(Execution).filter(Execution.id == execution_id).first()
    if not execution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Execution with id {execution_id} not found"
        )
    
    db.delete(execution)
    db.commit()
    
    logger.info(f"Deleted execution {execution_id}")
    return None
