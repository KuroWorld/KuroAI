"""Weather system for the simulation.

NOTE: This is a simplified rule-based weather system that will be enhanced in the future.
The planned enhancement will use the LLM to determine weather patterns based on:
- Historical weather patterns
- Current world events
- Story context and dramatic timing
- Character activities and planned events
- Seasonal patterns

This will create more meaningful and contextually appropriate weather changes
that enhance the narrative experience.
"""
from enum import Enum, auto
from dataclasses import dataclass
from typing import Dict, Set, Optional
import random
from datetime import datetime

class Weather(Enum):
    """Weather conditions in the simulation."""
    SUNNY = auto()
    PARTLY_CLOUDY = auto()
    CLOUDY = auto()
    RAINY = auto()
    STORMY = auto()
    
    def get_description(self) -> str:
        """Get a description of the weather."""
        descriptions = {
            self.SUNNY: "The sun shines brightly in the sky",
            self.PARTLY_CLOUDY: "A few clouds drift across the sun",
            self.CLOUDY: "Gray clouds blanket the sky",
            self.RAINY: "Rain falls steadily from the sky",
            self.STORMY: "Thunder and lightning fill the air"
        }
        return descriptions[self]


class WeatherSystem:
    """System for simulating weather changes.
    
    Weather changes are based on:
    1. Current weather
    2. Time of day
    3. Season (derived from simulation day)
    4. Random chance with weighted probabilities
    """
    
    # Define possible weather transitions
    # Weather can only change to an adjacent state
    TRANSITIONS: Dict[Weather, Set[Weather]] = {
        Weather.SUNNY: {Weather.PARTLY_CLOUDY},
        Weather.PARTLY_CLOUDY: {Weather.SUNNY, Weather.CLOUDY},
        Weather.CLOUDY: {Weather.PARTLY_CLOUDY, Weather.RAINY},
        Weather.RAINY: {Weather.CLOUDY, Weather.STORMY},
        Weather.STORMY: {Weather.RAINY}
    }
    
    # Weather change probabilities per time of day
    # Format: (chance_better, chance_worse)
    TIME_PROBABILITIES = {
        "MORNING": (0.4, 0.1),    # More likely to improve in morning
        "AFTERNOON": (0.2, 0.3),  # Slightly worse in afternoon
        "EVENING": (0.1, 0.2),    # Slightly worse in evening
        "NIGHT": (0.2, 0.1)       # Stable at night
    }
    
    def __init__(self, current_weather: Weather = Weather.SUNNY):
        self.current_weather = current_weather
        self._last_update_tick = 0
    
    def update(self, total_ticks: int, time_of_day: str) -> Optional[Weather]:
        """Update weather based on current conditions.
        
        Returns new weather if it changed, None otherwise.
        Updates every 120 ticks (3 simulation hours).
        """
        # Only update every 120 ticks
        if total_ticks - self._last_update_tick < 120:
            return None
            
        self._last_update_tick = total_ticks
        
        # Get probabilities for current time
        better_chance, worse_chance = self.TIME_PROBABILITIES[time_of_day]
        
        # Roll for weather change
        roll = random.random()
        
        # Determine if weather should change
        possible_transitions = self.TRANSITIONS[self.current_weather]
        if not possible_transitions:
            return None
            
        # Get better and worse weather options
        weather_list = list(Weather)
        current_idx = weather_list.index(self.current_weather)
        better = weather_list[current_idx - 1] if current_idx > 0 else None
        worse = weather_list[current_idx + 1] if current_idx < len(weather_list) - 1 else None
        
        # Change weather based on roll and valid transitions
        new_weather = None
        if better and roll < better_chance and better in possible_transitions:
            new_weather = better
        elif worse and roll > (1 - worse_chance) and worse in possible_transitions:
            new_weather = worse
            
        if new_weather:
            self.current_weather = new_weather
            return new_weather
            
        return None
