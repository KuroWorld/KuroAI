"""Location-related models for the simulation."""
from dataclasses import dataclass
from enum import Enum, auto
from typing import Set, Optional


class LocationType(Enum):
    """Types of locations in the simulation."""
    TOWN_SQUARE = auto()
    MARKET = auto()
    TAVERN = auto()
    LIBRARY = auto()
    PARK = auto()
    RESIDENTIAL = auto()
    GUILD_HALL = auto()
    
    def get_description(self) -> str:
        """Get a description of the location."""
        descriptions = {
            self.TOWN_SQUARE: "The bustling heart of the town where people gather",
            self.MARKET: "A lively marketplace with various vendors and goods",
            self.TAVERN: "A cozy establishment serving food and drinks",
            self.LIBRARY: "A quiet place filled with books and knowledge",
            self.PARK: "A peaceful green space for relaxation",
            self.RESIDENTIAL: "The living quarters where people reside",
            self.GUILD_HALL: "A grand building where adventurers gather"
        }
        return descriptions[self]


@dataclass
class Location:
    """Represents a location in the simulation."""
    type: LocationType
    name: str
    description: str
    connected_to: Set[LocationType]
    npcs_present: Set[str] = None
    special_features: Optional[dict] = None
    
    def __post_init__(self):
        """Initialize default values."""
        if self.npcs_present is None:
            self.npcs_present = set()
        if self.special_features is None:
            self.special_features = {}
