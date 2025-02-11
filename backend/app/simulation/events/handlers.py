"""
Event handling system for the simulation.
"""
from typing import Dict, Any, Callable, List
from ..core.agent import Agent
from ..models.npc import NPCProfile
from ..models.location import LocationType

class EventHandler:
    def __init__(self):
        self.handlers: Dict[str, List[Callable]] = {}
    
    def register(self, event_type: str, handler: Callable):
        """Register a new event handler."""
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        self.handlers[event_type].append(handler)
    
    async def handle(self, event_type: str, data: Dict[str, Any]):
        """Handle an event by calling all registered handlers."""
        if event_type in self.handlers:
            for handler in self.handlers[event_type]:
                await handler(data)

# Global event handler instance
event_handler = EventHandler()

# Register default handlers
@event_handler.register("kuro_moved")
async def handle_kuro_moved(data: Dict):
    """Handle Kuro movement events."""
    # TODO: Implement movement handling
    pass

@event_handler.register("interaction")
async def handle_interaction(data: Dict):
    """Handle interaction events between characters."""
    # TODO: Implement interaction handling
    pass
