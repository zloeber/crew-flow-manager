"""
CrewAI Flow Manager - Main Application Entry Point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import logging

from app.api import flows, executions, schedules, mcp_tools, mcp_servers, websocket
from app.core.config import settings
from app.db.database import engine, Base
from app.services.scheduler import scheduler_service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting CrewAI Flow Manager...")
    
    # Create database tables
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created")
    
    # Start scheduler
    scheduler_service.start()
    logger.info("Scheduler started")
    
    yield
    
    # Shutdown
    logger.info("Shutting down CrewAI Flow Manager...")
    scheduler_service.shutdown()
    logger.info("Scheduler stopped")


app = FastAPI(
    title="CrewAI Flow Manager",
    description="Manage, execute and monitor CrewAI Flows with real-time updates",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(flows.router, prefix="/api/flows", tags=["flows"])
app.include_router(executions.router, prefix="/api/executions", tags=["executions"])
app.include_router(schedules.router, prefix="/api/schedules", tags=["schedules"])
app.include_router(mcp_tools.router, prefix="/api/mcp-tools", tags=["mcp-tools"])
app.include_router(mcp_servers.router, prefix="/api/mcp-servers", tags=["mcp-servers"])
app.include_router(websocket.router, prefix="/ws", tags=["websocket"])


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "CrewAI Flow Manager API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health():
    """Detailed health check"""
    return {
        "status": "healthy",
        "scheduler": scheduler_service.is_running(),
        "database": "connected"
    }
