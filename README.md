# CrewAI Flow Manager

A full-stack web application for managing, executing, and monitoring CrewAI Flows with real-time updates.

## Features

- 🎯 **Flow Management**: Create, edit, and validate CrewAI Flow YAML configurations
- 📝 **Monaco Editor**: Advanced YAML editor with syntax highlighting
- ✅ **Real-time Validation**: Instant validation of Flow configurations
- ⚡ **On-Demand Execution**: Execute flows instantly with optional model override
- 📅 **Scheduled Execution**: Schedule flows using cron expressions with APScheduler
- 🔄 **Real-time Monitoring**: WebSocket-based live updates for execution status
- 🛠️ **MCP Tools Discovery**: Browse and discover available MCP server tools
- 🗄️ **PostgreSQL Persistence**: Reliable data storage with SQLAlchemy ORM
- 🐳 **Docker Support**: Fully containerized with Docker Compose
- 🤖 **Local LLM Support**: Use local LLMs like Ollama instead of OpenAI

## Tech Stack

### Backend
- **FastAPI**: Modern Python web framework
- **SQLAlchemy**: SQL toolkit and ORM
- **PostgreSQL**: Database
- **APScheduler**: Job scheduling
- **CrewAI ~1.0+**: AI agent orchestration
- **WebSockets**: Real-time communication

### Frontend
- **React 18**: UI library
- **TypeScript**: Type-safe JavaScript
- **Vite**: Fast build tool
- **Tailwind CSS**: Utility-first CSS
- **Monaco Editor**: Advanced code editor
- **Axios**: HTTP client
- **React Router**: Navigation

## Prerequisites

- Docker and Docker Compose
- OR:
  - Python 3.11+
  - Node.js 20+
  - PostgreSQL 16+

## Quick Start with Docker

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd crew-flow-manager
   ```

2. **Set environment variables**
   ```bash
   cp backend/.env.example backend/.env
   # Edit backend/.env and configure:
   # - For OpenAI: Add your OPENAI_API_KEY
   # - For Ollama: Set LLM_PROVIDER=ollama and OLLAMA_BASE_URL
   # See LOCAL_LLM_SETUP.md for detailed configuration
   ```

3. **Start the application**
   ```bash
   docker-compose up -d
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## Manual Setup

### Backend Setup

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Start PostgreSQL**
   ```bash
   # Install and start PostgreSQL, then create database
   createdb crewai_flows
   ```

6. **Run the backend**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Configure environment**
   ```bash
   # Create .env file
   echo "VITE_API_URL=http://localhost:8000" > .env
   echo "VITE_WS_URL=ws://localhost:8000" >> .env
   ```

4. **Run the frontend**
   ```bash
   npm run dev
   ```

## Usage Guide

### Creating a Flow

1. Navigate to the **Flows** page
2. Click **New Flow**
3. Enter flow details:
   - **Name**: Unique identifier for the flow
   - **Description**: Optional description
   - **YAML Content**: CrewAI Flow configuration
4. The editor will validate your YAML in real-time
5. Click **Create** to save

Example Flow YAML:
```yaml
name: Research Assistant Flow
description: A flow that researches topics and generates reports

agents:
  - role: researcher
    goal: Research the given topic thoroughly
    backstory: You are an experienced researcher

tasks:
  - description: Research the topic
    agent: researcher
    expected_output: Detailed research findings
```

### Executing a Flow

1. Go to the **Flows** page
2. Click the **Play** button on a valid flow
3. The execution will start immediately
4. View real-time progress on the **Executions** page

### Scheduling a Flow

1. Navigate to the **Schedules** page
2. Click **New Schedule**
3. Configure:
   - **Flow**: Select the flow to execute
   - **Name**: Schedule identifier
   - **Cron Expression**: When to run (e.g., `0 0 * * *` for daily at midnight)
   - **Model Override**: Optional AI model to use
   - **Inputs**: Optional JSON inputs
   - **Active**: Enable/disable the schedule
4. Click **Create**

### Cron Expression Examples

- `0 0 * * *` - Daily at midnight
- `0 */6 * * *` - Every 6 hours
- `30 9 * * 1-5` - Weekdays at 9:30 AM
- `0 12 1 * *` - First day of month at noon

### Monitoring Executions

The **Executions** page shows all flow runs with:
- Real-time status updates via WebSocket
- Execution logs
- Input/output data
- Error messages (if failed)

### MCP Tools

The **MCP Tools** page displays available tools from MCP servers that can be used in your flows.

## Using Local LLMs (Ollama)

CrewAI Flow Manager supports local LLM providers like Ollama, allowing you to run AI models locally without external API calls.

### Quick Setup

1. **Install Ollama**
   ```bash
   curl -fsSL https://ollama.ai/install.sh | sh
   ```

2. **Pull a model**
   ```bash
   ollama pull llama2
   ```

3. **Configure backend/.env**
   ```bash
   LLM_PROVIDER=ollama
   OLLAMA_BASE_URL=http://localhost:11434
   LLM_MODEL=llama2
   OPENAI_API_KEY=ollama
   ```

4. **Use in the UI**
   - When executing a flow, select "Ollama (Local)" as the LLM Provider
   - Enter `http://localhost:11434` as the base URL
   - Specify the model name (e.g., `llama2`, `mistral`)

### Supported Providers

- **OpenAI** - Standard OpenAI API (default)
- **Ollama** - Local LLM runtime
- **Custom** - Any OpenAI-compatible endpoint

For detailed setup instructions and troubleshooting, see [LOCAL_LLM_SETUP.md](LOCAL_LLM_SETUP.md).

## API Documentation

Interactive API documentation is available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Main Endpoints

#### Flows
- `GET /api/flows` - List all flows
- `POST /api/flows` - Create a flow
- `GET /api/flows/{id}` - Get flow details
- `PUT /api/flows/{id}` - Update a flow
- `DELETE /api/flows/{id}` - Delete a flow
- `POST /api/flows/validate` - Validate YAML

#### Executions
- `GET /api/executions` - List executions
- `POST /api/executions` - Start execution
- `GET /api/executions/{id}` - Get execution details
- `DELETE /api/executions/{id}` - Delete execution

#### Schedules
- `GET /api/schedules` - List schedules
- `POST /api/schedules` - Create schedule
- `PUT /api/schedules/{id}` - Update schedule
- `DELETE /api/schedules/{id}` - Delete schedule

#### MCP Tools
- `GET /api/mcp-tools` - List available tools

#### WebSocket
- `WS /ws/updates` - Real-time updates

## Architecture

```
crew-flow-manager/
├── backend/
│   ├── app/
│   │   ├── api/          # API endpoints
│   │   ├── core/         # Configuration
│   │   ├── db/           # Database connection
│   │   ├── models/       # SQLAlchemy models
│   │   ├── schemas/      # Pydantic schemas
│   │   ├── services/     # Business logic
│   │   └── main.py       # FastAPI app
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── pages/        # Page components
│   │   ├── services/     # API & WebSocket
│   │   ├── types/        # TypeScript types
│   │   ├── App.tsx       # Main component
│   │   └── main.tsx      # Entry point
│   ├── Dockerfile
│   └── package.json
└── docker-compose.yml
```

## Database Schema

- **flows**: Flow definitions and YAML content
- **executions**: Flow execution records and results
- **schedules**: Scheduled job configurations
- **apscheduler_jobs**: APScheduler job store

## Development

### Backend Development

```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload
```

### Frontend Development

```bash
cd frontend
npm run dev
```

### Code Style

Backend:
```bash
# Format code
black app/
# Check types
mypy app/
```

Frontend:
```bash
# Lint
npm run lint
# Type check
npx tsc --noEmit
```

## Troubleshooting

### Database Connection Issues
- Ensure PostgreSQL is running
- Check `DATABASE_URL` in `.env`
- Verify database exists: `psql -l`

### Port Conflicts
- Change ports in `docker-compose.yml` or `.env`
- Check if ports 3000, 8000, 5432 are available

### WebSocket Connection Failed
- Ensure backend is running
- Check CORS settings in `backend/app/core/config.py`
- Verify `VITE_WS_URL` in frontend `.env`

### Flow Validation Errors
- Check YAML syntax
- Ensure required fields are present
- Review error messages in UI

## Production Deployment

1. **Update environment variables**
   - Set strong `SECRET_KEY`
   - Configure production `DATABASE_URL`
   - Add real `OPENAI_API_KEY`
   - Update `CORS_ORIGINS`

2. **Build production images**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

3. **Use HTTPS**
   - Configure reverse proxy (nginx/traefik)
   - Add SSL certificates

4. **Database backups**
   ```bash
   docker exec crewai-postgres pg_dump -U crewai crewai_flows > backup.sql
   ```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For issues and questions:
- GitHub Issues: [repository-url]/issues
- Documentation: [repository-url]/wiki

## Roadmap

- [x] Local LLM support (Ollama and custom endpoints)
- [ ] User authentication and authorization
- [ ] Flow templates library
- [ ] Enhanced execution logs with streaming
- [ ] Flow version history
- [ ] Performance metrics and analytics
- [ ] Multi-language support
- [ ] Export/import flows
- [ ] Real MCP server integration
- [ ] Advanced cron expression builder
- [ ] Email notifications for execution status

## Credits

Built with:
- [CrewAI](https://github.com/joaomdmoura/crewai)
- [FastAPI](https://fastapi.tiangolo.com/)
- [React](https://react.dev/)
- [Tailwind CSS](https://tailwindcss.com/)
- [Monaco Editor](https://microsoft.github.io/monaco-editor/)
