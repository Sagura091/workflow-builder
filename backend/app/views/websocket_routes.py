"""
WebSocket Routes

This module provides WebSocket routes for real-time communication.
"""

import json
import logging
import uuid
from typing import Dict, Any, Optional

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from starlette.websockets import WebSocketState

from backend.app.services.websocket_manager import WebSocketManager

# Configure logger
logger = logging.getLogger("workflow_builder")

# Create router
router = APIRouter(prefix="/api/ws", tags=["websockets"])

# WebSocket manager
websocket_manager = WebSocketManager()

@router.websocket("/connect")
async def websocket_connect(
    websocket: WebSocket,
    client_id: Optional[str] = Query(None),
    workflow_id: Optional[str] = Query(None)
):
    """Connect to WebSocket server."""
    # Generate client ID if not provided
    if not client_id:
        client_id = f"client-{uuid.uuid4()}"
    
    # Prepare client info
    client_info = {
        "client_id": client_id
    }
    
    # Add workflow ID if provided
    if workflow_id:
        client_info["workflow_id"] = workflow_id
    
    # Connect client
    await websocket_manager.connect(websocket, client_info)
    
    try:
        # Process messages
        while True:
            # Wait for message
            try:
                message = await websocket.receive_text()
                
                # Parse message
                try:
                    data = json.loads(message)
                    await process_message(websocket, data, client_id)
                except json.JSONDecodeError:
                    logger.warning(f"Invalid JSON message from client {client_id}: {message}")
                    await websocket_manager.send_personal_message({
                        "type": "error",
                        "message": "Invalid JSON message"
                    }, websocket)
            except WebSocketDisconnect:
                websocket_manager.disconnect(websocket)
                logger.info(f"Client {client_id} disconnected")
                break
            except Exception as e:
                logger.error(f"Error processing message from client {client_id}: {str(e)}")
                if websocket.client_state != WebSocketState.DISCONNECTED:
                    await websocket_manager.send_personal_message({
                        "type": "error",
                        "message": f"Error processing message: {str(e)}"
                    }, websocket)
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)
        logger.info(f"Client {client_id} disconnected")
    except Exception as e:
        logger.error(f"WebSocket error for client {client_id}: {str(e)}")
        websocket_manager.disconnect(websocket)

@router.websocket("/workflow/{workflow_id}")
async def websocket_workflow(
    websocket: WebSocket,
    workflow_id: str,
    client_id: Optional[str] = Query(None)
):
    """Connect to a specific workflow."""
    # Generate client ID if not provided
    if not client_id:
        client_id = f"client-{uuid.uuid4()}"
    
    # Prepare client info
    client_info = {
        "client_id": client_id,
        "workflow_id": workflow_id,
        "groups": [f"workflow-{workflow_id}"]
    }
    
    # Connect client
    await websocket_manager.connect(websocket, client_info)
    
    try:
        # Process messages
        while True:
            # Wait for message
            try:
                message = await websocket.receive_text()
                
                # Parse message
                try:
                    data = json.loads(message)
                    await process_message(websocket, data, client_id)
                except json.JSONDecodeError:
                    logger.warning(f"Invalid JSON message from client {client_id}: {message}")
                    await websocket_manager.send_personal_message({
                        "type": "error",
                        "message": "Invalid JSON message"
                    }, websocket)
            except WebSocketDisconnect:
                websocket_manager.disconnect(websocket)
                logger.info(f"Client {client_id} disconnected from workflow {workflow_id}")
                break
            except Exception as e:
                logger.error(f"Error processing message from client {client_id}: {str(e)}")
                if websocket.client_state != WebSocketState.DISCONNECTED:
                    await websocket_manager.send_personal_message({
                        "type": "error",
                        "message": f"Error processing message: {str(e)}"
                    }, websocket)
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)
        logger.info(f"Client {client_id} disconnected from workflow {workflow_id}")
    except Exception as e:
        logger.error(f"WebSocket error for client {client_id} in workflow {workflow_id}: {str(e)}")
        websocket_manager.disconnect(websocket)

@router.websocket("/execution/{execution_id}")
async def websocket_execution(
    websocket: WebSocket,
    execution_id: str,
    client_id: Optional[str] = Query(None)
):
    """Connect to a specific execution."""
    # Generate client ID if not provided
    if not client_id:
        client_id = f"client-{uuid.uuid4()}"
    
    # Prepare client info
    client_info = {
        "client_id": client_id,
        "executions": [execution_id],
        "groups": [f"execution-{execution_id}"]
    }
    
    # Connect client
    await websocket_manager.connect(websocket, client_info)
    
    try:
        # Process messages
        while True:
            # Wait for message
            try:
                message = await websocket.receive_text()
                
                # Parse message
                try:
                    data = json.loads(message)
                    await process_message(websocket, data, client_id)
                except json.JSONDecodeError:
                    logger.warning(f"Invalid JSON message from client {client_id}: {message}")
                    await websocket_manager.send_personal_message({
                        "type": "error",
                        "message": "Invalid JSON message"
                    }, websocket)
            except WebSocketDisconnect:
                websocket_manager.disconnect(websocket)
                logger.info(f"Client {client_id} disconnected from execution {execution_id}")
                break
            except Exception as e:
                logger.error(f"Error processing message from client {client_id}: {str(e)}")
                if websocket.client_state != WebSocketState.DISCONNECTED:
                    await websocket_manager.send_personal_message({
                        "type": "error",
                        "message": f"Error processing message: {str(e)}"
                    }, websocket)
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)
        logger.info(f"Client {client_id} disconnected from execution {execution_id}")
    except Exception as e:
        logger.error(f"WebSocket error for client {client_id} in execution {execution_id}: {str(e)}")
        websocket_manager.disconnect(websocket)

async def process_message(websocket: WebSocket, data: Dict[str, Any], client_id: str):
    """Process a WebSocket message."""
    # Get message type
    message_type = data.get("type")
    
    if not message_type:
        logger.warning(f"Message from client {client_id} has no type: {data}")
        await websocket_manager.send_personal_message({
            "type": "error",
            "message": "Message has no type"
        }, websocket)
        return
    
    # Process message based on type
    if message_type == "ping":
        # Respond to ping
        await websocket_manager.send_personal_message({
            "type": "pong",
            "timestamp": data.get("timestamp")
        }, websocket)
    
    elif message_type == "subscribe":
        # Subscribe to execution updates
        execution_id = data.get("execution_id")
        if execution_id:
            websocket_manager.subscribe_to_execution(client_id, execution_id)
            await websocket_manager.send_personal_message({
                "type": "subscribed",
                "execution_id": execution_id
            }, websocket)
        else:
            await websocket_manager.send_personal_message({
                "type": "error",
                "message": "Missing execution_id for subscribe"
            }, websocket)
    
    elif message_type == "unsubscribe":
        # Unsubscribe from execution updates
        execution_id = data.get("execution_id")
        if execution_id:
            websocket_manager.unsubscribe_from_execution(client_id, execution_id)
            await websocket_manager.send_personal_message({
                "type": "unsubscribed",
                "execution_id": execution_id
            }, websocket)
        else:
            await websocket_manager.send_personal_message({
                "type": "error",
                "message": "Missing execution_id for unsubscribe"
            }, websocket)
    
    elif message_type == "join_group":
        # Join a group
        group = data.get("group")
        if group:
            websocket_manager.add_to_group(client_id, group)
            await websocket_manager.send_personal_message({
                "type": "joined_group",
                "group": group
            }, websocket)
        else:
            await websocket_manager.send_personal_message({
                "type": "error",
                "message": "Missing group for join_group"
            }, websocket)
    
    elif message_type == "leave_group":
        # Leave a group
        group = data.get("group")
        if group:
            websocket_manager.remove_from_group(client_id, group)
            await websocket_manager.send_personal_message({
                "type": "left_group",
                "group": group
            }, websocket)
        else:
            await websocket_manager.send_personal_message({
                "type": "error",
                "message": "Missing group for leave_group"
            }, websocket)
    
    else:
        # Unknown message type
        logger.warning(f"Unknown message type from client {client_id}: {message_type}")
        await websocket_manager.send_personal_message({
            "type": "error",
            "message": f"Unknown message type: {message_type}"
        }, websocket)
