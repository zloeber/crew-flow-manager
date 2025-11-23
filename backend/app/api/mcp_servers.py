"""
MCP Server management API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List
import json
import io

from app.db.database import get_db
from app.models.models import MCPServer
from app.schemas.schemas import (
    MCPServerCreate, MCPServerUpdate, MCPServerResponse, MCPServersImport
)
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/", response_model=List[MCPServerResponse])
def list_mcp_servers(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all MCP servers"""
    servers = db.query(MCPServer).offset(skip).limit(limit).all()
    return servers


@router.get("/{server_id}", response_model=MCPServerResponse)
def get_mcp_server(server_id: int, db: Session = Depends(get_db)):
    """Get a specific MCP server by ID"""
    server = db.query(MCPServer).filter(MCPServer.id == server_id).first()
    if not server:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"MCP Server with id {server_id} not found"
        )
    return server


@router.post("/", response_model=MCPServerResponse, status_code=status.HTTP_201_CREATED)
def create_mcp_server(server_data: MCPServerCreate, db: Session = Depends(get_db)):
    """Create a new MCP server"""
    # Check if server with same name exists
    existing = db.query(MCPServer).filter(MCPServer.name == server_data.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"MCP Server with name '{server_data.name}' already exists"
        )
    
    # Create server
    server = MCPServer(
        name=server_data.name,
        command=server_data.command,
        args=server_data.args,
        env=server_data.env,
        type=server_data.type,
        url=server_data.url,
        is_active=server_data.is_active
    )
    
    db.add(server)
    db.commit()
    db.refresh(server)
    
    logger.info(f"Created MCP server {server.id}: {server.name}")
    return server


@router.put("/{server_id}", response_model=MCPServerResponse)
def update_mcp_server(
    server_id: int,
    server_data: MCPServerUpdate,
    db: Session = Depends(get_db)
):
    """Update an existing MCP server"""
    server = db.query(MCPServer).filter(MCPServer.id == server_id).first()
    if not server:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"MCP Server with id {server_id} not found"
        )
    
    # Check name uniqueness if changing name
    if server_data.name and server_data.name != server.name:
        existing = db.query(MCPServer).filter(MCPServer.name == server_data.name).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"MCP Server with name '{server_data.name}' already exists"
            )
    
    # Update fields
    if server_data.name is not None:
        server.name = server_data.name
    if server_data.command is not None:
        server.command = server_data.command
    if server_data.args is not None:
        server.args = server_data.args
    if server_data.env is not None:
        server.env = server_data.env
    if server_data.type is not None:
        server.type = server_data.type
    if server_data.url is not None:
        server.url = server_data.url
    if server_data.is_active is not None:
        server.is_active = server_data.is_active
    
    db.commit()
    db.refresh(server)
    
    logger.info(f"Updated MCP server {server.id}: {server.name}")
    return server


@router.delete("/{server_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_mcp_server(server_id: int, db: Session = Depends(get_db)):
    """Delete an MCP server"""
    server = db.query(MCPServer).filter(MCPServer.id == server_id).first()
    if not server:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"MCP Server with id {server_id} not found"
        )
    
    db.delete(server)
    db.commit()
    
    logger.info(f"Deleted MCP server {server_id}")
    return None


@router.post("/import")
async def import_mcp_servers(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Import MCP servers from a JSON file (mcp.json format)"""
    if not file.filename.endswith('.json'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a JSON file (.json)"
        )
    
    try:
        content = await file.read()
        data = json.loads(content.decode('utf-8'))
        
        if 'servers' not in data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="JSON file must contain a 'servers' object"
            )
        
        created_servers = []
        errors = []
        
        for server_name, server_config in data['servers'].items():
            try:
                # Check if server already exists
                existing = db.query(MCPServer).filter(MCPServer.name == server_name).first()
                if existing:
                    errors.append(f"Server '{server_name}' already exists, skipping")
                    continue
                
                # Create server
                server = MCPServer(
                    name=server_name,
                    command=server_config.get('command', ''),
                    args=server_config.get('args', []),
                    env=server_config.get('env', {}),
                    type=server_config.get('type', 'stdio'),
                    url=server_config.get('url'),
                    is_active=True
                )
                
                db.add(server)
                created_servers.append(server_name)
                
            except Exception as e:
                errors.append(f"Error creating server '{server_name}': {str(e)}")
                logger.error(f"Error creating server '{server_name}': {str(e)}")
        
        if created_servers:
            db.commit()
        
        logger.info(f"Imported {len(created_servers)} MCP servers")
        return {
            "created": created_servers,
            "errors": errors,
            "total_created": len(created_servers)
        }
        
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid JSON format: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error importing MCP servers: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error importing MCP servers: {str(e)}"
        )


@router.get("/export/all")
def export_mcp_servers(db: Session = Depends(get_db)):
    """Export all MCP servers as a JSON file (mcp.json format)"""
    servers = db.query(MCPServer).all()
    
    if not servers:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No MCP servers found to export"
        )
    
    # Create JSON structure matching mcp.json format
    servers_dict = {}
    for server in servers:
        server_config = {
            "command": server.command,
            "type": server.type
        }
        
        if server.args:
            server_config["args"] = server.args
        
        if server.env:
            server_config["env"] = server.env
        
        if server.url:
            server_config["url"] = server.url
        
        servers_dict[server.name] = server_config
    
    export_data = {
        "servers": servers_dict,
        "inputs": []
    }
    
    # Create a file-like object
    json_content = json.dumps(export_data, indent=2)
    file_stream = io.BytesIO(json_content.encode('utf-8'))
    
    # Return as streaming response
    return StreamingResponse(
        file_stream,
        media_type="application/json",
        headers={
            "Content-Disposition": "attachment; filename=mcp_servers.json"
        }
    )
