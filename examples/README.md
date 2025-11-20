# Example Flow Configurations

This directory contains example CrewAI Flow YAML configurations that you can use as templates.

## Available Examples

1. **simple_flow.yaml** - A basic flow with one agent and one task
2. **sample_flow.yaml** - A research and report flow with multiple agents and tasks
3. **ollama-flow-example.yaml** - Using local LLMs with Ollama
4. **custom-endpoint-example.yaml** - Using custom OpenAI-compatible endpoints

## Local LLM Examples

### Ollama Example

The `ollama-flow-example.yaml` demonstrates how to use local LLMs through Ollama:
- Uses models like `llama2` or `mistral`
- Runs entirely offline for privacy
- No API costs

**Prerequisites:**
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull a model
ollama pull llama2

# Configure backend/.env
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
LLM_MODEL=llama2
OPENAI_API_KEY=ollama
```

### Custom Endpoint Example

The `custom-endpoint-example.yaml` shows how to use custom OpenAI-compatible endpoints:
- LM Studio
- vLLM
- Text Generation WebUI
- Your own API

**Configuration:**
```bash
# In backend/.env
LLM_PROVIDER=custom
OPENAI_API_BASE=https://your-api.com/v1
OPENAI_API_KEY=your-api-key
LLM_MODEL=your-model-name
```

## Usage

You can copy these examples and modify them for your needs:

1. Open the CrewAI Flow Manager web interface
2. Navigate to the Flows page
3. Click "New Flow"
4. Copy the content from one of these example files
5. Paste into the YAML editor
6. Modify as needed
7. Save your flow

## Creating Your Own Flows

A typical CrewAI Flow YAML includes:

- `name`: Unique identifier for your flow
- `description`: What the flow does
- `agents`: List of AI agents with their roles, goals, and backstories
- `tasks`: List of tasks to be performed by agents

Refer to the CrewAI documentation for more details on flow structure.

## Additional Resources

- [LOCAL_LLM_SETUP.md](../LOCAL_LLM_SETUP.md) - Detailed guide for local LLM configuration
- [README.md](../README.md) - Main project documentation
- [CrewAI Documentation](https://docs.crewai.com/) - Official CrewAI docs

