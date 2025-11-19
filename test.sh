#!/bin/bash

# Test script for CrewAI Flow Manager
# This script performs basic validation tests

set -e

echo "====================================="
echo "CrewAI Flow Manager - Test Suite"
echo "====================================="
echo ""

# Test 1: Check directory structure
echo "Test 1: Checking directory structure..."
if [ -d "backend/app" ] && [ -d "frontend/src" ]; then
    echo "✓ Directory structure is correct"
else
    echo "✗ Directory structure is incorrect"
    exit 1
fi

# Test 2: Check Python files
echo ""
echo "Test 2: Checking Python syntax..."
cd backend
python3 -m py_compile app/main.py
python3 -m py_compile app/core/config.py
python3 -m py_compile app/db/database.py
python3 -m py_compile app/models/models.py
python3 -m py_compile app/api/flows.py
python3 -m py_compile app/api/executions.py
python3 -m py_compile app/api/schedules.py
python3 -m py_compile app/services/flow_validator.py
python3 -m py_compile app/services/flow_executor.py
python3 -m py_compile app/services/scheduler.py
echo "✓ All Python files have valid syntax"
cd ..

# Test 3: Check required files exist
echo ""
echo "Test 3: Checking required files..."
required_files=(
    "docker-compose.yml"
    "backend/Dockerfile"
    "backend/requirements.txt"
    "frontend/Dockerfile"
    "frontend/package.json"
    "frontend/tsconfig.json"
    "frontend/vite.config.ts"
    "README.md"
)

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo "✓ $file exists"
    else
        echo "✗ $file is missing"
        exit 1
    fi
done

# Test 4: Check backend dependencies
echo ""
echo "Test 4: Checking backend requirements..."
if grep -q "fastapi" backend/requirements.txt && \
   grep -q "sqlalchemy" backend/requirements.txt && \
   grep -q "apscheduler" backend/requirements.txt && \
   grep -q "crewai" backend/requirements.txt; then
    echo "✓ Backend requirements include all necessary packages"
else
    echo "✗ Backend requirements are missing some packages"
    exit 1
fi

# Test 5: Check frontend dependencies
echo ""
echo "Test 5: Checking frontend package.json..."
if grep -q "react" frontend/package.json && \
   grep -q "typescript" frontend/package.json && \
   grep -q "vite" frontend/package.json && \
   grep -q "tailwindcss" frontend/package.json && \
   grep -q "@monaco-editor/react" frontend/package.json; then
    echo "✓ Frontend package.json includes all necessary packages"
else
    echo "✗ Frontend package.json is missing some packages"
    exit 1
fi

# Test 6: Check Docker configuration
echo ""
echo "Test 6: Checking Docker configuration..."
if grep -q "postgres:16" docker-compose.yml && \
   grep -q "backend:" docker-compose.yml && \
   grep -q "frontend:" docker-compose.yml; then
    echo "✓ Docker Compose configuration is valid"
else
    echo "✗ Docker Compose configuration has issues"
    exit 1
fi

echo ""
echo "====================================="
echo "All tests passed! ✓"
echo "====================================="
echo ""
echo "Next steps:"
echo "1. Copy backend/.env.example to backend/.env and configure"
echo "2. Run: docker-compose up -d"
echo "3. Access frontend at http://localhost:3000"
echo "4. Access backend API at http://localhost:8000/docs"
