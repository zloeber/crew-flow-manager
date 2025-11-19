# Testing Guide

This document provides instructions for testing the CrewAI Flow Manager application.

## Quick Test

Run the included test script to verify basic functionality:

```bash
./test.sh
```

This will check:
- Directory structure
- Python syntax
- Required files
- Backend dependencies
- Frontend dependencies
- Docker configuration

## Manual Testing

### 1. Backend Testing

#### Start Backend Locally

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Set up environment
export DATABASE_URL="sqlite:///./test.db"
export SECRET_KEY="test-secret-key"

# Run the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Test API Endpoints

Visit http://localhost:8000/docs to see interactive API documentation.

**Test Health Check:**
```bash
curl http://localhost:8000/health
```

**Test Flow Creation:**
```bash
curl -X POST http://localhost:8000/api/flows \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Flow",
    "description": "A test flow",
    "yaml_content": "name: Test\ndescription: Test flow\n"
  }'
```

**Test Flow Listing:**
```bash
curl http://localhost:8000/api/flows
```

**Test Flow Validation:**
```bash
curl -X POST http://localhost:8000/api/flows/validate \
  -H "Content-Type: text/plain" \
  -d "name: Test Flow\ndescription: A test flow"
```

### 2. Frontend Testing

#### Start Frontend Locally

```bash
cd frontend
npm install

# Set up environment
echo "VITE_API_URL=http://localhost:8000" > .env
echo "VITE_WS_URL=ws://localhost:8000" >> .env

# Run dev server
npm run dev
```

Access http://localhost:3000

#### Test UI Components

1. **Home Page**
   - Verify dashboard loads
   - Check statistics display

2. **Flows Page**
   - Click "New Flow"
   - Enter flow details
   - Test Monaco editor
   - Save flow
   - Edit existing flow
   - Delete flow

3. **Executions Page**
   - Execute a flow from Flows page
   - Verify execution appears
   - Check real-time updates
   - View execution details

4. **Schedules Page**
   - Create new schedule
   - Set cron expression
   - Toggle active/inactive
   - Edit schedule
   - Delete schedule

5. **MCP Tools Page**
   - Verify tools list loads
   - Test search functionality

### 3. Docker Testing

#### Build Images

```bash
# Build backend
docker build -t crewai-backend ./backend

# Build frontend
docker build -t crewai-frontend ./frontend
```

#### Run with Docker Compose

```bash
# Copy environment file
cp backend/.env.example backend/.env
# Edit backend/.env and set OPENAI_API_KEY

# Start all services
docker-compose up -d

# Check logs
docker-compose logs -f

# Verify services are running
docker-compose ps
```

#### Test Services

```bash
# Test backend
curl http://localhost:8000/health

# Test database connection
docker exec crewai-postgres psql -U crewai -d crewai_flows -c "SELECT version();"

# Check backend logs
docker logs crewai-backend

# Check frontend logs
docker logs crewai-frontend
```

#### Stop Services

```bash
docker-compose down
# To remove volumes as well:
docker-compose down -v
```

### 4. Integration Testing

#### Test Flow Lifecycle

1. **Create a Flow**
   ```bash
   curl -X POST http://localhost:8000/api/flows \
     -H "Content-Type: application/json" \
     -d '{
       "name": "Integration Test Flow",
       "description": "Testing flow lifecycle",
       "yaml_content": "name: Integration Test\ndescription: Test\nagents:\n  - role: tester\n    goal: Test the system\ntasks:\n  - description: Test task\n"
     }'
   ```

2. **Execute the Flow**
   ```bash
   # Get flow ID from previous response, e.g., 1
   curl -X POST http://localhost:8000/api/executions \
     -H "Content-Type: application/json" \
     -d '{"flow_id": 1}'
   ```

3. **Check Execution Status**
   ```bash
   # Get execution ID from previous response, e.g., 1
   curl http://localhost:8000/api/executions/1
   ```

4. **Create a Schedule**
   ```bash
   curl -X POST http://localhost:8000/api/schedules \
     -H "Content-Type: application/json" \
     -d '{
       "flow_id": 1,
       "name": "Daily Test",
       "cron_expression": "0 0 * * *",
       "is_active": true
     }'
   ```

#### Test WebSocket Connection

Use a WebSocket client or browser console:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/updates');

ws.onopen = () => {
  console.log('Connected to WebSocket');
};

ws.onmessage = (event) => {
  console.log('Received:', JSON.parse(event.data));
};

ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};
```

### 5. Load Testing (Optional)

#### Using Apache Bench

```bash
# Test flow listing endpoint
ab -n 100 -c 10 http://localhost:8000/api/flows

# Test health endpoint
ab -n 1000 -c 50 http://localhost:8000/health
```

#### Using wrk

```bash
# Install wrk
# sudo apt-get install wrk

# Test API
wrk -t12 -c400 -d30s http://localhost:8000/api/flows
```

## Testing Checklist

- [ ] Backend starts without errors
- [ ] Database tables are created
- [ ] API endpoints respond correctly
- [ ] Frontend builds successfully
- [ ] UI pages load correctly
- [ ] Monaco editor works
- [ ] Flow CRUD operations work
- [ ] Flow validation works
- [ ] Flow execution works
- [ ] Execution status updates in real-time
- [ ] Schedule CRUD operations work
- [ ] Scheduled jobs execute
- [ ] WebSocket connection works
- [ ] MCP tools page displays tools
- [ ] Docker images build successfully
- [ ] Docker Compose starts all services
- [ ] Services communicate correctly

## Troubleshooting

### Backend Won't Start

1. Check Python version: `python3 --version` (should be 3.11+)
2. Check dependencies: `pip list | grep fastapi`
3. Check database connection: Verify DATABASE_URL
4. Check logs: Look for error messages

### Frontend Won't Build

1. Check Node version: `node --version` (should be 20+)
2. Clear cache: `rm -rf node_modules package-lock.json && npm install`
3. Check TypeScript: `npx tsc --noEmit`
4. Check for syntax errors in .tsx files

### Docker Issues

1. Check Docker version: `docker --version`
2. Check Docker Compose version: `docker-compose --version`
3. Clear containers: `docker-compose down -v`
4. Rebuild images: `docker-compose build --no-cache`
5. Check logs: `docker-compose logs`

### Database Connection Failed

1. Check PostgreSQL is running: `docker ps | grep postgres`
2. Verify credentials in .env file
3. Check database exists: `docker exec crewai-postgres psql -U crewai -l`
4. Check network: `docker network ls`

## Performance Benchmarks

Expected performance on standard hardware:

- API response time: < 100ms
- Flow validation: < 500ms
- Flow execution: Depends on flow complexity
- WebSocket latency: < 50ms
- Frontend load time: < 2s

## Security Testing

### Basic Security Checks

1. **SQL Injection**: Try malicious inputs in API
2. **XSS**: Test YAML editor with script tags
3. **CORS**: Verify CORS headers are set correctly
4. **Authentication**: (To be implemented) Test auth flows
5. **Rate Limiting**: (To be implemented) Test rate limits

## Continuous Integration

For CI/CD pipelines, create a test script:

```bash
#!/bin/bash
set -e

echo "Running CI tests..."

# Backend tests
cd backend
python3 -m pytest tests/ || true

# Frontend tests
cd ../frontend
npm run lint
npm run build

echo "CI tests completed"
```

## Additional Resources

- FastAPI Testing: https://fastapi.tiangolo.com/tutorial/testing/
- React Testing Library: https://testing-library.com/docs/react-testing-library/intro/
- Docker Testing: https://docs.docker.com/compose/
