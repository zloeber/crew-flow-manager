"""
Flow execution service
"""
import logging
import asyncio
import yaml
from typing import Dict, Any, Optional, List
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
        llm_provider: Optional[str] = None,
        llm_base_url: Optional[str] = None,
        inputs: Optional[Dict[str, Any]] = None,
        selected_tasks: Optional[List[str]] = None
    ):
        """
        Execute a CrewAI flow
        
        Args:
            db: Database session
            execution_id: Execution record ID
            flow: Flow model instance
            model_override: Optional model to override default
            llm_provider: LLM provider (openai, ollama, custom)
            llm_base_url: Custom base URL for LLM endpoint
            inputs: Optional input parameters
            selected_tasks: Optional list of task descriptions to execute (executes all if None)
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
            
            # Parse YAML to get flow configuration
            logger.info(f"Executing flow {flow.name} (execution {execution_id})")
            flow_config = yaml.safe_load(flow.yaml_content)
            
            # Build execution logs
            logs = []
            logs.append(f"[{datetime.utcnow().isoformat()}] Starting flow execution: {flow.name}")
            
            if model_override:
                logs.append(f"[{datetime.utcnow().isoformat()}] Using model override: {model_override}")
            
            if llm_provider:
                logs.append(f"[{datetime.utcnow().isoformat()}] LLM Provider: {llm_provider}")
            
            if llm_base_url:
                logs.append(f"[{datetime.utcnow().isoformat()}] LLM Base URL: {llm_base_url}")
            
            if inputs:
                logs.append(f"[{datetime.utcnow().isoformat()}] Inputs: {inputs}")
            
            if selected_tasks:
                logs.append(f"[{datetime.utcnow().isoformat()}] Selected tasks: {', '.join(selected_tasks)}")
            
            # Execute the flow using CrewAI
            result = await self._execute_crewai_flow(
                flow_config, 
                logs, 
                model_override, 
                llm_provider, 
                llm_base_url, 
                inputs,
                selected_tasks
            )
            
            # Update execution with success
            execution.status = ExecutionStatus.SUCCESS
            execution.completed_at = datetime.utcnow()
            execution.logs = "\n".join(logs)
            execution.outputs = result
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
    
    async def _execute_crewai_flow(
        self,
        flow_config: Dict[str, Any],
        logs: List[str],
        model_override: Optional[str] = None,
        llm_provider: Optional[str] = None,
        llm_base_url: Optional[str] = None,
        inputs: Optional[Dict[str, Any]] = None,
        selected_tasks: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Execute CrewAI flow with actual agents and tasks
        
        Args:
            flow_config: Parsed YAML flow configuration
            logs: List to append execution logs to
            model_override: Optional model override
            llm_provider: LLM provider
            llm_base_url: LLM base URL
            inputs: Input parameters
            selected_tasks: List of task descriptions to execute
            
        Returns:
            Dictionary with execution results
        """
        try:
            # Import CrewAI components
            from crewai import Agent, Task, Crew, Process
            from langchain_openai import ChatOpenAI
            import os
            
            logs.append(f"[{datetime.utcnow().isoformat()}] Parsing flow configuration...")
            
            # Get agents and tasks from config
            agents_config = flow_config.get('agents', [])
            tasks_config = flow_config.get('tasks', [])
            
            if not agents_config:
                logs.append(f"[{datetime.utcnow().isoformat()}] No agents defined in flow")
                return {"result": "No agents to execute", "tasks_executed": 0}
            
            if not tasks_config:
                logs.append(f"[{datetime.utcnow().isoformat()}] No tasks defined in flow")
                return {"result": "No tasks to execute", "tasks_executed": 0}
            
            # Setup LLM
            llm_config = {}
            if model_override:
                llm_config['model'] = model_override
            if llm_base_url:
                llm_config['base_url'] = llm_base_url
            
            # Set API key from environment or provider
            api_key_override = None
            if llm_provider == 'ollama':
                api_key_override = 'ollama'  # Dummy key for Ollama
                if not llm_config.get('base_url'):
                    llm_config['base_url'] = 'http://localhost:11434/v1'
            
            # Create LLM instance if configured
            llm = None
            if llm_config:
                try:
                    # Only set env var temporarily if needed
                    if api_key_override:
                        llm_config['api_key'] = api_key_override
                    llm = ChatOpenAI(**llm_config)
                    logs.append(f"[{datetime.utcnow().isoformat()}] Configured LLM: {llm_config}")
                except Exception as e:
                    logs.append(f"[{datetime.utcnow().isoformat()}] Warning: Could not configure LLM: {str(e)}")
            
            # Create agents
            agents = {}
            logs.append(f"[{datetime.utcnow().isoformat()}] Creating {len(agents_config)} agent(s)...")
            
            for agent_config in agents_config:
                role = agent_config.get('role')
                if not role:
                    continue
                    
                agent_params = {
                    'role': role,
                    'goal': agent_config.get('goal', f'Complete tasks as {role}'),
                    'backstory': agent_config.get('backstory', f'You are a {role}'),
                    'verbose': True,
                    'allow_delegation': agent_config.get('allow_delegation', False)
                }
                
                if llm:
                    agent_params['llm'] = llm
                
                agents[role] = Agent(**agent_params)
                logs.append(f"[{datetime.utcnow().isoformat()}]   - Created agent: {role}")
            
            # Filter tasks if selected_tasks is provided
            tasks_to_execute = tasks_config
            if selected_tasks:
                tasks_to_execute = [
                    task for task in tasks_config 
                    if task.get('description') in selected_tasks
                ]
                logs.append(f"[{datetime.utcnow().isoformat()}] Filtered to {len(tasks_to_execute)} selected task(s)")
            
            # Create tasks
            tasks = []
            logs.append(f"[{datetime.utcnow().isoformat()}] Creating {len(tasks_to_execute)} task(s)...")
            
            for task_config in tasks_to_execute:
                description = task_config.get('description')
                agent_role = task_config.get('agent')
                
                if not description or not agent_role:
                    logs.append(f"[{datetime.utcnow().isoformat()}]   - Skipping invalid task configuration")
                    continue
                
                if agent_role not in agents:
                    logs.append(f"[{datetime.utcnow().isoformat()}]   - Warning: Agent '{agent_role}' not found for task")
                    continue
                
                task_params = {
                    'description': description,
                    'agent': agents[agent_role],
                    'expected_output': task_config.get('expected_output', 'Task completed')
                }
                
                tasks.append(Task(**task_params))
                logs.append(f"[{datetime.utcnow().isoformat()}]   - Created task: {description[:50]}...")
            
            if not tasks:
                logs.append(f"[{datetime.utcnow().isoformat()}] No valid tasks to execute")
                return {"result": "No valid tasks", "tasks_executed": 0}
            
            # Create and run crew
            logs.append(f"[{datetime.utcnow().isoformat()}] Starting crew execution...")
            
            crew = Crew(
                agents=list(agents.values()),
                tasks=tasks,
                process=Process.sequential,
                verbose=True
            )
            
            # Execute in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            start_time = datetime.utcnow()
            result = await loop.run_in_executor(None, crew.kickoff, inputs or {})
            end_time = datetime.utcnow()
            execution_time = (end_time - start_time).total_seconds()
            
            logs.append(f"[{datetime.utcnow().isoformat()}] Crew execution completed successfully")
            
            # Format result
            return {
                "result": str(result),
                "tasks_executed": len(tasks),
                "agents_used": len(agents),
                "execution_time": execution_time
            }
            
        except ImportError as e:
            # CrewAI not installed, fallback to simulation
            logs.append(f"[{datetime.utcnow().isoformat()}] CrewAI not available, using simulation mode")
            logs.append(f"[{datetime.utcnow().isoformat()}] Error: {str(e)}")
            
            # Simulate execution
            await asyncio.sleep(2)
            logs.append(f"[{datetime.utcnow().isoformat()}] Simulating task execution...")
            
            tasks_to_simulate = flow_config.get('tasks', [])
            if selected_tasks:
                tasks_to_simulate = [
                    task for task in tasks_to_simulate 
                    if task.get('description') in selected_tasks
                ]
            
            for i, task in enumerate(tasks_to_simulate):
                await asyncio.sleep(1)
                task_desc = task.get('description', f'Task {i+1}')
                logs.append(f"[{datetime.utcnow().isoformat()}]   - Simulated: {task_desc[:60]}...")
            
            logs.append(f"[{datetime.utcnow().isoformat()}] Simulation completed")
            
            return {
                "result": "Simulated execution (CrewAI not installed)",
                "tasks_executed": len(tasks_to_simulate),
                "simulation": True
            }
        
        except Exception as e:
            logs.append(f"[{datetime.utcnow().isoformat()}] Error during execution: {str(e)}")
            raise


flow_executor = FlowExecutor()
