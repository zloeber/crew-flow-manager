# Using Local LLM Endpoints (Ollama)

This guide explains how to configure CrewAI Flow Manager to use local LLM endpoints like Ollama instead of OpenAI's API.

## Overview

CrewAI Flow Manager now supports multiple LLM providers:
- **OpenAI** (default) - Uses OpenAI's API
- **Ollama** - Local LLM runtime
- **Custom** - Any OpenAI-compatible endpoint

## Setup Ollama

### 1. Install Ollama

Visit [https://ollama.ai](https://ollama.ai) and follow the installation instructions for your platform:

**macOS/Linux:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**Windows:**
Download the installer from the Ollama website.

### 2. Start Ollama Service

```bash
ollama serve
```

By default, Ollama runs on `http://localhost:11434`.

### 3. Download a Model

Pull a model you want to use:

```bash
# Popular models
ollama pull llama2          # Meta's Llama 2
ollama pull mistral         # Mistral 7B
ollama pull codellama       # Code Llama
ollama pull llama2:13b      # Llama 2 13B
ollama pull mixtral         # Mixtral 8x7B
```

List available models:
```bash
ollama list
```

## Configuration

### Global Configuration (Environment Variables)

Configure the default LLM provider in `backend/.env`:

```bash
# For Ollama
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
LLM_MODEL=llama2
OPENAI_API_KEY=ollama  # Set to any non-empty value

# For custom OpenAI-compatible endpoints
# LLM_PROVIDER=custom
# OPENAI_API_BASE=https://your-endpoint.com/v1
# OPENAI_API_KEY=your-api-key
# LLM_MODEL=your-model-name
```

### Per-Execution Configuration (UI)

When executing a flow, you can override the LLM settings:

1. Go to **Flows** page
2. Click the **Play** button on a flow
3. In the execution modal, configure:
   - **Model Override**: Specify the model (e.g., `llama2`, `mistral`)
   - **LLM Provider**: Select `Ollama (Local)` or `Custom Endpoint`
   - **LLM Base URL**: Enter `http://localhost:11434` for Ollama
   - **Inputs**: Optional JSON inputs for the flow

### Per-Schedule Configuration

When creating or editing a schedule:

1. Go to **Schedules** page
2. Click **New Schedule** or edit an existing one
3. Configure the same LLM settings as above
4. The schedule will use these settings for all executions

## Example Configurations

### Using Ollama with Llama 2

**Environment Variables:**
```bash
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
LLM_MODEL=llama2
OPENAI_API_KEY=ollama
```

**UI Configuration:**
- Model Override: `llama2`
- LLM Provider: `Ollama (Local)`
- LLM Base URL: `http://localhost:11434`

### Using Ollama with Mistral

**Environment Variables:**
```bash
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
LLM_MODEL=mistral
OPENAI_API_KEY=ollama
```

**UI Configuration:**
- Model Override: `mistral`
- LLM Provider: `Ollama (Local)`
- LLM Base URL: `http://localhost:11434`

### Using a Custom OpenAI-Compatible Endpoint

**Environment Variables:**
```bash
LLM_PROVIDER=custom
OPENAI_API_BASE=https://api.your-service.com/v1
OPENAI_API_KEY=your-api-key-here
LLM_MODEL=your-model-name
```

**UI Configuration:**
- Model Override: `your-model-name`
- LLM Provider: `Custom Endpoint`
- LLM Base URL: `https://api.your-service.com/v1`

## Docker Setup with Ollama

If you're running CrewAI Flow Manager in Docker and want to use Ollama:

### Option 1: Ollama on Host Machine

Run Ollama on your host machine and configure the backend to access it:

**docker-compose.yml:**
```yaml
services:
  backend:
    environment:
      - LLM_PROVIDER=ollama
      - OLLAMA_BASE_URL=http://host.docker.internal:11434
      - LLM_MODEL=llama2
      - OPENAI_API_KEY=ollama
```

**Linux:** Use `http://172.17.0.1:11434` instead of `host.docker.internal`

### Option 2: Ollama as a Docker Service

Add Ollama to your docker-compose.yml:

```yaml
services:
  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    
  backend:
    depends_on:
      - ollama
    environment:
      - LLM_PROVIDER=ollama
      - OLLAMA_BASE_URL=http://ollama:11434
      - LLM_MODEL=llama2
      - OPENAI_API_KEY=ollama

volumes:
  ollama_data:
```

After starting the services, download a model:
```bash
docker exec -it <ollama-container> ollama pull llama2
```

## Troubleshooting

### Connection Refused

**Problem:** Cannot connect to Ollama
**Solution:**
- Ensure Ollama is running: `ollama serve`
- Check the URL is correct (default: `http://localhost:11434`)
- If using Docker, use `host.docker.internal` or container name

### Model Not Found

**Problem:** Model not available in Ollama
**Solution:**
```bash
ollama pull <model-name>
ollama list  # Verify model is downloaded
```

### Slow Performance

**Problem:** Local model is slow
**Solution:**
- Use smaller models (e.g., `llama2:7b` instead of `llama2:70b`)
- Ensure sufficient RAM (8GB+ recommended)
- Consider GPU acceleration (NVIDIA GPUs supported)

### Flow Execution Fails

**Problem:** Execution fails with LLM errors
**Solution:**
- Check Ollama logs: `ollama logs`
- Verify model compatibility with CrewAI
- Try a different model
- Check the execution logs in the UI for specific errors

## Best Practices

1. **Model Selection:**
   - Use `llama2` or `mistral` for general tasks
   - Use `codellama` for code-related workflows
   - Larger models (13B, 70B) for complex reasoning

2. **Performance:**
   - Start with smaller models and scale up if needed
   - Monitor system resources (RAM, GPU)
   - Use GPU acceleration when available

3. **Development:**
   - Use Ollama for development/testing
   - Switch to OpenAI for production if needed
   - Test flows with both providers

4. **Security:**
   - Local LLMs keep data private
   - No external API calls required
   - Control over model versions

## Supported Models

Popular models that work well with CrewAI:

- **llama2** - Meta's general-purpose model
- **mistral** - High-quality open model
- **codellama** - Specialized for code
- **mixtral** - Mixture of experts model
- **neural-chat** - Intel's chat model
- **starling-lm** - Berkeley's instruction-following model

See [Ollama Library](https://ollama.ai/library) for a complete list.

## Additional Resources

- [Ollama Documentation](https://github.com/ollama/ollama/blob/main/docs/README.md)
- [CrewAI Documentation](https://docs.crewai.com/)
- [Model Comparison](https://ollama.ai/library)

## Next Steps

- Try different models to find the best fit
- Experiment with model parameters
- Monitor execution logs for optimization
- Share your findings with the community
