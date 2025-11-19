"""
Schedule management API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.db.database import get_db
from app.models.models import Schedule, Flow
from app.schemas.schemas import ScheduleCreate, ScheduleUpdate, ScheduleResponse
from app.services.scheduler import scheduler_service
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/", response_model=List[ScheduleResponse])
def list_schedules(
    skip: int = 0,
    limit: int = 100,
    flow_id: int = None,
    db: Session = Depends(get_db)
):
    """List all schedules, optionally filtered by flow_id"""
    query = db.query(Schedule)
    
    if flow_id is not None:
        query = query.filter(Schedule.flow_id == flow_id)
    
    schedules = query.offset(skip).limit(limit).all()
    return schedules


@router.get("/{schedule_id}", response_model=ScheduleResponse)
def get_schedule(schedule_id: int, db: Session = Depends(get_db)):
    """Get a specific schedule by ID"""
    schedule = db.query(Schedule).filter(Schedule.id == schedule_id).first()
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Schedule with id {schedule_id} not found"
        )
    return schedule


@router.post("/", response_model=ScheduleResponse, status_code=status.HTTP_201_CREATED)
def create_schedule(
    schedule_data: ScheduleCreate,
    db: Session = Depends(get_db)
):
    """Create a new schedule"""
    # Check if flow exists
    flow = db.query(Flow).filter(Flow.id == schedule_data.flow_id).first()
    if not flow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Flow with id {schedule_data.flow_id} not found"
        )
    
    # Create schedule
    schedule = Schedule(
        flow_id=schedule_data.flow_id,
        name=schedule_data.name,
        cron_expression=schedule_data.cron_expression,
        model_override=schedule_data.model_override,
        inputs=schedule_data.inputs,
        is_active=schedule_data.is_active
    )
    
    db.add(schedule)
    db.commit()
    db.refresh(schedule)
    
    # Add to scheduler if active
    if schedule.is_active:
        try:
            scheduler_service.add_job(
                schedule_id=schedule.id,
                flow_id=schedule.flow_id,
                cron_expression=schedule.cron_expression,
                model_override=schedule.model_override,
                inputs=schedule.inputs
            )
            
            # Calculate next run time
            job = scheduler_service.scheduler.get_job(f"schedule_{schedule.id}")
            if job:
                schedule.next_run_at = job.next_run_time.replace(tzinfo=None)
                db.commit()
                db.refresh(schedule)
                
        except Exception as e:
            logger.error(f"Error adding schedule to scheduler: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid cron expression: {str(e)}"
            )
    
    logger.info(f"Created schedule {schedule.id}: {schedule.name}")
    return schedule


@router.put("/{schedule_id}", response_model=ScheduleResponse)
def update_schedule(
    schedule_id: int,
    schedule_data: ScheduleUpdate,
    db: Session = Depends(get_db)
):
    """Update an existing schedule"""
    schedule = db.query(Schedule).filter(Schedule.id == schedule_id).first()
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Schedule with id {schedule_id} not found"
        )
    
    # Update fields
    if schedule_data.name is not None:
        schedule.name = schedule_data.name
    if schedule_data.cron_expression is not None:
        schedule.cron_expression = schedule_data.cron_expression
    if schedule_data.model_override is not None:
        schedule.model_override = schedule_data.model_override
    if schedule_data.inputs is not None:
        schedule.inputs = schedule_data.inputs
    if schedule_data.is_active is not None:
        schedule.is_active = schedule_data.is_active
    
    db.commit()
    db.refresh(schedule)
    
    # Update scheduler
    scheduler_service.remove_job(schedule_id)
    
    if schedule.is_active:
        try:
            scheduler_service.add_job(
                schedule_id=schedule.id,
                flow_id=schedule.flow_id,
                cron_expression=schedule.cron_expression,
                model_override=schedule.model_override,
                inputs=schedule.inputs
            )
            
            # Calculate next run time
            job = scheduler_service.scheduler.get_job(f"schedule_{schedule.id}")
            if job:
                schedule.next_run_at = job.next_run_time.replace(tzinfo=None)
                db.commit()
                db.refresh(schedule)
                
        except Exception as e:
            logger.error(f"Error updating schedule in scheduler: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid cron expression: {str(e)}"
            )
    else:
        schedule.next_run_at = None
        db.commit()
        db.refresh(schedule)
    
    logger.info(f"Updated schedule {schedule.id}: {schedule.name}")
    return schedule


@router.delete("/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_schedule(schedule_id: int, db: Session = Depends(get_db)):
    """Delete a schedule"""
    schedule = db.query(Schedule).filter(Schedule.id == schedule_id).first()
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Schedule with id {schedule_id} not found"
        )
    
    # Remove from scheduler
    scheduler_service.remove_job(schedule_id)
    
    db.delete(schedule)
    db.commit()
    
    logger.info(f"Deleted schedule {schedule_id}")
    return None
