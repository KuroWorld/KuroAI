"""API routes for the simulation."""
import time
from typing import Dict, Optional, Set
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Depends
from pydantic import BaseModel

from ..simulation.events.models import EventType, SimulationEvent

from ..simulation.events.models import EventType
from ..simulation.core.simulation_manager import SimulationManager
from .websocket import SimulationWebSocket
from main import get_sim_manager

router = APIRouter()
websocket_manager = SimulationWebSocket()

from ..simulation.models.simulation_state import SimulationState

@router.get("/state", response_model=SimulationState)
async def get_simulation_state(sim_manager: SimulationManager = Depends(get_sim_manager)) -> SimulationState:
    """Get current simulation state."""
    if not sim_manager.agent:
        raise HTTPException(status_code=400, detail="Simulation not initialized")
        
    # Get NPCs grouped by location
    npcs_by_location = {}
    for loc_type, npcs in sim_manager.locations.items():
        npcs_by_location[loc_type.name] = [
            sim_manager.npcs[npc].name 
            for npc in npcs 
            if npc in sim_manager.npcs
        ]
    
    # Get current intent if any
    current_intent = None
    if sim_manager.agent.current_intent:
        intent = sim_manager.agent.current_intent
        current_intent = {
            "type": intent.type.name,
            "target": intent.target,
            "location": intent.location.name if intent.location else None,
            "status": intent.status.name
        }
    
    return SimulationState(
        is_running=sim_manager.is_running,
        tick_count=sim_manager.tick_count,
        agent_location=sim_manager.agent.location.name,
        npcs_by_location=npcs_by_location,
        current_intent=current_intent
    )


@router.websocket("/ws/{client_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    client_id: str,
    sim_manager: SimulationManager = Depends(get_sim_manager),
    event_types: Set[EventType] = None
) -> None:
    """WebSocket endpoint for real-time simulation events.
    
    Sends simulation events to the client in the format:
    {
        "type": "EVENT_TYPE",  # e.g., AGENT_MOVED, INTERACTION_STARTED
        "data": {...}         # Event-specific data
    }
    
    The simulation manager uses the LLM to determine the agent's actions,
    and this WebSocket connection simply streams those events to the client.
    
    Events include:
    - AGENT_MOVED: When the agent changes location
    - INTERACTION_STARTED: When the agent starts talking to an NPC
    - DIALOGUE_GENERATED: When conversation occurs
    - MEMORY_ADDED: When the agent learns something new
    
    Args:
        websocket: The WebSocket connection
        client_id: Unique identifier for the client
        sim_manager: The simulation manager instance
        event_types: Optional set of event types to subscribe to. If None, subscribes to all events.
    """
    await websocket.accept()
    
    # Subscribe to events
    if event_types is None:
        event_types = set(EventType)
        
    for event_type in event_types:
        sim_manager.event_bus.subscribe(
            event_type,
            lambda event: websocket.send_json({
                "type": event.type.name,
                "data": event.data
            })
        )
    
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        # Clean up subscriptions
        for event_type in event_types:
            sim_manager.event_bus.unsubscribe(event_type)
