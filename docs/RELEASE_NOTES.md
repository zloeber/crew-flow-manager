# Release Notes - Task Selection and Flow Execution Improvements

## Version: Next Release

### 🎯 New Features

#### 1. Actual CrewAI Flow Execution

Previously, flow executions were simulated without actually running AI agents. Now:

- **Real AI Agents**: Flows execute with actual CrewAI agents and tasks
- **LLM Integration**: Support for OpenAI, Ollama (local), and custom endpoints
- **Detailed Logging**: Comprehensive execution logs showing each step
- **Graceful Fallback**: Automatically falls back to simulation if CrewAI is not installed
- **Task Output Capture**: Captures and stores actual task results

**Benefits:**
- Flows now produce real AI-generated outputs
- Proper LLM configuration with multiple provider support
- Better debugging with detailed execution logs

**Related Documentation:** See `CREWAI_EXECUTION.md` for technical details

#### 2. Task Selection Controls

Users can now choose which specific tasks to execute from a flow:

- **Selective Execution**: Run only the tasks you need
- **Task List View**: See all tasks with their descriptions and assigned agents
- **Checkbox Selection**: Click to select/deselect individual tasks
- **Bulk Actions**: "Select All" / "Deselect All" buttons
- **Visual Feedback**: Shows count of selected tasks
- **Default Behavior**: Executes all tasks if none are selected

**Benefits:**
- Test individual tasks during development
- Reduce costs by running only necessary tasks
- Debug specific task issues in isolation
- Faster iteration cycles

**API Endpoint:** `GET /api/flows/{flow_id}/tasks`

**Related Documentation:** See `TASK_SELECTION.md` for usage guide

#### 3. MCP Server Dashboard Enhancements

The MCP Tools page now provides detailed server configuration views:

- **Expandable Cards**: Click to expand/collapse server details
- **Full Configuration Display**: 
  - Command and arguments
  - Environment variables
  - URL (for HTTP servers)
  - Creation and update timestamps
- **Improved Status Indicators**: 
  - ● Green bullet = Active
  - ○ Gray bullet = Inactive
- **Better Layout**: Single-column cards for better detail visibility

**Benefits:**
- Easier troubleshooting of MCP server issues
- Quick verification of server configurations
- Better visibility of server settings

**Related Documentation:** See `MCP_DASHBOARD.md` for complete guide

### 🔧 Technical Improvements

#### Backend Changes

**flow_executor.py:**
- Implemented `_execute_crewai_flow()` method for real execution
- Added CrewAI Agent and Task object creation
- LLM configuration with provider-specific handling
- Task filtering based on user selection
- Actual execution time calculation
- Secure API key handling (parameter instead of environment variable)

**flows.py:**
- New endpoint: `GET /api/flows/{flow_id}/tasks`
- Returns structured task list with indices, descriptions, agents

**executions.py:**
- Updated to pass `selected_tasks` parameter to executor
- Maintains backward compatibility

**schemas.py:**
- Added `selected_tasks: Optional[List[str]]` to `ExecutionCreate`

#### Frontend Changes

**FlowsPage.tsx:**
- Task selection UI with checkboxes
- Loads tasks when opening execution modal
- Uses task indices for consistency
- Shows user feedback for errors
- Select all/deselect all functionality

**MCPToolsPage.tsx:**
- Expandable server cards with state management
- Detailed configuration display
- Improved visual hierarchy
- Chevron icons for expand/collapse

**api.ts:**
- Added `getTasks(id: number)` method to flowsApi

### 🔒 Security Updates

- Updated axios from ^1.6.5 to ^1.12.0
- Addressed multiple DoS and SSRF vulnerabilities
- No dangerous functions (eval, exec) used
- Secure LLM API key handling
- CodeQL security scan passed with 0 alerts

### 📚 Documentation

New documentation files:
- `TASK_SELECTION.md` - Task selection feature guide
- `MCP_DASHBOARD.md` - MCP server dashboard guide
- `CREWAI_EXECUTION.md` - Technical implementation details

### 🧪 Testing

All automated checks passed:
- ✅ Python syntax validation
- ✅ TypeScript compilation
- ✅ Production build
- ✅ Security scanning
- ✅ Code review
- ✅ Dependency vulnerability check

### 🚀 Getting Started

#### Using Task Selection

1. Navigate to Flows page
2. Click "Execute" on a flow
3. In the modal, you'll see a "Select Tasks to Execute" section
4. Click on tasks to select/deselect them
5. Click "Execute" to run selected tasks (or all if none selected)

#### Viewing MCP Server Details

1. Navigate to MCP Tools & Servers page
2. Find the server you want to inspect
3. Click the chevron (↓) icon next to the server name
4. View detailed configuration
5. Click chevron (↑) to collapse

#### Using Ollama (Local LLM)

1. Install Ollama: `curl -fsSL https://ollama.ai/install.sh | sh`
2. Pull a model: `ollama pull llama2`
3. When executing a flow:
   - Set Model Override: `llama2`
   - Set LLM Provider: `ollama`
   - Set LLM Base URL: `http://localhost:11434/v1`
4. Execute and see real AI outputs!

### ⚠️ Breaking Changes

None. All changes are backward compatible.

### 🐛 Known Issues

None reported.

### 🔜 Future Enhancements

Potential improvements for future releases:
- Task dependency visualization
- Streaming execution progress
- Task execution history
- Real-time MCP server health checks
- Cost tracking per execution
- Execution templates

### 📝 Migration Guide

No migration needed. The changes are fully backward compatible:
- Existing flows continue to work
- Executions without `selected_tasks` run all tasks
- Existing MCP server configurations remain unchanged

### 🙏 Credits

- User feedback driving these improvements
- Code review suggestions implemented
- Security best practices applied

---

For questions or issues, please create a GitHub issue or refer to the documentation in the `docs/` directory.
