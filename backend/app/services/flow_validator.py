"""
Flow validation service using CrewAI
"""
import yaml
import logging
from typing import Dict, Any, List, Tuple

logger = logging.getLogger(__name__)


class FlowValidator:
    """Validates CrewAI Flow YAML configurations"""
    
    REQUIRED_FIELDS = ["name"]
    OPTIONAL_FIELDS = ["description", "agents", "tasks", "crews", "flows"]
    
    def validate(self, yaml_content: str) -> Tuple[bool, List[str]]:
        """
        Validate a CrewAI Flow YAML configuration
        
        Args:
            yaml_content: YAML content as string
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        
        # Parse YAML
        try:
            data = yaml.safe_load(yaml_content)
        except yaml.YAMLError as e:
            return False, [f"Invalid YAML syntax: {str(e)}"]
        
        if not isinstance(data, dict):
            return False, ["YAML must be a dictionary/object"]
        
        # Check required fields
        for field in self.REQUIRED_FIELDS:
            if field not in data:
                errors.append(f"Missing required field: {field}")
        
        # Validate name
        if "name" in data:
            if not isinstance(data["name"], str) or not data["name"].strip():
                errors.append("Field 'name' must be a non-empty string")
        
        # Validate agents if present
        if "agents" in data:
            agent_errors = self._validate_agents(data["agents"])
            errors.extend(agent_errors)
        
        # Validate tasks if present
        if "tasks" in data:
            task_errors = self._validate_tasks(data["tasks"])
            errors.extend(task_errors)
        
        # Validate crews if present
        if "crews" in data:
            crew_errors = self._validate_crews(data["crews"])
            errors.extend(crew_errors)
        
        is_valid = len(errors) == 0
        return is_valid, errors
    
    def _validate_agents(self, agents: Any) -> List[str]:
        """Validate agents section"""
        errors = []
        
        if not isinstance(agents, list):
            return ["Field 'agents' must be a list"]
        
        for i, agent in enumerate(agents):
            if not isinstance(agent, dict):
                errors.append(f"Agent at index {i} must be a dictionary")
                continue
            
            if "role" not in agent:
                errors.append(f"Agent at index {i} missing required field 'role'")
        
        return errors
    
    def _validate_tasks(self, tasks: Any) -> List[str]:
        """Validate tasks section"""
        errors = []
        
        if not isinstance(tasks, list):
            return ["Field 'tasks' must be a list"]
        
        for i, task in enumerate(tasks):
            if not isinstance(task, dict):
                errors.append(f"Task at index {i} must be a dictionary")
                continue
            
            if "description" not in task:
                errors.append(f"Task at index {i} missing required field 'description'")
        
        return errors
    
    def _validate_crews(self, crews: Any) -> List[str]:
        """Validate crews section"""
        errors = []
        
        if not isinstance(crews, list):
            return ["Field 'crews' must be a list"]
        
        for i, crew in enumerate(crews):
            if not isinstance(crew, dict):
                errors.append(f"Crew at index {i} must be a dictionary")
        
        return errors


flow_validator = FlowValidator()
