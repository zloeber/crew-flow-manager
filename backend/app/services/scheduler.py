"""
APScheduler service for scheduled flow executions
"""
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from datetime import datetime
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.database import SessionLocal, engine

logger = logging.getLogger(__name__)


class SchedulerService:
    """Manages scheduled flow executions"""
    
    def __init__(self):
        self.scheduler = None
        self._running = False
    
    def start(self):
        """Start the scheduler"""
        if self._running:
            logger.warning("Scheduler already running")
            return
        
        jobstores = {
            'default': SQLAlchemyJobStore(engine=engine)
        }
        
        self.scheduler = BackgroundScheduler(
            jobstores=jobstores,
            timezone=settings.SCHEDULER_TIMEZONE
        )
        
        self.scheduler.start()
        self._running = True
        logger.info("Scheduler started successfully")
    
    def shutdown(self):
        """Shutdown the scheduler"""
        if not self._running or not self.scheduler:
            return
        
        self.scheduler.shutdown(wait=False)
        self._running = False
        logger.info("Scheduler shutdown successfully")
    
    def is_running(self) -> bool:
        """Check if scheduler is running"""
        return self._running
    
    def add_job(
        self,
        schedule_id: int,
        flow_id: int,
        cron_expression: str,
        model_override: str = None,
        inputs: dict = None
    ):
        """
        Add a scheduled job
        
        Args:
            schedule_id: Schedule record ID
            flow_id: Flow ID to execute
            cron_expression: Cron expression for scheduling
            model_override: Optional model override
            inputs: Optional inputs
        """
        if not self._running:
            raise RuntimeError("Scheduler is not running")
        
        job_id = f"schedule_{schedule_id}"
        
        # Parse cron expression
        cron_parts = cron_expression.split()
        if len(cron_parts) != 5:
            raise ValueError("Invalid cron expression, must have 5 parts: minute hour day month day_of_week")
        
        trigger = CronTrigger(
            minute=cron_parts[0],
            hour=cron_parts[1],
            day=cron_parts[2],
            month=cron_parts[3],
            day_of_week=cron_parts[4],
            timezone=settings.SCHEDULER_TIMEZONE
        )
        
        self.scheduler.add_job(
            func=self._execute_scheduled_flow,
            trigger=trigger,
            id=job_id,
            args=[schedule_id, flow_id, model_override, inputs],
            replace_existing=True
        )
        
        logger.info(f"Added scheduled job {job_id} for flow {flow_id}")
    
    def remove_job(self, schedule_id: int):
        """Remove a scheduled job"""
        if not self._running:
            return
        
        job_id = f"schedule_{schedule_id}"
        try:
            self.scheduler.remove_job(job_id)
            logger.info(f"Removed scheduled job {job_id}")
        except Exception as e:
            logger.warning(f"Failed to remove job {job_id}: {str(e)}")
    
    def _execute_scheduled_flow(
        self,
        schedule_id: int,
        flow_id: int,
        model_override: str = None,
        inputs: dict = None
    ):
        """Execute a scheduled flow"""
        from app.models.models import Execution, Schedule, Flow
        from app.services.flow_executor import flow_executor
        import asyncio
        
        logger.info(f"Executing scheduled flow {flow_id} from schedule {schedule_id}")
        
        db = SessionLocal()
        try:
            # Get flow
            flow = db.query(Flow).filter(Flow.id == flow_id).first()
            if not flow:
                logger.error(f"Flow {flow_id} not found")
                return
            
            # Create execution record
            execution = Execution(
                flow_id=flow_id,
                model_override=model_override,
                inputs=inputs
            )
            db.add(execution)
            db.commit()
            db.refresh(execution)
            
            # Update schedule last run
            schedule = db.query(Schedule).filter(Schedule.id == schedule_id).first()
            if schedule:
                schedule.last_run_at = datetime.utcnow()
                db.commit()
            
            # Execute flow asynchronously
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(
                flow_executor.execute_flow(db, execution.id, flow, model_override, inputs)
            )
            loop.close()
            
        except Exception as e:
            logger.error(f"Error in scheduled execution: {str(e)}")
        finally:
            db.close()


scheduler_service = SchedulerService()
