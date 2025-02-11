"""Event-related models and types for the simulation."""
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, Optional

from ..models.location import LocationType


class EventType(Enum):
    """Types of events that can occur in the simulation."""
    # Agent events
    AGENT_MOVED = auto()
    AGENT_INTENT_FORMED = auto()
    AGENT_INTENT_COMPLETED = auto()
    
    # Interaction events
    INTERACTION_STARTED = auto()
    INTERACTION_ENDED = auto()
    DIALOGUE_GENERATED = auto()
    
    # Knowledge events
    KNOWLEDGE_GAINED = auto()
    MEMORY_ADDED = auto()
    
    # Simulation lifecycle events
    SIMULATION_STARTED = auto()
    SIMULATION_STOPPED = auto()
    SIMULATION_RESET = auto()
    
    # Environmental events
    WEATHER_CHANGED = auto()
    
    # Simulation tick events
    TICK_STARTED = auto()
    TICK_COMPLETED = auto()
    ERROR_OCCURRED = auto()


@dataclass(frozen=True)
class SimulationEvent:
    """Base event class for all simulation events."""
    type: EventType
    agent_id: str
    timestamp: float
    data: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def create_move_event(
        cls,
        agent_id: str,
        old_location: LocationType,
        new_location: LocationType,
        timestamp: float
    ) -> "SimulationEvent":
        """Create a movement event."""
        return cls(
            type=EventType.AGENT_MOVED,
            agent_id=agent_id,
            timestamp=timestamp,
            data={
                "old_location": old_location,
                "new_location": new_location
            }
        )
    
    @classmethod
    def create_intent_event(
        cls,
        agent_id: str,
        intent_type: str,
        timestamp: float,
        target: Optional[str] = None,
        location: Optional[LocationType] = None
    ) -> "SimulationEvent":
        """Create an intent formation event."""
        return cls(
            type=EventType.AGENT_INTENT_FORMED,
            agent_id=agent_id,
            timestamp=timestamp,
            data={
                "intent_type": intent_type,
                "target": target,
                "location": location
            }
        )
    
    @classmethod
    def create_interaction_event(
        cls,
        agent_id: str,
        target_id: str,
        location: LocationType,
        timestamp: float,
        is_start: bool = True
    ) -> "SimulationEvent":
        """Create an interaction event."""
        return cls(
            type=EventType.INTERACTION_STARTED if is_start else EventType.INTERACTION_ENDED,
            agent_id=agent_id,
            timestamp=timestamp,
            data={
                "target_id": target_id,
                "location": location
            }
        )
