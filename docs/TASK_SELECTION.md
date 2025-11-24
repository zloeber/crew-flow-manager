# Task Selection Feature

## Overview

The task selection feature allows users to selectively execute specific tasks from a flow, rather than always running all tasks. This provides more granular control over flow execution and is useful for:

- Testing individual tasks during development
- Running only specific tasks when debugging
- Executing partial workflows based on requirements
- Reducing execution time by skipping unnecessary tasks

## How It Works

### Backend Implementation

#### New API Endpoint

**GET /api/flows/{flow_id}/tasks**

Returns a list of tasks available in a flow's YAML configuration.

**Response:**
```json
{
  "flow_id": 1,
  "flow_name": "Research and Report Flow",
  "tasks": [
    {
      "index": 0,
      "description": "Research the topic thoroughly",
      "agent": "Senior Researcher",
      "expected_output": "Detailed research findings with sources"
    },
    {
      "index": 1,
      "description": "Write a comprehensive report based on the research",
      "agent": "Report Writer",
      "expected_output": "A well-structured report with introduction, findings, and conclusion"
    }
  ],
  "total_tasks": 2
}
```

#### Updated Execution Schema

The `ExecutionCreate` schema now includes an optional `selected_tasks` field:

```python
class ExecutionCreate(BaseModel):
    flow_id: int
    model_override: Optional[str] = None
    llm_provider: Optional[str] = None
    llm_base_url: Optional[str] = None
    inputs: Optional[Dict[str, Any]] = None
    selected_tasks: Optional[List[str]] = None  # List of task descriptions
```

#### Flow Executor Changes

The `flow_executor.py` service has been updated to:

1. Accept `selected_tasks` parameter
2. Filter tasks based on the selection
3. Execute only the selected tasks
4. Fall back to executing all tasks if none are selected

### Frontend Implementation

#### Task Selection UI

When executing a flow, users can:

1. **View all available tasks** - The execution modal displays all tasks from the flow
2. **Select specific tasks** - Click on individual tasks to select/deselect them
3. **Select all/Deselect all** - Use the toggle button to quickly select or clear all tasks
4. **See selection status** - Visual indicators show:
   - Selected tasks with a blue checkbox icon
   - Unselected tasks with a gray checkbox icon
   - Count of selected tasks vs total tasks

#### User Experience

- **No tasks selected**: All tasks will be executed (default behavior)
- **Some tasks selected**: Only the selected tasks will be executed
- **Visual feedback**: The modal shows "X of Y task(s) selected" or "No tasks selected - all tasks will be executed"

## Usage Examples

### Example 1: Running All Tasks (Default)

1. Click "Execute" on a flow
2. Configure model/provider settings if needed
3. Don't select any tasks
4. Click "Execute"
5. All tasks in the flow will run

### Example 2: Running Specific Tasks

1. Click "Execute" on a flow
2. In the task selection section, click on the tasks you want to run
3. Selected tasks will show a blue checkbox
4. Click "Execute"
5. Only the selected tasks will run

### Example 3: Testing a Single Task

1. Open execution modal for a flow
2. Click "Deselect All" to clear any selections
3. Click on the single task you want to test
4. Click "Execute"
5. Only that task will run

## API Usage

### Creating an Execution with Task Selection

```bash
curl -X POST http://localhost:8000/api/executions \
  -H "Content-Type: application/json" \
  -d '{
    "flow_id": 1,
    "model_override": "gpt-4",
    "selected_tasks": [
      "Research the topic thoroughly"
    ]
  }'
```

### Getting Tasks for a Flow

```bash
curl http://localhost:8000/api/flows/1/tasks
```

## Benefits

1. **Faster Development Cycles**: Test individual tasks without running the entire flow
2. **Cost Efficiency**: Run only necessary tasks, saving on API calls and compute time
3. **Better Debugging**: Isolate and debug specific tasks more easily
4. **Flexible Execution**: Adapt workflow execution to specific needs

## Technical Notes

- Task selection is matched by task description (exact match)
- If a selected task's agent is not found, it will be skipped with a warning
- Task dependencies are not enforced - users are responsible for selecting tasks in the correct order
- The feature works with both real CrewAI execution and simulation mode

## Future Enhancements

Potential improvements for future versions:

- Task dependency visualization and enforcement
- Task execution order customization
- Saved task selection presets
- Task-level parameter overrides
- Task execution history and analytics
