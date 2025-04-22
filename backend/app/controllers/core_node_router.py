"""
Core Node Router

This module provides API endpoints for core nodes.
"""

from fastapi import APIRouter, HTTPException, Query, WebSocket, WebSocketDisconnect
from typing import Dict, List, Any, Optional
import json
import logging

from backend.app.services.core_node_registry import CoreNodeRegistry
from backend.app.controllers.core_node_controller import CoreNodeController
from backend.app.services.websocket_manager import WebSocketManager

logger = logging.getLogger("workflow_builder")

router = APIRouter(prefix="/core-nodes", tags=["Core Nodes"])
node_registry = CoreNodeRegistry()
node_controller = CoreNodeController(node_registry)
websocket_manager = WebSocketManager()

@router.get("/")
async def get_all_core_nodes(
    skip: int = Query(0, description="Number of nodes to skip"),
    limit: int = Query(100, description="Maximum number of nodes to return"),
    full_metadata: bool = Query(False, description="Whether to include full metadata")
):
    """Get all core nodes with pagination."""
    nodes = node_registry.get_all_nodes()
    node_ids = list(nodes.keys())[skip:skip+limit]
    
    result = []
    for node_id in node_ids:
        if full_metadata:
            metadata = node_registry.get_node_metadata(node_id)
            if metadata:
                result.append(node_controller._format_node_metadata(node_id, metadata))
        else:
            # Return minimal metadata
            metadata = node_registry.get_node_metadata(node_id)
            if metadata:
                result.append({
                    "id": node_id,
                    "name": metadata.get("name", node_id.split(".")[-1].title()),
                    "category": metadata.get("category", "UNKNOWN").upper(),
                    "description": metadata.get("description", "")
                })
    
    return {
        "status": "success", 
        "data": result, 
        "total": len(nodes), 
        "skip": skip, 
        "limit": limit
    }

@router.get("/categories")
async def get_node_categories():
    """Get all node categories."""
    directories = node_registry.get_nodes_by_directory()
    return {"status": "success", "data": list(directories.keys())}

@router.get("/categories/{category}")
async def get_nodes_by_category(
    category: str,
    full_metadata: bool = Query(False, description="Whether to include full metadata")
):
    """Get all nodes in a category."""
    directories = node_registry.get_nodes_by_directory(category)
    
    if category not in directories:
        raise HTTPException(status_code=404, detail=f"Category {category} not found")
    
    node_ids = directories[category]
    result = []
    
    for node_id in node_ids:
        if full_metadata:
            metadata = node_registry.get_node_metadata(node_id)
            if metadata:
                result.append(node_controller._format_node_metadata(node_id, metadata))
        else:
            # Return minimal metadata
            metadata = node_registry.get_node_metadata(node_id)
            if metadata:
                result.append({
                    "id": node_id,
                    "name": metadata.get("name", node_id.split(".")[-1].title()),
                    "category": metadata.get("category", "UNKNOWN").upper(),
                    "description": metadata.get("description", "")
                })
    
    return {"status": "success", "data": result}

@router.get("/{node_id}")
async def get_core_node(node_id: str):
    """Get a specific core node by ID."""
    try:
        node_data = node_controller.get_node(node_id)
        return {"status": "success", "data": node_data}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates to core nodes."""
    await websocket_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Process incoming messages if needed
            # For now, we're just using WebSockets for server -> client communication
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)
