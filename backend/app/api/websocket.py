"""
WebSocket endpoint for real-time updates
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.websocket_manager import websocket_manager
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.websocket("/updates")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time execution updates
    
    Clients connect to this endpoint to receive real-time notifications
    about flow executions, status changes, and other events.
    """
    await websocket_manager.connect(websocket)
    try:
        # Send welcome message
        await websocket_manager.send_personal_message(
            {"type": "connected", "data": {"message": "Connected to CrewAI Flow Manager"}},
            websocket
        )
        
        # Keep connection alive and listen for messages
        while True:
            # Receive messages from client (for keep-alive or commands)
            data = await websocket.receive_text()
            logger.debug(f"Received WebSocket message: {data}")
            
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        websocket_manager.disconnect(websocket)
