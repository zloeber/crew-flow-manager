"""
MCP Tools discovery API endpoints
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.schemas import MCPToolsResponse, MCPTool
from app.db.database import get_db
from app.models.models import MCPServer
from app.services.mcp_tools_loader import mcp_tools_loader
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/", response_model=MCPToolsResponse)
async def list_mcp_tools(db: Session = Depends(get_db)):
    """
    List available MCP server tools
    
    Loads tools from all active MCP servers configured in the database.
    """
    # Get all active MCP servers
    servers = db.query(MCPServer).filter(MCPServer.is_active == True).all()
    
    all_tools = []
    server_names = []
    
    for server in servers:
        server_names.append(server.name)
        
        # Load tools from server using mock data
        # In a full implementation, this would actually query the server
        mock_tools = mcp_tools_loader.get_mock_tools_for_server(server.name)
        
        for tool in mock_tools:
            all_tools.append(
                MCPTool(
                    name=tool["name"],
                    description=tool["description"],
                    server=server.name,
                    parameters=tool.get("parameters")
                )
            )
    
    return MCPToolsResponse(
        tools=all_tools,
        count=len(all_tools),
        servers=server_names
    )
