# Architecture Overview

This document provides a detailed overview of the CrewAI Flow Manager architecture.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                          Client Browser                              │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │                    React Frontend (Port 3000)                   │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐   │ │
│  │  │   Home   │  │  Flows   │  │Executions│  │   Schedules  │   │ │
│  │  └────┬─────┘  └────┬─────┘  └────┬─────┘  └──────┬───────┘   │ │
│  │       │             │              │                │           │ │
│  │       └─────────────┴──────────────┴────────────────┘           │ │
│  │                          │                                      │ │
│  │                    ┌─────┴──────┐                              │ │
│  │                    │ API Client │                              │ │
│  │                    │  (Axios)   │                              │ │
│  │                    └─────┬──────┘                              │ │
│  │                          │                                      │ │
│  │                    ┌─────┴──────┐                              │ │
│  │                    │ WebSocket  │                              │ │
│  │                    │   Client   │                              │ │
│  │                    └─────┬──────┘                              │ │
│  └──────────────────────────┼───────────────────────────────────┘ │
└────────────────────────────┼────────────────────────────────────────┘
                             │
                    ┌────────┼────────┐
                    │   HTTP │ WS     │
                    │        │        │
┌───────────────────▼────────▼────────────────────────────────────────┐
│                  FastAPI Backend (Port 8000)                         │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │                      API Layer                                  │ │
│  │  ┌─────────┐ ┌──────────┐ ┌───────────┐ ┌──────────────────┐  │ │
│  │  │ Flows   │ │Executions│ │ Schedules │ │ WebSocket Events │  │ │
│  │  │ /api/   │ │ /api/    │ │ /api/     │ │   /ws/updates    │  │ │
│  │  └────┬────┘ └────┬─────┘ └─────┬─────┘ └─────────┬────────┘  │ │
│  │       │           │             │                  │           │ │
│  └───────┼───────────┼─────────────┼──────────────────┼───────────┘ │
│          │           │             │                  │             │
│  ┌───────┼───────────┼─────────────┼──────────────────┼───────────┐ │
│  │       │           │             │                  │           │ │
│  │  ┌────▼────┐ ┌────▼──────┐ ┌───▼────────┐  ┌──────▼────────┐  │ │
│  │  │  Flow   │ │   Flow    │ │  Scheduler │  │   WebSocket   │  │ │
│  │  │Validator│ │  Executor │ │  Service   │  │    Manager    │  │ │
│  │  └─────────┘ └───────────┘ └────────────┘  └───────────────┘  │ │
│  │                                                                 │ │
│  │                     Service Layer                               │ │
│  └─────────────────────────────┬───────────────────────────────────┘ │
│                                │                                     │
│  ┌─────────────────────────────▼───────────────────────────────────┐ │
│  │                    SQLAlchemy ORM                                │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────────────┐  │ │
│  │  │   Flow   │  │Execution │  │ Schedule │  │  APScheduler   │  │ │
│  │  │  Model   │  │  Model   │  │  Model   │  │   JobStore     │  │ │
│  │  └──────────┘  └──────────┘  └──────────┘  └────────────────┘  │ │
│  └─────────────────────────────┬───────────────────────────────────┘ │
└────────────────────────────────┼─────────────────────────────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │ PostgreSQL Database     │
                    │     (Port 5432)         │
                    │  ┌──────────────────┐   │
                    │  │   flows          │   │
                    │  │   executions     │   │
                    │  │   schedules      │   │
                    │  │   apscheduler_*  │   │
                    │  └──────────────────┘   │
                    └─────────────────────────┘
```

## Component Details

### Frontend (React + TypeScript)

**Technology Stack:**
- React 18
- TypeScript
- Vite (build tool)
- Tailwind CSS (styling)
- Monaco Editor (YAML editing)
- Axios (HTTP client)
- WebSocket API (real-time updates)

**Key Components:**
- `HomePage`: Dashboard with statistics
- `FlowsPage`: Create, edit, view, and delete flows
- `ExecutionsPage`: Monitor flow executions with real-time updates
- `SchedulesPage`: Manage scheduled flow executions
- `MCPToolsPage`: Browse available MCP server tools

### Backend (FastAPI + Python)

**Technology Stack:**
- FastAPI (web framework)
- SQLAlchemy (ORM)
- Alembic (migrations - optional)
- APScheduler (job scheduling)
- Pydantic (data validation)
- WebSockets (real-time communication)
- CrewAI (flow execution)

**API Endpoints:**

```
GET    /                      - Health check
GET    /health                - Detailed health status

# Flows
GET    /api/flows             - List all flows
POST   /api/flows             - Create flow
GET    /api/flows/{id}        - Get flow by ID
PUT    /api/flows/{id}        - Update flow
DELETE /api/flows/{id}        - Delete flow
POST   /api/flows/validate    - Validate YAML

# Executions
GET    /api/executions        - List executions
POST   /api/executions        - Create execution
GET    /api/executions/{id}   - Get execution by ID
DELETE /api/executions/{id}   - Delete execution

# Schedules
GET    /api/schedules         - List schedules
POST   /api/schedules         - Create schedule
GET    /api/schedules/{id}    - Get schedule by ID
PUT    /api/schedules/{id}    - Update schedule
DELETE /api/schedules/{id}    - Delete schedule

# MCP Tools
GET    /api/mcp-tools         - List MCP tools

# WebSocket
WS     /ws/updates            - Real-time updates
```

### Database Schema

**flows table:**
```
id              INTEGER PRIMARY KEY
name            VARCHAR(255) UNIQUE NOT NULL
description     TEXT
yaml_content    TEXT NOT NULL
is_valid        BOOLEAN DEFAULT FALSE
validation_errors JSON
created_at      TIMESTAMP
updated_at      TIMESTAMP
```

**executions table:**
```
id              INTEGER PRIMARY KEY
flow_id         INTEGER FOREIGN KEY -> flows.id
status          ENUM (pending, running, success, failed, cancelled)
model_override  VARCHAR(255)
inputs          JSON
outputs         JSON
error_message   TEXT
logs            TEXT
started_at      TIMESTAMP
completed_at    TIMESTAMP
created_at      TIMESTAMP
```

**schedules table:**
```
id              INTEGER PRIMARY KEY
flow_id         INTEGER FOREIGN KEY -> flows.id
name            VARCHAR(255) NOT NULL
cron_expression VARCHAR(100) NOT NULL
model_override  VARCHAR(255)
inputs          JSON
is_active       BOOLEAN DEFAULT TRUE
last_run_at     TIMESTAMP
next_run_at     TIMESTAMP
created_at      TIMESTAMP
updated_at      TIMESTAMP
```

## Data Flow

### Creating a Flow

```
User Input → Frontend Form → API Request → Validation Service → Database
                                              ↓
                                        WebSocket Update
                                              ↓
                                          Frontend
```

### Executing a Flow

```
User Action → API Request → Create Execution Record → Background Task
                                                            ↓
                                                      Flow Executor
                                                            ↓
                                                   Update Status (DB)
                                                            ↓
                                                    WebSocket Broadcast
                                                            ↓
                                                   Frontend Updates
```

### Scheduled Execution

```
APScheduler → Check Active Schedules → Execute Flow
                                            ↓
                                     Create Execution
                                            ↓
                                      Flow Executor
                                            ↓
                                   Update Last Run Time
                                            ↓
                                   Calculate Next Run
```

## Real-time Communication

### WebSocket Message Types

```typescript
// Connection established
{
  type: "connected",
  data: {
    message: "Connected to CrewAI Flow Manager"
  }
}

// Execution status update
{
  type: "execution_update",
  data: {
    execution_id: 1,
    status: "running",
    started_at: "2024-01-01T00:00:00Z"
  }
}

// Execution completed
{
  type: "execution_update",
  data: {
    execution_id: 1,
    status: "success",
    completed_at: "2024-01-01T00:05:00Z",
    outputs: {...}
  }
}
```

## Security Considerations

### Current Implementation
- CORS configured for local development
- Database credentials in environment variables
- API key for OpenAI stored securely

### Future Enhancements
- User authentication (JWT tokens)
- Role-based access control (RBAC)
- API rate limiting
- Input sanitization
- SQL injection prevention (via ORM)
- XSS protection
- CSRF tokens

## Scalability Considerations

### Current Implementation
- SQLAlchemy connection pooling
- Async execution handling
- Background task processing

### Future Enhancements
- Redis for caching
- Message queue (Celery/RabbitMQ) for heavy workloads
- Horizontal scaling with load balancer
- Database read replicas
- CDN for frontend assets
- Kubernetes deployment

## Deployment Architecture

### Docker Compose (Development)
```
┌─────────────────┐
│   Frontend      │ :3000
│   (Node/Vite)   │
└────────┬────────┘
         │
┌────────┴────────┐
│    Backend      │ :8000
│   (FastAPI)     │
└────────┬────────┘
         │
┌────────┴────────┐
│   PostgreSQL    │ :5432
└─────────────────┘
```

### Production (Recommended)
```
┌─────────────────┐
│  Load Balancer  │
│   (nginx/HAProxy)│
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
┌───▼──┐  ┌──▼───┐
│ API  │  │ API  │  Multiple backend instances
│ :8000│  │ :8000│
└───┬──┘  └──┬───┘
    │        │
    └───┬────┘
        │
┌───────▼────────┐
│  PostgreSQL    │  Master + Replicas
│   Cluster      │
└────────────────┘
```

## Monitoring and Logging

### Current Implementation
- Python logging module
- Console logs
- Docker logs

### Recommended Additions
- Application Performance Monitoring (APM)
- Centralized logging (ELK stack)
- Metrics collection (Prometheus)
- Alerting (Grafana)
- Error tracking (Sentry)

## Technology Choices

### Why FastAPI?
- High performance (async support)
- Automatic API documentation
- Type checking with Pydantic
- Modern Python features
- Easy to test and maintain

### Why React?
- Component-based architecture
- Large ecosystem
- Virtual DOM for performance
- TypeScript support
- Developer experience

### Why PostgreSQL?
- Reliable and mature
- ACID compliance
- JSON support for flexible data
- Good performance for reads/writes
- APScheduler native support

### Why Tailwind CSS?
- Utility-first approach
- Rapid development
- Consistent design system
- Small bundle size
- Easy customization

### Why Monaco Editor?
- Full-featured code editor
- Syntax highlighting
- Auto-completion
- Error detection
- Same editor as VS Code

## Development Workflow

```
1. Code Change → Git Commit
2. Run Tests → CI/CD Pipeline
3. Build Docker Images
4. Deploy to Staging
5. Manual Testing
6. Deploy to Production
7. Monitor & Log
```

---

For more details on specific components, refer to the inline code documentation and README.md.
