"""
Node Instance Controller

This module provides API endpoints for managing node instances.
"""

from fastapi import APIRouter, HTTPException, Depends, Query, WebSocket, WebSocketDisconnect
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import logging

from backend.app.services.core_node_registry import CoreNodeRegistry
from backend.app.models.node_instance import NodeInstance, NodeInstanceCreate, NodeInstanceUpdate
from backend.app.services.websocket_manager import WebSocketManager

logger = logging.getLogger("workflow_builder")

router = APIRouter(prefix="/node-instances", tags=["Node Instances"])
node_registry = CoreNodeRegistry()
websocket_manager = WebSocketManager()

# In-memory store for node instances (would be replaced with database in production)
node_instances: Dict[str, NodeInstance] = {}

@router.get("/", response_model=List[NodeInstance])
async def get_all_node_instances(
    workflow_id: Optional[str] = None,
    skip: int = Query(0, description="Number of instances to skip"),
    limit: int = Query(100, description="Maximum number of instances to return")
):
    """Get all node instances with optional filtering by workflow."""
    if workflow_id:
        filtered_instances = [
            instance for instance in node_instances.values() 
            if instance.workflow_id == workflow_id
        ]
        return filtered_instances[skip:skip+limit]
    
    return list(node_instances.values())[skip:skip+limit]

@router.post("/", response_model=NodeInstance)
async def create_node_instance(instance_create: NodeInstanceCreate):
    """Create a new node instance."""
    # Check if node type exists
    if not node_registry.get_node(instance_create.node_type_id):
        raise HTTPException(status_code=404, detail=f"Node type {instance_create.node_type_id} not found")
    
    # Create instance
    new_instance = NodeInstance(
        node_type_id=instance_create.node_type_id,
        name=instance_create.name or f"{instance_create.node_type_id.split('.')[-1].title()} Instance",
        config=instance_create.config or {},
        position=instance_create.position,
        workflow_id=instance_create.workflow_id
    )
    
    node_instances[new_instance.id] = new_instance
    
    # Notify connected clients
    await websocket_manager.broadcast(
        json.dumps({
            "type": "node_instance_created",
            "data": new_instance.dict()
        })
    )
    
    return new_instance

@router.get("/{instance_id}", response_model=NodeInstance)
async def get_node_instance(instance_id: str):
    """Get a node instance by ID."""
    if instance_id not in node_instances:
        raise HTTPException(status_code=404, detail=f"Node instance {instance_id} not found")
    
    return node_instances[instance_id]

@router.put("/{instance_id}", response_model=NodeInstance)
async def update_node_instance(instance_id: str, update: NodeInstanceUpdate):
    """Update a node instance."""
    if instance_id not in node_instances:
        raise HTTPException(status_code=404, detail=f"Node instance {instance_id} not found")
    
    instance = node_instances[instance_id]
    
    # Update fields
    if update.name is not None:
        instance.name = update.name
    if update.config is not None:
        instance.config = update.config
    if update.position is not None:
        instance.position = update.position
    if update.workflow_id is not None:
        instance.workflow_id = update.workflow_id
    
    # Update timestamp
    instance.updated_at = datetime.utcnow()
    
    # Notify connected clients
    await websocket_manager.broadcast(
        json.dumps({
            "type": "node_instance_updated",
            "data": instance.dict()
        })
    )
    
    return instance

@router.delete("/{instance_id}")
async def delete_node_instance(instance_id: str):
    """Delete a node instance."""
    if instance_id not in node_instances:
        raise HTTPException(status_code=404, detail=f"Node instance {instance_id} not found")
    
    deleted_instance = node_instances.pop(instance_id)
    
    # Notify connected clients
    await websocket_manager.broadcast(
        json.dumps({
            "type": "node_instance_deleted",
            "data": {"id": instance_id}
        })
    )
    
    return {"status": "success", "message": f"Node instance {instance_id} deleted"}

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates to node instances."""
    await websocket_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Process incoming messages if needed
            # For now, we're just using WebSockets for server -> client communication
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)
