"""
Memory system models for KuroAI.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List
from .state import LocationType

@dataclass
class Memory:
    timestamp: datetime
    event_type: str
    description: str
    location: LocationType
    involved_npcs: List[str] = field(default_factory=list)
    emotional_impact: float = 0.0  # -1.0 to 1.0
