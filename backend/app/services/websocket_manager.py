"""
WebSocket Manager Service

This module provides a manager for WebSocket connections.
"""

from fastapi import WebSocket, WebSocketDisconnect
from typing import List, Dict, Any, Optional, Set
import logging
import json
import asyncio
import datetime

logger = logging.getLogger("workflow_builder")

class WebSocketManager:
    """Manager for WebSocket connections."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(WebSocketManager, cls).__new__(cls)
            cls._instance.active_connections: List[WebSocket] = []
            cls._instance.connection_info: Dict[WebSocket, Dict[str, Any]] = {}
            cls._instance.client_ids: Dict[str, WebSocket] = {}
            cls._instance.execution_subscriptions: Dict[str, Set[str]] = {}
            cls._instance.group_connections: Dict[str, Set[str]] = {}
        return cls._instance

    async def connect(self, websocket: WebSocket, client_info: Dict[str, Any] = None):
        """Connect a new WebSocket client."""
        await websocket.accept()
        self.active_connections.append(websocket)

        # Initialize client info
        client_info = client_info or {}
        self.connection_info[websocket] = client_info

        # Store client ID if provided
        client_id = client_info.get("client_id")
        if client_id:
            self.client_ids[client_id] = websocket

            # Add to groups if specified
            groups = client_info.get("groups", [])
            for group in groups:
                self.add_to_group(client_id, group)

            # Subscribe to executions if specified
            executions = client_info.get("executions", [])
            for execution_id in executions:
                self.subscribe_to_execution(client_id, execution_id)

        logger.info(f"New WebSocket connection. Total connections: {len(self.active_connections)}")

        # Send welcome message
        try:
            await websocket.send_json({
                "type": "connection_established",
                "timestamp": datetime.datetime.now().isoformat(),
                "message": "Connected to Workflow Builder WebSocket server"
            })
        except Exception as e:
            logger.error(f"Error sending welcome message: {e}")

    def disconnect(self, websocket: WebSocket):
        """Disconnect a WebSocket client."""
        # Get client ID before removing connection
        client_id = None
        if websocket in self.connection_info:
            client_id = self.connection_info[websocket].get("client_id")

        # Remove from active connections
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

        # Remove from connection info
        if websocket in self.connection_info:
            del self.connection_info[websocket]

        # Remove from client IDs
        if client_id and client_id in self.client_ids:
            del self.client_ids[client_id]

            # Remove from all groups
            for group in list(self.group_connections.keys()):
                if client_id in self.group_connections[group]:
                    self.group_connections[group].remove(client_id)

                    # Clean up empty groups
                    if not self.group_connections[group]:
                        del self.group_connections[group]

            # Remove from execution subscriptions
            for execution_id in list(self.execution_subscriptions.keys()):
                if client_id in self.execution_subscriptions[execution_id]:
                    self.execution_subscriptions[execution_id].remove(client_id)

                    # Clean up empty subscriptions
                    if not self.execution_subscriptions[execution_id]:
                        del self.execution_subscriptions[execution_id]

        logger.info(f"WebSocket disconnected. Remaining connections: {len(self.active_connections)}")

    def add_to_group(self, client_id: str, group: str) -> None:
        """Add a client to a group."""
        if group not in self.group_connections:
            self.group_connections[group] = set()

        self.group_connections[group].add(client_id)
        logger.debug(f"Client {client_id} added to group {group}")

    def remove_from_group(self, client_id: str, group: str) -> None:
        """Remove a client from a group."""
        if group in self.group_connections and client_id in self.group_connections[group]:
            self.group_connections[group].remove(client_id)

            # Clean up empty groups
            if not self.group_connections[group]:
                del self.group_connections[group]

            logger.debug(f"Client {client_id} removed from group {group}")

    def subscribe_to_execution(self, client_id: str, execution_id: str) -> None:
        """Subscribe a client to execution updates."""
        if execution_id not in self.execution_subscriptions:
            self.execution_subscriptions[execution_id] = set()

        self.execution_subscriptions[execution_id].add(client_id)
        logger.debug(f"Client {client_id} subscribed to execution {execution_id}")

    def unsubscribe_from_execution(self, client_id: str, execution_id: str) -> None:
        """Unsubscribe a client from execution updates."""
        if execution_id in self.execution_subscriptions and client_id in self.execution_subscriptions[execution_id]:
            self.execution_subscriptions[execution_id].remove(client_id)

            # Clean up empty subscriptions
            if not self.execution_subscriptions[execution_id]:
                del self.execution_subscriptions[execution_id]

            logger.debug(f"Client {client_id} unsubscribed from execution {execution_id}")

    async def send_personal_message(self, message: Any, websocket: WebSocket):
        """Send a message to a specific client."""
        try:
            if isinstance(message, str):
                await websocket.send_text(message)
            else:
                await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
            self.disconnect(websocket)

    async def send_message_by_client_id(self, message: Any, client_id: str) -> bool:
        """Send a message to a client by ID."""
        if client_id not in self.client_ids:
            logger.warning(f"Client ID {client_id} not found")
            return False

        websocket = self.client_ids[client_id]
        try:
            if isinstance(message, str):
                await websocket.send_text(message)
            else:
                await websocket.send_json(message)
            return True
        except Exception as e:
            logger.error(f"Error sending message to client {client_id}: {e}")
            self.disconnect(websocket)
            return False

    async def broadcast(self, message: Any, exclude: Optional[WebSocket] = None):
        """Broadcast a message to all connected clients."""
        disconnected_websockets = []

        for websocket in self.active_connections:
            if websocket != exclude:
                try:
                    if isinstance(message, str):
                        await websocket.send_text(message)
                    else:
                        await websocket.send_json(message)
                except Exception as e:
                    logger.error(f"Error broadcasting message: {e}")
                    disconnected_websockets.append(websocket)

        # Clean up disconnected websockets
        for websocket in disconnected_websockets:
            self.disconnect(websocket)

    async def broadcast_to_workflow(self, message: Any, workflow_id: str, exclude: Optional[WebSocket] = None):
        """Broadcast a message to all clients connected to a specific workflow."""
        disconnected_websockets = []

        for websocket in self.active_connections:
            if websocket != exclude and self.connection_info.get(websocket, {}).get("workflow_id") == workflow_id:
                try:
                    if isinstance(message, str):
                        await websocket.send_text(message)
                    else:
                        await websocket.send_json(message)
                except Exception as e:
                    logger.error(f"Error broadcasting message to workflow: {e}")
                    disconnected_websockets.append(websocket)

        # Clean up disconnected websockets
        for websocket in disconnected_websockets:
            self.disconnect(websocket)

    async def broadcast_to_group(self, message: Any, group: str):
        """Broadcast a message to a group of clients."""
        if group not in self.group_connections:
            logger.debug(f"No clients in group {group}")
            return

        disconnected_clients = []

        for client_id in self.group_connections[group]:
            if client_id in self.client_ids:
                try:
                    websocket = self.client_ids[client_id]
                    if isinstance(message, str):
                        await websocket.send_text(message)
                    else:
                        await websocket.send_json(message)
                except Exception as e:
                    logger.error(f"Error sending message to client {client_id} in group {group}: {e}")
                    disconnected_clients.append(client_id)

        # Clean up disconnected clients
        for client_id in disconnected_clients:
            if client_id in self.client_ids:
                self.disconnect(self.client_ids[client_id])

    async def broadcast_execution_update(self, execution_id: str, update_type: str, data: Dict[str, Any]):
        """Broadcast an execution update to subscribed clients."""
        if execution_id not in self.execution_subscriptions:
            logger.debug(f"No clients subscribed to execution {execution_id}")
            return

        message = {
            "type": "execution_update",
            "execution_id": execution_id,
            "update_type": update_type,
            "timestamp": datetime.datetime.now().isoformat(),
            "data": data
        }

        disconnected_clients = []

        for client_id in self.execution_subscriptions[execution_id]:
            if client_id in self.client_ids:
                try:
                    websocket = self.client_ids[client_id]
                    await websocket.send_json(message)
                except Exception as e:
                    logger.error(f"Error sending execution update to client {client_id}: {e}")
                    disconnected_clients.append(client_id)

        # Clean up disconnected clients
        for client_id in disconnected_clients:
            if client_id in self.client_ids:
                self.disconnect(self.client_ids[client_id])
