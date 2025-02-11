"""WebSocket handler for streaming simulation events."""
from typing import Dict, Set
import json
import logging
from fastapi import WebSocket, WebSocketDisconnect

from ..simulation.events.models import SimulationEvent, EventType

logger = logging.getLogger(__name__)


class SimulationWebSocket:
    """Manages WebSocket connections and event broadcasting."""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.subscriptions: Dict[str, Set[EventType]] = {}
    
    async def connect(
        self,
        websocket: WebSocket,
        client_id: str,
        event_types: Set[EventType] = None
    ) -> None:
        """Accept a new WebSocket connection."""
        await websocket.accept()
        self.active_connections[client_id] = websocket
        self.subscriptions[client_id] = event_types or set(EventType)
        
        logger.info(f"Client {client_id} connected")
    
    def disconnect(self, client_id: str) -> None:
        """Handle client disconnection."""
        self.active_connections.pop(client_id, None)
        self.subscriptions.pop(client_id, None)
        logger.info(f"Client {client_id} disconnected")
    
    async def broadcast_event(self, event: SimulationEvent) -> None:
        """Broadcast an event to all subscribed clients."""
        disconnected = []
        
        for client_id, websocket in self.active_connections.items():
            if event.type in self.subscriptions[client_id]:
                try:
                    await websocket.send_json({
                        "type": event.type.name,
                        "agent_id": event.agent_id,
                        "timestamp": event.timestamp,
                        "data": event.data
                    })
                except WebSocketDisconnect:
                    disconnected.append(client_id)
                except Exception as e:
                    logger.error(f"Error sending to client {client_id}: {e}")
                    disconnected.append(client_id)
        
        # Clean up disconnected clients
        for client_id in disconnected:
            self.disconnect(client_id)
    
    async def send_message(self, client_id: str, message: dict) -> None:
        """Send a message to a specific client."""
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].send_json(message)
            except Exception as e:
                logger.error(f"Error sending to client {client_id}: {e}")
                self.disconnect(client_id)
