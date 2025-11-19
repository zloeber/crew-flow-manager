"""
Flow execution service
"""
import logging
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.models import Execution, Flow, ExecutionStatus
from app.services.websocket_manager import websocket_manager

logger = logging.getLogger(__name__)


class FlowExecutor:
    """Executes CrewAI flows"""
    
    async def execute_flow(
        self,
        db: Session,
        execution_id: int,
        flow: Flow,
        model_override: Optional[str] = None,
        inputs: Optional[Dict[str, Any]] = None
    ):
        """
        Execute a CrewAI flow
        
        Args:
            db: Database session
            execution_id: Execution record ID
            flow: Flow model instance
            model_override: Optional model to override default
            inputs: Optional input parameters
        """
        execution = db.query(Execution).filter(Execution.id == execution_id).first()
        if not execution:
            logger.error(f"Execution {execution_id} not found")
            return
        
        try:
            # Update status to running
            execution.status = ExecutionStatus.RUNNING
            execution.started_at = datetime.utcnow()
            db.commit()
            
            # Send WebSocket update
            await websocket_manager.broadcast({
                "type": "execution_update",
                "data": {
                    "execution_id": execution_id,
                    "status": "running",
                    "started_at": execution.started_at.isoformat()
                }
            })
            
            # Simulate flow execution (in real implementation, use CrewAI here)
            logger.info(f"Executing flow {flow.name} (execution {execution_id})")
            
            # Build execution logs
            logs = []
            logs.append(f"[{datetime.utcnow().isoformat()}] Starting flow execution: {flow.name}")
            
            if model_override:
                logs.append(f"[{datetime.utcnow().isoformat()}] Using model override: {model_override}")
            
            if inputs:
                logs.append(f"[{datetime.utcnow().isoformat()}] Inputs: {inputs}")
            
            # For demonstration, simulate some work
            await asyncio.sleep(2)
            logs.append(f"[{datetime.utcnow().isoformat()}] Flow execution in progress...")
            
            await asyncio.sleep(2)
            logs.append(f"[{datetime.utcnow().isoformat()}] Flow execution completed successfully")
            
            # Update execution with success
            execution.status = ExecutionStatus.SUCCESS
            execution.completed_at = datetime.utcnow()
            execution.logs = "\n".join(logs)
            execution.outputs = {
                "result": "Flow executed successfully",
                "execution_time": (execution.completed_at - execution.started_at).total_seconds()
            }
            db.commit()
            
            # Send WebSocket update
            await websocket_manager.broadcast({
                "type": "execution_update",
                "data": {
                    "execution_id": execution_id,
                    "status": "success",
                    "completed_at": execution.completed_at.isoformat(),
                    "outputs": execution.outputs
                }
            })
            
            logger.info(f"Flow execution {execution_id} completed successfully")
            
        except Exception as e:
            logger.error(f"Error executing flow {execution_id}: {str(e)}")
            
            # Update execution with failure
            execution.status = ExecutionStatus.FAILED
            execution.completed_at = datetime.utcnow()
            execution.error_message = str(e)
            db.commit()
            
            # Send WebSocket update
            await websocket_manager.broadcast({
                "type": "execution_update",
                "data": {
                    "execution_id": execution_id,
                    "status": "failed",
                    "error": str(e)
                }
            })


flow_executor = FlowExecutor()
