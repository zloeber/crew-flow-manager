# Quick Start Guide

Get the CrewAI Flow Manager up and running in 5 minutes!

## Prerequisites

- Docker and Docker Compose installed
- Git installed
- (Optional) OpenAI API key for actual flow execution

## Step 1: Clone and Setup

```bash
# Clone the repository
git clone https://github.com/zloeber/crew-flow-manager.git
cd crew-flow-manager

# Copy environment configuration
cp backend/.env.example backend/.env
```

## Step 2: Configure (Optional)

Edit `backend/.env` to add your OpenAI API key:

```bash
OPENAI_API_KEY=sk-your-api-key-here
```

> **Note**: The app will run without an API key, but flow executions will be simulated.

## Step 3: Start the Application

```bash
# Start all services
docker compose up -d

# Check status
docker compose ps

# View logs (optional)
docker compose logs -f
```

## Step 4: Access the Application

Open your browser and navigate to:

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## Step 5: Create Your First Flow

1. Go to http://localhost:3000/flows
2. Click **"New Flow"**
3. Enter flow details:
   - Name: `My First Flow`
   - Description: `A simple test flow`
4. Use the Monaco editor to write your flow YAML:

```yaml
name: My First Flow
description: A simple test flow

agents:
  - role: Assistant
    goal: Help with tasks
    backstory: You are a helpful AI assistant

tasks:
  - description: Say hello and introduce yourself
    agent: Assistant
    expected_output: A friendly greeting message
```

5. Click **"Create"**
6. Click the **Play** button to execute your flow!

## Step 6: Monitor Execution

1. Go to the **Executions** page
2. Watch real-time updates as your flow runs
3. Click **View** to see logs and outputs

## What's Next?

### Schedule a Flow

1. Go to **Schedules** page
2. Click **"New Schedule"**
3. Select your flow
4. Set a cron expression (e.g., `0 0 * * *` for daily at midnight)
5. Click **"Create"**

### Explore MCP Tools

1. Go to **MCP Tools** page
2. Browse available tools that can be used in your flows

### Try Example Flows

Check the `examples/` directory for sample flow configurations:

```bash
cat examples/sample_flow.yaml
cat examples/simple_flow.yaml
```

## Common Commands

```bash
# Stop the application
docker compose down

# Restart the application
docker compose restart

# View logs
docker compose logs -f backend
docker compose logs -f frontend

# Rebuild after code changes
docker compose up -d --build

# Clean up everything (including database)
docker compose down -v
```

## Troubleshooting

### Port Already in Use

If ports 3000, 8000, or 5432 are already in use:

1. Edit `docker-compose.yml`
2. Change the port mappings:
   ```yaml
   ports:
     - "3001:3000"  # Change 3000 to 3001
   ```

### Services Won't Start

```bash
# Check Docker is running
docker ps

# Check logs for errors
docker compose logs

# Rebuild images
docker compose build --no-cache
docker compose up -d
```

### Database Connection Issues

```bash
# Check database is running
docker compose ps db

# Connect to database
docker exec -it crewai-postgres psql -U crewai -d crewai_flows
```

## Development Mode

For development with hot-reload:

### Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL="postgresql://crewai:crewai@localhost:5432/crewai_flows"
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Getting Help

- **Documentation**: See README.md for detailed documentation
- **Testing Guide**: See TESTING.md for testing instructions
- **Examples**: Check the `examples/` directory
- **Issues**: Report bugs on GitHub Issues

## Next Steps

1. Read the full [README.md](README.md) for comprehensive documentation
2. Check [TESTING.md](TESTING.md) for testing your setup
3. Explore the example flows in `examples/`
4. Visit the API docs at http://localhost:8000/docs
5. Join the community and share your flows!

---

**Congratulations!** 🎉 You now have a fully functional CrewAI Flow Manager!
