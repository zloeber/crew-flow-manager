"""
Flow management API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.models.models import Flow
from app.schemas.schemas import FlowCreate, FlowUpdate, FlowResponse, ValidationResult
from app.services.flow_validator import flow_validator
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/", response_model=List[FlowResponse])
def list_flows(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all flows"""
    flows = db.query(Flow).offset(skip).limit(limit).all()
    return flows


@router.get("/{flow_id}", response_model=FlowResponse)
def get_flow(flow_id: int, db: Session = Depends(get_db)):
    """Get a specific flow by ID"""
    flow = db.query(Flow).filter(Flow.id == flow_id).first()
    if not flow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Flow with id {flow_id} not found"
        )
    return flow


@router.post("/", response_model=FlowResponse, status_code=status.HTTP_201_CREATED)
def create_flow(flow_data: FlowCreate, db: Session = Depends(get_db)):
    """Create a new flow"""
    # Check if flow with same name exists
    existing = db.query(Flow).filter(Flow.name == flow_data.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Flow with name '{flow_data.name}' already exists"
        )
    
    # Validate YAML
    is_valid, errors = flow_validator.validate(flow_data.yaml_content)
    
    # Create flow
    flow = Flow(
        name=flow_data.name,
        description=flow_data.description,
        yaml_content=flow_data.yaml_content,
        is_valid=is_valid,
        validation_errors={"errors": errors} if errors else None
    )
    
    db.add(flow)
    db.commit()
    db.refresh(flow)
    
    logger.info(f"Created flow {flow.id}: {flow.name}")
    return flow


@router.put("/{flow_id}", response_model=FlowResponse)
def update_flow(
    flow_id: int,
    flow_data: FlowUpdate,
    db: Session = Depends(get_db)
):
    """Update an existing flow"""
    flow = db.query(Flow).filter(Flow.id == flow_id).first()
    if not flow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Flow with id {flow_id} not found"
        )
    
    # Check name uniqueness if changing name
    if flow_data.name and flow_data.name != flow.name:
        existing = db.query(Flow).filter(Flow.name == flow_data.name).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Flow with name '{flow_data.name}' already exists"
            )
    
    # Update fields
    if flow_data.name is not None:
        flow.name = flow_data.name
    if flow_data.description is not None:
        flow.description = flow_data.description
    if flow_data.yaml_content is not None:
        flow.yaml_content = flow_data.yaml_content
        # Re-validate
        is_valid, errors = flow_validator.validate(flow_data.yaml_content)
        flow.is_valid = is_valid
        flow.validation_errors = {"errors": errors} if errors else None
    
    db.commit()
    db.refresh(flow)
    
    logger.info(f"Updated flow {flow.id}: {flow.name}")
    return flow


@router.delete("/{flow_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_flow(flow_id: int, db: Session = Depends(get_db)):
    """Delete a flow"""
    flow = db.query(Flow).filter(Flow.id == flow_id).first()
    if not flow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Flow with id {flow_id} not found"
        )
    
    db.delete(flow)
    db.commit()
    
    logger.info(f"Deleted flow {flow_id}")
    return None


@router.post("/validate", response_model=ValidationResult)
def validate_flow_yaml(yaml_content: str):
    """Validate a flow YAML without saving it"""
    is_valid, errors = flow_validator.validate(yaml_content)
    return ValidationResult(is_valid=is_valid, errors=errors if errors else None)
