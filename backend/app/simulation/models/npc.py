"""NPC-related models."""
from dataclasses import dataclass
from typing import Dict

from .location import LocationType


@dataclass(frozen=True)
class NPCProfile:
    """Basic NPC information."""
    name: str
    role: str
    location: LocationType
    personality: Dict[str, str]  # Traits that influence behavior
    is_static: bool = True       # If True, NPC doesn't move/change state
