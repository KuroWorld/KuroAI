"""Time-related models for the simulation."""
from enum import Enum, auto
from dataclasses import dataclass


class TimeOfDay(Enum):
    """Represents different times of day in the simulation."""
    MORNING = auto()
    AFTERNOON = auto()
    EVENING = auto()
    NIGHT = auto()
    
    @classmethod
    def from_hour(cls, hour: int) -> 'TimeOfDay':
        """Convert hour (0-23) to TimeOfDay."""
        if 5 <= hour < 12:
            return cls.MORNING
        elif 12 <= hour < 17:
            return cls.AFTERNOON
        elif 17 <= hour < 22:
            return cls.EVENING
        else:
            return cls.NIGHT


@dataclass
class SimulationTime:
    """Represents time in the simulation.
    
    Time scale:
    - 1 tick = 15 seconds real time
    - 40 ticks = 1 simulation hour (10 real minutes)
    - 960 ticks = 1 simulation day (4 real hours)
    """
    total_ticks: int
    start_hour: int  # Hour when simulation started (0-23)
    
    @property
    def day(self) -> int:
        """Get the current simulation day (1-based)."""
        total_hours = self.start_hour + ((self.total_ticks) // 40)
        return (total_hours // 24) + 1
    
    @property
    def hour(self) -> int:
        """Get the current hour (0-23)."""
        total_hours = self.start_hour + ((self.total_ticks) // 40)
        return total_hours % 24
    
    @property
    def time_of_day(self) -> TimeOfDay:
        """Get the current time of day."""
        return TimeOfDay.from_hour(self.hour)
    
    def __str__(self) -> str:
        return f"Day {self.day}, {self.hour:02d}:00 ({self.time_of_day.name})"
