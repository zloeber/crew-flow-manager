# CrewAI Flow Execution Implementation

## Overview

The flow execution system has been updated to actually execute CrewAI flows instead of just simulating them. This enables real AI agent workflows with proper task execution, LLM integration, and detailed logging.

## Previous Behavior (Simulation Mode)

Previously, the `flow_executor.py` only simulated flow execution:
- Created dummy logs with timestamps
- Waited a few seconds with `asyncio.sleep()`
- Returned a generic "Flow executed successfully" message
- Did not actually run any AI agents or tasks

## New Behavior (Real Execution)

The updated system now:
1. Parses YAML flow configuration
2. Creates actual CrewAI Agent and Task objects
3. Configures LLM based on user preferences (OpenAI, Ollama, custom)
4. Executes the crew with real AI interactions
5. Captures and logs detailed execution progress
6. Returns actual task outputs
7. Falls back to simulation if CrewAI is not installed

## Architecture

### Flow Execution Pipeline

```
1. User triggers execution → 
2. API creates execution record → 
3. Background task starts → 
4. YAML parsed to extract config → 
5. Agents created with LLM → 
6. Tasks created and assigned to agents → 
7. Crew executes (sequential process) → 
8. Results captured and stored → 
9. WebSocket broadcasts updates → 
10. Execution marked as complete
```

### Key Components

#### FlowExecutor._execute_crewai_flow()

The main execution method that:
- Imports CrewAI components (Agent, Task, Crew)
- Configures LLM based on provider settings
- Creates agents from YAML configuration
- Creates tasks from YAML configuration
- Filters tasks if user selected specific ones
- Runs the crew and captures results
- Handles errors gracefully

## LLM Configuration

### Supported Providers

1. **OpenAI (Default)**
   ```json
   {
     "llm_provider": "openai",
     "model_override": "gpt-4",
     "llm_base_url": null
   }
   ```

2. **Ollama (Local)**
   ```json
   {
     "llm_provider": "ollama",
     "model_override": "llama2",
     "llm_base_url": "http://localhost:11434/v1"
   }
   ```

3. **Custom Endpoint**
   ```json
   {
     "llm_provider": "custom",
     "model_override": "gpt-3.5-turbo",
     "llm_base_url": "https://api.example.com/v1"
   }
   ```

### LLM Setup Process

```python
# 1. Build configuration from user inputs
llm_config = {}
if model_override:
    llm_config['model'] = model_override
if llm_base_url:
    llm_config['base_url'] = llm_base_url

# 2. Handle special cases (Ollama)
if llm_provider == 'ollama':
    os.environ['OPENAI_API_KEY'] = 'ollama'  # Dummy key
    if not llm_config.get('base_url'):
        llm_config['base_url'] = 'http://localhost:11434/v1'

# 3. Create LLM instance
llm = ChatOpenAI(**llm_config)
```

## Agent Creation

Agents are created from YAML configuration:

```yaml
agents:
  - role: Senior Researcher
    goal: Research topics thoroughly
    backstory: You are an experienced researcher...
    allow_delegation: false
```

Converted to CrewAI Agent:

```python
agent = Agent(
    role='Senior Researcher',
    goal='Research topics thoroughly',
    backstory='You are an experienced researcher...',
    verbose=True,
    allow_delegation=False,
    llm=llm  # Configured LLM
)
```

## Task Creation

Tasks are created from YAML configuration:

```yaml
tasks:
  - description: Research the given topic
    agent: Senior Researcher
    expected_output: Detailed research findings
```

Converted to CrewAI Task:

```python
task = Task(
    description='Research the given topic',
    agent=agents['Senior Researcher'],  # Reference to created agent
    expected_output='Detailed research findings'
)
```

## Execution Logging

Detailed logs are captured at each step:

```
[2025-01-15T10:30:00.000000] Starting flow execution: Research Flow
[2025-01-15T10:30:00.100000] Using model override: gpt-4
[2025-01-15T10:30:00.200000] LLM Provider: openai
[2025-01-15T10:30:00.300000] Parsing flow configuration...
[2025-01-15T10:30:00.400000] Creating 2 agent(s)...
[2025-01-15T10:30:00.500000]   - Created agent: Senior Researcher
[2025-01-15T10:30:00.600000]   - Created agent: Report Writer
[2025-01-15T10:30:00.700000] Creating 2 task(s)...
[2025-01-15T10:30:00.800000]   - Created task: Research the given topic...
[2025-01-15T10:30:00.900000]   - Created task: Write a comprehensive report...
[2025-01-15T10:30:01.000000] Starting crew execution...
[2025-01-15T10:35:00.000000] Crew execution completed successfully
```

## Output Structure

Successful execution returns:

```json
{
  "result": "Final output from the crew execution",
  "tasks_executed": 2,
  "agents_used": 2,
  "execution_time": 240.5
}
```

Failed execution returns error details in the `error_message` field.

## Error Handling

### CrewAI Not Installed

If CrewAI is not available, the system:
1. Catches the `ImportError`
2. Logs a warning about simulation mode
3. Falls back to simulated execution
4. Returns results marked with `"simulation": true`

### Task Configuration Errors

- Missing agent: Logs warning and skips task
- Invalid task: Logs error and skips task
- No valid tasks: Returns early with appropriate message

### LLM Configuration Errors

- LLM setup failure: Logs warning, continues without LLM config
- API errors: Captured in execution error message
- Timeout errors: Handled by CrewAI with appropriate logging

## Task Selection Integration

When users select specific tasks:

```python
# Filter tasks based on selection
tasks_to_execute = tasks_config
if selected_tasks:
    tasks_to_execute = [
        task for task in tasks_config 
        if task.get('description') in selected_tasks
    ]
    logs.append(f"Filtered to {len(tasks_to_execute)} selected task(s)")
```

Only the filtered tasks are created and executed.

## Async Execution

Crew execution runs in a thread pool to avoid blocking:

```python
loop = asyncio.get_event_loop()
result = await loop.run_in_executor(None, crew.kickoff, inputs or {})
```

This allows:
- Non-blocking API responses
- Real-time WebSocket updates
- Concurrent executions
- Background processing

## WebSocket Updates

Real-time status updates are broadcast:

```python
# On start
await websocket_manager.broadcast({
    "type": "execution_update",
    "data": {
        "execution_id": execution_id,
        "status": "running",
        "started_at": execution.started_at.isoformat()
    }
})

# On completion
await websocket_manager.broadcast({
    "type": "execution_update",
    "data": {
        "execution_id": execution_id,
        "status": "success",
        "completed_at": execution.completed_at.isoformat(),
        "outputs": execution.outputs
    }
})
```

## Configuration Examples

### Example 1: OpenAI with GPT-4

```bash
curl -X POST http://localhost:8000/api/executions \
  -H "Content-Type: application/json" \
  -d '{
    "flow_id": 1,
    "model_override": "gpt-4",
    "llm_provider": "openai",
    "inputs": {"topic": "AI trends"}
  }'
```

### Example 2: Ollama Local

```bash
curl -X POST http://localhost:8000/api/executions \
  -H "Content-Type: application/json" \
  -d '{
    "flow_id": 1,
    "model_override": "llama2",
    "llm_provider": "ollama",
    "llm_base_url": "http://localhost:11434/v1",
    "inputs": {"topic": "Local AI"}
  }'
```

### Example 3: Custom Endpoint

```bash
curl -X POST http://localhost:8000/api/executions \
  -H "Content-Type: application/json" \
  -d '{
    "flow_id": 1,
    "model_override": "gpt-3.5-turbo",
    "llm_provider": "custom",
    "llm_base_url": "https://api.mycompany.com/v1",
    "inputs": {}
  }'
```

## Testing

### With CrewAI Installed

1. Install dependencies: `pip install crewai crewai-tools langchain-openai`
2. Set API key: `export OPENAI_API_KEY=your-key`
3. Create a flow from examples
4. Execute the flow
5. Check logs for actual agent/task execution

### Without CrewAI (Simulation Mode)

1. Don't install CrewAI packages
2. Create and execute a flow
3. System automatically falls back to simulation
4. Results include `"simulation": true`

## Troubleshooting

### Common Issues

**Issue**: "CrewAI not available, using simulation mode"
- **Cause**: CrewAI package not installed
- **Solution**: Install with `pip install crewai crewai-tools langchain-openai`

**Issue**: "No agents defined in flow"
- **Cause**: YAML missing `agents` section
- **Solution**: Add agents to your flow YAML

**Issue**: "Agent 'X' not found for task"
- **Cause**: Task references non-existent agent
- **Solution**: Ensure task's `agent` field matches an agent's `role`

**Issue**: LLM API errors
- **Cause**: Invalid API key or endpoint
- **Solution**: Check API key and base URL configuration

## Benefits

1. **Real AI Execution**: Actual AI agents perform tasks with real LLMs
2. **Flexible Configuration**: Support for multiple LLM providers
3. **Detailed Logging**: Comprehensive execution logs for debugging
4. **Error Resilience**: Graceful fallback to simulation mode
5. **Task Selection**: Run specific tasks instead of entire flow
6. **Real-time Updates**: WebSocket notifications for execution progress

## Future Enhancements

Potential improvements:

- Streaming task outputs during execution
- Task result caching
- Parallel task execution support
- Custom tool integration
- Memory/context persistence
- Execution replay functionality
- Cost tracking per execution
- Execution templates and presets
