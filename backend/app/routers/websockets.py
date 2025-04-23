"""
WebSockets Router

This module provides WebSocket endpoints for real-time communication.
"""

import json
import logging
import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from starlette.websockets import WebSocketState

from backend.app.models.websocket_models import WebSocketMessage, MessageType
from backend.app.services.websocket_manager import WebSocketManager

# Configure logger
logger = logging.getLogger("workflow_builder")

# Create router with API versioning
router = APIRouter(prefix="/api/v1/ws", tags=["WebSockets"])

# WebSocket manager
websocket_manager = WebSocketManager()

@router.websocket("/connect")
async def websocket_connect(
    websocket: WebSocket,
    client_id: Optional[str] = Query(None),
    token: Optional[str] = Query(None),
    user_agent: Optional[str] = Query(None)
):
    """Connect to WebSocket server."""
    # Generate client ID if not provided
    if not client_id:
        client_id = f"client-{uuid.uuid4()}"

    # Get user agent from header if not provided
    if not user_agent and "user-agent" in websocket.headers:
        user_agent = websocket.headers.get("user-agent")

    # Prepare client info
    client_info = {
        "user_id": None,  # Will be set if token is valid
        "user_agent": user_agent,
        "connected_at": datetime.now().isoformat()
    }

    # Connect client
    connection_success = await websocket_manager.connect(websocket, client_id, client_info)
    if not connection_success:
        logger.warning(f"Failed to connect client {client_id}")
        return

    # Authenticate if token provided
    if token:
        # Authentication will be handled by the message handler
        await websocket_manager.process_message(client_id, {
            "type": MessageType.AUTH_REQUEST,
            "data": {"token": token}
        })

    try:
        # Process messages
        while True:
            # Wait for message
            try:
                message = await websocket.receive_text()

                # Parse message
                try:
                    data = json.loads(message)
                    await websocket_manager.process_message(client_id, data)
                except json.JSONDecodeError:
                    logger.warning(f"Invalid JSON message from client {client_id}: {message}")
                    await websocket_manager.send_personal_message(
                        WebSocketMessage(
                            type=MessageType.ERROR,
                            data={
                                "code": "invalid_json",
                                "message": "Invalid JSON message"
                            }
                        ),
                        client_id
                    )
            except WebSocketDisconnect:
                await websocket_manager.disconnect(client_id, reason="Client disconnected")
                logger.info(f"Client {client_id} disconnected")
                break
            except Exception as e:
                logger.error(f"Error processing message from client {client_id}: {str(e)}")
                if websocket.client_state != WebSocketState.DISCONNECTED:
                    await websocket_manager.send_personal_message(
                        WebSocketMessage(
                            type=MessageType.ERROR,
                            data={
                                "code": "message_processing_error",
                                "message": "Error processing message"
                            }
                        ),
                        client_id
                    )
    except Exception as e:
        logger.error(f"WebSocket error for client {client_id}: {str(e)}")
        await websocket_manager.disconnect(client_id, reason="WebSocket error")

@router.websocket("/workflow/{workflow_id}")
async def websocket_workflow(
    websocket: WebSocket,
    workflow_id: str,
    client_id: Optional[str] = Query(None),
    token: Optional[str] = Query(None),
    user_agent: Optional[str] = Query(None)
):
    """Connect to a specific workflow."""
    # Generate client ID if not provided
    if not client_id:
        client_id = f"client-{uuid.uuid4()}"

    # Get user agent from header if not provided
    if not user_agent and "user-agent" in websocket.headers:
        user_agent = websocket.headers.get("user-agent")

    # Prepare client info
    client_info = {
        "user_id": None,  # Will be set if token is valid
        "user_agent": user_agent,
        "workflow_id": workflow_id,
        "groups": [f"workflow-{workflow_id}"],
        "connected_at": datetime.now().isoformat()
    }

    # Connect client
    connection_success = await websocket_manager.connect(websocket, client_id, client_info)
    if not connection_success:
        logger.warning(f"Failed to connect client {client_id} to workflow {workflow_id}")
        return

    # Authenticate if token provided
    if token:
        # Authentication will be handled by the message handler
        await websocket_manager.process_message(client_id, {
            "type": MessageType.AUTH_REQUEST,
            "data": {"token": token}
        })

    # Subscribe to workflow group
    await websocket_manager.process_message(client_id, {
        "type": MessageType.SUBSCRIBE,
        "data": {"group": f"workflow-{workflow_id}"}
    })

    try:
        # Process messages
        while True:
            # Wait for message
            try:
                message = await websocket.receive_text()

                # Parse message
                try:
                    data = json.loads(message)
                    await websocket_manager.process_message(client_id, data)
                except json.JSONDecodeError:
                    logger.warning(f"Invalid JSON message from client {client_id}: {message}")
                    await websocket_manager.send_personal_message(
                        WebSocketMessage(
                            type=MessageType.ERROR,
                            data={
                                "code": "invalid_json",
                                "message": "Invalid JSON message"
                            }
                        ),
                        client_id
                    )
            except WebSocketDisconnect:
                await websocket_manager.disconnect(client_id, reason="Client disconnected from workflow")
                logger.info(f"Client {client_id} disconnected from workflow {workflow_id}")
                break
            except Exception as e:
                logger.error(f"Error processing message from client {client_id}: {str(e)}")
                if websocket.client_state != WebSocketState.DISCONNECTED:
                    await websocket_manager.send_personal_message(
                        WebSocketMessage(
                            type=MessageType.ERROR,
                            data={
                                "code": "message_processing_error",
                                "message": "Error processing message"
                            }
                        ),
                        client_id
                    )
    except Exception as e:
        logger.error(f"WebSocket error for client {client_id} in workflow {workflow_id}: {str(e)}")
        await websocket_manager.disconnect(client_id, reason="WebSocket error in workflow connection")

@router.websocket("/execution/{execution_id}")
async def websocket_execution(
    websocket: WebSocket,
    execution_id: str,
    client_id: Optional[str] = Query(None),
    token: Optional[str] = Query(None),
    user_agent: Optional[str] = Query(None)
):
    """Connect to a specific execution."""
    # Generate client ID if not provided
    if not client_id:
        client_id = f"client-{uuid.uuid4()}"

    # Get user agent from header if not provided
    if not user_agent and "user-agent" in websocket.headers:
        user_agent = websocket.headers.get("user-agent")

    # Prepare client info
    client_info = {
        "user_id": None,  # Will be set if token is valid
        "user_agent": user_agent,
        "executions": [execution_id],
        "groups": [f"execution-{execution_id}"],
        "connected_at": datetime.now().isoformat()
    }

    # Connect client
    connection_success = await websocket_manager.connect(websocket, client_id, client_info)
    if not connection_success:
        logger.warning(f"Failed to connect client {client_id} to execution {execution_id}")
        return

    # Authenticate if token provided
    if token:
        # Authentication will be handled by the message handler
        await websocket_manager.process_message(client_id, {
            "type": MessageType.AUTH_REQUEST,
            "data": {"token": token}
        })

    # Subscribe to execution updates
    await websocket_manager.process_message(client_id, {
        "type": MessageType.EXECUTION_SUBSCRIBE,
        "data": {"execution_id": execution_id}
    })

    # Subscribe to execution group
    await websocket_manager.process_message(client_id, {
        "type": MessageType.SUBSCRIBE,
        "data": {"group": f"execution-{execution_id}"}
    })

    try:
        # Process messages
        while True:
            # Wait for message
            try:
                message = await websocket.receive_text()

                # Parse message
                try:
                    data = json.loads(message)
                    await websocket_manager.process_message(client_id, data)
                except json.JSONDecodeError:
                    logger.warning(f"Invalid JSON message from client {client_id}: {message}")
                    await websocket_manager.send_personal_message(
                        WebSocketMessage(
                            type=MessageType.ERROR,
                            data={
                                "code": "invalid_json",
                                "message": "Invalid JSON message"
                            }
                        ),
                        client_id
                    )
            except WebSocketDisconnect:
                await websocket_manager.disconnect(client_id, reason="Client disconnected from execution")
                logger.info(f"Client {client_id} disconnected from execution {execution_id}")
                break
            except Exception as e:
                logger.error(f"Error processing message from client {client_id}: {str(e)}")
                if websocket.client_state != WebSocketState.DISCONNECTED:
                    await websocket_manager.send_personal_message(
                        WebSocketMessage(
                            type=MessageType.ERROR,
                            data={
                                "code": "message_processing_error",
                                "message": "Error processing message"
                            }
                        ),
                        client_id
                    )
    except Exception as e:
        logger.error(f"WebSocket error for client {client_id} in execution {execution_id}: {str(e)}")
        await websocket_manager.disconnect(client_id, reason="WebSocket error in execution connection")


# Add a statistics endpoint
@router.get("/stats", tags=["WebSockets"])
async def get_websocket_stats():
    """Get WebSocket connection statistics."""
    return websocket_manager.get_connection_stats()
