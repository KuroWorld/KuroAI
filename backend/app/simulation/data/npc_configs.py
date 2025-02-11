"""
NPC configuration data for the simulation.
"""
from typing import Dict, Any
from ..models.location import LocationType

DEFAULT_NPCS: Dict[str, Dict[str, Any]] = {
    "theo": {
        "name": "Theo",
        "role": "Eccentric Artist",
        "location": LocationType.WORKSHOP,
        "personality_traits": {
            "creativity": 0.9,
            "wisdom": 0.7
        },
        "dialogue_cues": ["art_inspiration", "community_projects"]
    },
    "sarah": {
        "name": "Sarah",
        "role": "Coffee Shop Owner",
        "location": LocationType.COFFEE_SHOP,
        "personality_traits": {
            "hospitality": 0.8,
            "empathy": 0.9
        },
        "dialogue_cues": ["local_community", "coffee_culture"]
    },
    "professor_chen": {
        "name": "Professor Chen",
        "role": "Retired Scholar",
        "location": LocationType.LIBRARY,
        "personality_traits": {
            "knowledge": 0.95,
            "patience": 0.8
        },
        "dialogue_cues": ["philosophy", "local_history"]
    }
}
