"""
Core simulation manager for the KuroAI world.

Manages:
- Main simulation loop
- Event processing
- Agent and NPC state
- World state tracking
"""
import logging
import time
from typing import Dict, List, Optional, Set

from ..models.npc import NPCProfile
from ..models.location import LocationType
from ..ai.dialogue_manager import DialogueManager
from ..ai.llm_manager import LLMManager
from ..events.bus import SimulationEventBus
from ..events.models import EventType, SimulationEvent
from .agent import Agent
from ..models.world_state import WorldState

logger = logging.getLogger(__name__)


class SimulationManager:
    """Manages the overall simulation state and progression."""
    
    def __init__(
        self,
        dialogue_manager: DialogueManager,
        llm_manager: LLMManager
    ) -> None:
        """Initialize the simulation manager."""
        # Core components
        self.dialogue_manager = dialogue_manager
        self.llm_manager = llm_manager
        self.event_bus = SimulationEventBus()
        
        # Initialize or load world state
        self.world_state = None
        self.simulation_id = str(int(time.time()))
        
        # World state will be loaded in start() method
        # If no existing state is found, a new one will be created
        
        # State tracking
        self.locations: Dict[LocationType, Set[str]] = {
            loc_type: set() for loc_type in LocationType
        }
        self.npcs: Dict[str, NPCProfile] = {}
        self.agent: Optional[Agent] = None
        
        # Simulation state
        self.is_running = False
        self.tick_count = 0
        
        # Set up event handlers
        self._setup_event_handlers()
    
    def initialize_agent(
        self,
        agent_id: str,
        name: str,
        personality: Dict[str, str],
        start_location: LocationType
    ) -> None:
        """Initialize the main agent (Kuro)."""
        self.agent = Agent(
            agent_id=agent_id,
            name=name,
            personality=personality,
            llm_manager=self.llm_manager,
            event_bus=self.event_bus,
            location=start_location,
            memory_capacity=100
        )
        self.locations[start_location].add(agent_id)
    
    def add_npc(self, npc: NPCProfile) -> None:
        """Add an NPC to the simulation."""
        self.npcs[npc.name] = npc
        self.locations[npc.location].add(npc.name)
    
    def remove_npc(self, npc_name: str) -> None:
        """Remove an NPC from the simulation."""
        if npc_name in self.npcs:
            npc = self.npcs[npc_name]
            self.locations[npc.location].remove(npc_name)
            del self.npcs[npc_name]
    
    def move_npc(self, npc_name: str, new_location: LocationType) -> bool:
        """Move an NPC to a new location."""
        if npc_name not in self.npcs:
            return False
            
        npc = self.npcs[npc_name]
        
        # Update location tracking
        self.locations[npc.location].remove(npc_name)
        self.locations[new_location].add(npc_name)
        
        # Update NPC location
        npc.location = new_location
        return True
    
    def get_npcs_at_location(self, location: LocationType) -> List[NPCProfile]:
        """Get all NPCs currently at a location."""
        return [
            self.npcs[name]
            for name in self.locations[location]
            if name in self.npcs
        ]
    
    async def tick(self) -> None:
        """Advance simulation by one tick."""
        if not self.is_running or not self.agent:
            return
            
        try:
            # Update world state
            self.world_state.total_ticks += 1
            self.world_state.timestamp = time.time()
            await self.world_state.save()
            
            # Check for weather changes
            if new_weather := await self.world_state.update_weather():
                # Weather changed, emit event
                await self.event_bus.publish(
                    SimulationEvent(
                        type=EventType.WEATHER_CHANGED,
                        agent_id=self.agent.agent_id,
                        timestamp=time.time(),
                        data={
                            "weather": new_weather.name,
                            "description": new_weather.get_description()
                        }
                    )
                )
            
            # Emit tick start
            await self.event_bus.publish(
                SimulationEvent(
                    type=EventType.TICK_STARTED,
                    agent_id=self.agent.agent_id,
                    timestamp=time.time(),
                    data={"tick": self.tick_count}
                )
            )
            
            # Process agent intent
            intent = await self.agent.form_intent()
            if intent:
                # Handle movement
                if intent.location and intent.location != self.agent.location:
                    old_location = self.agent.location
                    # Update location tracking
                    self.locations[old_location].remove(self.agent.agent_id)
                    self.locations[intent.location].add(self.agent.agent_id)
                    self.agent.location = intent.location
                    
                    # Emit movement event
                    await self.event_bus.publish(
                        SimulationEvent.create_move_event(
                            agent_id=self.agent.agent_id,
                            old_location=old_location,
                            new_location=intent.location,
                            timestamp=time.time()
                        )
                    )
                    
                # Handle NPC interaction
                if intent.target and intent.target in self.npcs:
                    npc = self.npcs[intent.target]
                    # Emit interaction start
                    await self.event_bus.publish(
                        SimulationEvent.create_interaction_event(
                            agent_id=self.agent.agent_id,
                            target_id=intent.target,
                            location=self.agent.location,
                            timestamp=time.time(),
                            is_start=True
                        )
                    )
                    
                    # Generate dialogue
                    await self.dialogue_manager.generate_dialogue(
                        speaker=self.agent,
                        listener=npc,
                        location=self.agent.location
                    )
                    
                    # Emit interaction end
                    await self.event_bus.publish(
                        SimulationEvent.create_interaction_event(
                            agent_id=self.agent.agent_id,
                            target_id=intent.target,
                            location=self.agent.location,
                            timestamp=time.time(),
                            is_start=False
                        )
                    )
                
                # Complete the intent
                await self.agent.complete_intent(success=True)
            
            # Emit tick completion
            await self.event_bus.publish(
                SimulationEvent(
                    type=EventType.TICK_COMPLETED,
                    agent_id=self.agent.agent_id,
                    timestamp=time.time(),
                    data={"tick": self.tick_count}
                )
            )
            
            self.tick_count += 1
            
        except Exception as e:
            logger.error(f"Error during tick: {e}")
            # Emit error event
            await self.event_bus.publish(
                SimulationEvent(
                    type=EventType.ERROR_OCCURRED,
                    agent_id=self.agent.agent_id if self.agent else "system",
                    timestamp=time.time(),
                    data={"error": str(e)}
                )
            )
            raise
    
    async def start(self) -> None:
        """Start the simulation."""
        if not self.agent:
            raise ValueError("Cannot start simulation without an agent")
        
        # Try to load existing world state
        try:
            self.world_state = await WorldState.get(f"world_state:{self.simulation_id}")
            logger.info(f"Loaded existing world state with ID {self.simulation_id}")
        except Exception as e:
            # Create new world state if none exists
            logger.info(f"Creating new world state with ID {self.simulation_id}")
            self.world_state = WorldState(
                simulation_id=self.simulation_id,
                timestamp=time.time(),
                started_at=time.time()
            )
            await self.world_state.save()
            
        self.is_running = True
        logger.info("Simulation started")
        
        # Emit simulation start event
        await self.event_bus.publish(
            SimulationEvent(
                type=EventType.SIMULATION_STARTED,
                agent_id=self.agent.agent_id,
                timestamp=time.time(),
                data={}
            )
        )
    
    def stop(self) -> None:
        """Stop the simulation."""
        self.is_running = False
        self.event_bus.stop()
        logger.info("Simulation stopped")
    
    async def reset(self) -> None:
        """Reset the simulation to initial state."""
        self.stop()
        self.tick_count = 0
        
        # Clear locations
        for location in self.locations.values():
            location.clear()
            
        # Reset agent to starting location if exists
        if self.agent:
            start_loc = next(iter(LocationType))  # Default to first location
            self.agent.location = start_loc
            self.locations[start_loc].add(self.agent.agent_id)
            
            # Emit reset event
            await self.event_bus.publish(
                SimulationEvent(
                    type=EventType.SIMULATION_RESET,
                    agent_id=self.agent.agent_id,
                    timestamp=time.time(),
                    data={}
                )
            )
        
        logger.info("Simulation reset")
    
    def _setup_event_handlers(self) -> None:
        """Set up internal event handlers."""
        
        async def handle_error(event: SimulationEvent) -> None:
            """Handle error events."""
            error_msg = event.data.get("error", "Unknown error")
            logger.error(f"Simulation error: {error_msg}")
            self.stop()
            
        async def handle_memory_added(event: SimulationEvent) -> None:
            """Log memory additions."""
            memory_type = event.data.get("memory_type")
            logger.debug(f"Memory added for agent {event.agent_id}: {memory_type}")
        
        # Register handlers
        self.event_bus.subscribe(
            handle_error,
            event_types={EventType.ERROR_OCCURRED}
        )
        
        self.event_bus.subscribe(
            handle_memory_added,
            event_types={EventType.MEMORY_ADDED}
        )
