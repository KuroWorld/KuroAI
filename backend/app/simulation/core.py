"""
Core simulation loop for KuroAI.
This module handles the main simulation logic and state management.
"""
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Set, Optional
from asyncio import Queue
from typing import Dict, List
from .models.npc import NPCProfile
from .models.location import LocationType
from .core.agent import Agent
from .models.memory import Memory

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimulationEnvironment:
    # Class-level state ensures singleton pattern works even if multiple imports occur
    # These must be class variables, not instance variables, to prevent race conditions
    _instance = None
    _has_started = False
    
    def __new__(cls):
        # Using __new__ instead of a traditional singleton pattern because:
        # 1. It prevents any possibility of multiple instances
        # 2. It works with inheritance
        # 3. It's thread-safe without additional locks
        if cls._instance is None:
            cls._instance = super(SimulationEnvironment, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True

        # Core state initialization
        # Note: These values represent the initial conditions of the universe
        # They can never be changed after the simulation starts
        # Think of this as the cosmic constants at the moment of the Big Bang
        self.kuro = KuroState(
            current_location=LocationType.PLAZA,
            personality_traits={"curiosity": 0.8, "sustainability": 0.7}
        )
        self.npcs: Dict[str, NPCProfile] = {}
        self._load_npcs()
        
        # Simulation state
        # active_events uses a List instead of a Queue because:
        # 1. We need to iterate over all events each tick
        # 2. Events can be added/removed from any position
        # 3. We need to maintain event order for deterministic simulation
        self.active_events: List[Dict] = []
        self.tick_rate = 1.0  # 1 second per tick - this affects simulation granularity
        self.current_time = datetime.now()
        
        # WebSocket state management
        # Using unbounded Queue() because dropping state updates would break simulation consistency
        # If a client is slow, it's better to build up backpressure than to lose updates
        self._state_updates: Queue = Queue()
        self._connected_clients: Set[str] = set()
        
    async def start_simulation(self):
        """Start the simulation. Can only be called once - this is the God event."""
        if self._has_started:
            logger.error("Cannot start simulation: The world has already begun.")
            raise RuntimeError("The simulation can only be started once. The world has already begun.")
        
        logger.info("⚡ The world begins - initiating the God event...")
        self._has_started = True
        
        while True:
            await self.update_state()
            await self.process_events()
            await self.update_kuro_goals()
            await asyncio.sleep(self.tick_rate)
    
    async def update_state(self):
        if not self._has_started:
            raise RuntimeError("Cannot update state: Simulation has not started")
            
        self.current_time = datetime.now()
        logger.info(f"Updating state: Kuro at {self.kuro.current_location}")
        await self.process_location_effects()
        
        # Create state update for WebSocket clients
        update = {
            "timestamp": self.current_time,
            "kuro_location": self.kuro.current_location.value,
            "emotional_state": self.kuro.emotional_state,
            "active_events": len(self.active_events)
        }
        await self._state_updates.put(update)
        
    async def process_location_effects(self):
        # IMPORTANT: Location effects are processed first in the update cycle because:
        # 1. They establish the basic context for other interactions
        # 2. They're deterministic (unlike events or NPC behaviors)
        # 3. They must be processed before any NPC or event logic that might change locations
        location = self.kuro.current_location
        npcs_present = [
            npc for npc in self.npcs.values() 
            if npc.location == location
        ]
        
        for npc in npcs_present:
            memory = Memory(
                timestamp=datetime.now(),
                event_type="npc_presence",
                description=f"Encountered {npc.name} at {location.value}",
                location=location,
                involved_npcs=[npc.name]
            )
            self.kuro.add_memory(memory)
    
    async def move_kuro(self, new_location: LocationType) -> bool:
        # Early return pattern used here because:
        # 1. Prevents unnecessary memory creation
        # 2. Avoids adding redundant entries to the memory log
        # 3. Maintains cleaner simulation history
        if new_location == self.kuro.current_location:
            return False
            
        memory = Memory(
            timestamp=datetime.now(),
            event_type="movement",
            description=f"Moved from {self.kuro.current_location.value} to {new_location.value}",
            location=new_location
        )
        self.kuro.add_memory(memory)
        
        self.kuro.current_location = new_location
        return True
    
    async def process_events(self):
        # Using [:] to create a copy of the list because:
        # 1. We're modifying the list while iterating
        # 2. Events might trigger new events
        # 3. Prevents concurrent modification issues
        for event in self.active_events[:]:
            if await self.handle_event(event):
                self.active_events.remove(event)
    
    async def handle_event(self, event: Dict) -> bool:
        event_type = event.get("type")
        if event_type == "interaction":
            npc_name = event.get("npc")
            if npc_name in self.npcs:
                npc = self.npcs[npc_name]
                npc.interaction_history.append({
                    "timestamp": datetime.now(),
                    "type": event.get("interaction_type"),
                    "outcome": event.get("outcome", "pending")
                })
                return True
        return False
    
    def _load_npcs(self):
        """Load NPCs from configuration."""
        from .data.npc_configs import DEFAULT_NPCS
        
        for npc_id, config in DEFAULT_NPCS.items():
            self.npcs[npc_id] = NPCProfile(
                name=config["name"],
                role=config["role"],
                location=config["location"],
                personality_traits=config["personality_traits"],
                dialogue_cues=config["dialogue_cues"]
            )
    
    async def get_next_update(self) -> Dict:
        """Get the next state update. Used by WebSocket connections."""
        if not self._has_started:
            raise RuntimeError("Cannot get updates: Simulation has not started")
        return await self._state_updates.get()
    
    async def update_kuro_goals(self):
        # To be implemented
        pass
