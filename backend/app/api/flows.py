"""
Flow management API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List
import yaml
import io

from app.db.database import get_db
from app.models.models import Flow
from app.schemas.schemas import (
    FlowCreate, FlowUpdate, FlowResponse, ValidationResult,
    FlowExport, FlowsExport
)
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


@router.post("/import", response_model=FlowResponse, status_code=status.HTTP_201_CREATED)
async def import_flow(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Import a flow from a YAML file"""
    if not file.filename.endswith(('.yaml', '.yml')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a YAML file (.yaml or .yml)"
        )
    
    try:
        content = await file.read()
        yaml_content = content.decode('utf-8')
        
        # Parse YAML to extract name and description
        data = yaml.safe_load(yaml_content)
        name = data.get('name', file.filename.replace('.yaml', '').replace('.yml', ''))
        description = data.get('description', '')
        
        # Check if flow with same name exists
        existing = db.query(Flow).filter(Flow.name == name).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Flow with name '{name}' already exists"
            )
        
        # Validate YAML
        is_valid, errors = flow_validator.validate(yaml_content)
        
        # Create flow
        flow = Flow(
            name=name,
            description=description,
            yaml_content=yaml_content,
            is_valid=is_valid,
            validation_errors={"errors": errors} if errors else None
        )
        
        db.add(flow)
        db.commit()
        db.refresh(flow)
        
        logger.info(f"Imported flow {flow.id}: {flow.name}")
        return flow
        
    except yaml.YAMLError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid YAML format: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error importing flow: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error importing flow: {str(e)}"
        )


@router.get("/{flow_id}/export")
def export_flow(flow_id: int, db: Session = Depends(get_db)):
    """Export a flow as a YAML file"""
    flow = db.query(Flow).filter(Flow.id == flow_id).first()
    if not flow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Flow with id {flow_id} not found"
        )
    
    # Create YAML content
    yaml_content = flow.yaml_content
    
    # Create a file-like object
    file_stream = io.BytesIO(yaml_content.encode('utf-8'))
    
    # Return as streaming response
    return StreamingResponse(
        file_stream,
        media_type="application/x-yaml",
        headers={
            "Content-Disposition": f"attachment; filename={flow.name.replace(' ', '_')}.yaml"
        }
    )


@router.post("/export-multiple")
def export_multiple_flows(flow_ids: List[int], db: Session = Depends(get_db)):
    """Export multiple flows as a single YAML file"""
    flows = db.query(Flow).filter(Flow.id.in_(flow_ids)).all()
    
    if not flows:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No flows found with the provided IDs"
        )
    
    # Create combined YAML content
    combined_content = "# Multiple Flows Export\n# Each flow is separated by ---\n\n"
    for i, flow in enumerate(flows):
        if i > 0:
            combined_content += "\n---\n\n"
        combined_content += flow.yaml_content
    
    # Create a file-like object
    file_stream = io.BytesIO(combined_content.encode('utf-8'))
    
    # Return as streaming response
    return StreamingResponse(
        file_stream,
        media_type="application/x-yaml",
        headers={
            "Content-Disposition": f"attachment; filename=flows_export.yaml"
        }
    )


@router.get("/{flow_id}/tasks")
def get_flow_tasks(flow_id: int, db: Session = Depends(get_db)):
    """Get list of tasks from a flow's YAML configuration"""
    flow = db.query(Flow).filter(Flow.id == flow_id).first()
    if not flow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Flow with id {flow_id} not found"
        )
    
    try:
        # Parse YAML to extract tasks
        data = yaml.safe_load(flow.yaml_content)
        tasks = data.get('tasks', [])
        
        # Format task list with descriptions
        task_list = []
        for i, task in enumerate(tasks):
            task_info = {
                'index': i,
                'description': task.get('description', f'Task {i+1}'),
                'agent': task.get('agent', 'Unknown'),
                'expected_output': task.get('expected_output', 'Not specified')
            }
            task_list.append(task_info)
        
        return {
            'flow_id': flow_id,
            'flow_name': flow.name,
            'tasks': task_list,
            'total_tasks': len(task_list)
        }
        
    except yaml.YAMLError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid YAML format: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error getting flow tasks: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting flow tasks: {str(e)}"
        )
