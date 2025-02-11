"""World state models for the simulation."""
from enum import Enum, auto
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel, Field

from datetime import datetime
from .time import SimulationTime, TimeOfDay
from .weather import Weather, WeatherSystem
from ..core.redis import RedisModel


class WorldState(RedisModel):
    """Current state of the simulation world.
    
    This model represents the environmental and temporal state
    of the simulation world. It uses simulation time rather than
    real time, allowing for time compression/expansion.
    
    The state is stored in Redis with automatic persistence.
    Key format: "world_state:{simulation_id}"
    """
    simulation_id: str = Field(..., description="Unique identifier for this simulation instance")
    timestamp: float = Field(..., description="Unix timestamp when this state was last updated")
    
    # Time tracking
    started_at: float = Field(..., description="Unix timestamp when simulation started")
    total_ticks: int = Field(0, description="Total number of simulation ticks since start")
    
    # Environmental conditions
    weather: Weather = Field(Weather.SUNNY, description="Current weather in the simulation")
    current_events: List[str] = Field(default_factory=list, description="List of active world events")
    
    # Systems
    _weather_system: Optional[WeatherSystem] = None
    
    @property
    def redis_key(self) -> str:
        """Get Redis key for this world state."""
        return f"world_state:{self.simulation_id}"
    
    async def update_weather(self) -> Optional[Weather]:
        """Update weather based on time of day and current conditions.
        Returns the new weather if it changed, None otherwise.
        """
        if not self._weather_system:
            self._weather_system = WeatherSystem(self.weather)
            
        new_weather = self._weather_system.update(
            total_ticks=self.total_ticks,
            time_of_day=self.time_of_day.name
        )
        
        if new_weather:
            self.weather = new_weather
            await self.save()  # Persist to Redis
            
        return new_weather
    
    @property
    def simulation_time(self) -> SimulationTime:
        """Get current simulation time based on total ticks and start time."""
        start_datetime = datetime.fromtimestamp(self.started_at)
        return SimulationTime(
            total_ticks=self.total_ticks,
            start_hour=start_datetime.hour
        )
    
    @property
    def time_of_day(self) -> TimeOfDay:
        """Get current time of day."""
        return self.simulation_time.time_of_day
    
    @property
    def day_number(self) -> int:
        """Get current simulation day number (1-based)."""
        return self.simulation_time.day
    
    class Config:
        use_enum_values = True
