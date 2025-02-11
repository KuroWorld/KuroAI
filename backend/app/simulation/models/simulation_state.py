"""Models for representing the overall simulation state."""
from typing import Dict, Optional
from pydantic import BaseModel

from .location import LocationType

class SimulationState(BaseModel):
    """Current state of the simulation.
    
    This model represents the overall state of the simulation,
    used primarily for API responses to provide a snapshot of
    the current simulation status.
    """
    is_running: bool
    tick_count: int
    agent_location: LocationType
    npcs_by_location: Dict[LocationType, list[str]]
    current_intent: Optional[dict] = None
