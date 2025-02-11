"""Core agent implementation for autonomous decision making."""
import time
from typing import Dict, List, Optional
from dataclasses import dataclass

from ..models.intent import Intent, IntentStatus, IntentType
from ..models.location import LocationType
from ..ai.llm_manager import LLMManager
from ..events.bus import SimulationEventBus
from ..events.models import EventType, SimulationEvent


@dataclass
class Memory:
    """Represents a single memory entry for an agent."""
    type: str
    content: Dict[str, str]
    timestamp: float
    importance: float = 1.0


class Agent:
    """Autonomous agent capable of forming intents and making decisions."""

    def __init__(
        self,
        agent_id: str,
        name: str,
        personality: Dict[str, str],
        llm_manager: LLMManager,
        event_bus: SimulationEventBus,
        location: LocationType,
        memory_capacity: int = 100
    ) -> None:
        self.agent_id = agent_id
        self.name = name
        self.personality = personality
        self.llm_manager = llm_manager
        self.event_bus = event_bus
        self.location = location
        self._current_intent: Optional[Intent] = None
        self._memory: List[Memory] = []
        self._memory_capacity = memory_capacity

    @property
    def current_intent(self) -> Optional[Intent]:
        """Current active intent if any."""
        return self._current_intent

    async def form_intent(self) -> Optional[Intent]:
        """Form a new intent using LLM if no active intent exists."""
        if self._current_intent and self._current_intent.status == IntentStatus.ACTIVE:
            return self._current_intent

        intent_data = await self.llm_manager.decide_intent(
            agent_name=self.name,
            personality=self.personality,
            memories=self._get_relevant_memories()
        )

        self._current_intent = Intent(
            agent_id=self.agent_id,
            type=IntentType[intent_data["type"].upper()],
            target=intent_data.get("target"),
            location=LocationType[intent_data["location"]] if intent_data.get("location") else None,
            status=IntentStatus.ACTIVE,
            context=intent_data.get("context", {})
        )
        
        # Emit intent formed event
        await self.event_bus.publish(
            SimulationEvent.create_intent_event(
                agent_id=self.agent_id,
                intent_type=self._current_intent.type.name,
                timestamp=time.time(),
                target=self._current_intent.target,
                location=self._current_intent.location
            )
        )
        
        return self._current_intent

    async def complete_intent(self, success: bool = True) -> None:
        """Mark current intent as completed or failed and store in memory."""
        if not self._current_intent:
            return

        status = IntentStatus.COMPLETED if success else IntentStatus.FAILED
        timestamp = time.time()
        
        # Store in memory
        await self._add_memory(
            type="intent",
            content={
                "type": self._current_intent.type.name,
                "target": self._current_intent.target or "",
                "location": self._current_intent.location.name if self._current_intent.location else "",
                "status": status.name,
            },
            timestamp=timestamp
        )
        
        # Emit completion event
        await self.event_bus.publish(
            SimulationEvent(
                type=EventType.AGENT_INTENT_COMPLETED,
                agent_id=self.agent_id,
                timestamp=timestamp,
                data={
                    "intent_type": self._current_intent.type.name,
                    "success": success
                }
            )
        )
        
        self._current_intent = None

    async def _add_memory(
        self,
        type: str,
        content: Dict[str, str],
        timestamp: Optional[float] = None
    ) -> None:
        """Add a new memory, maintaining capacity limits."""
        if timestamp is None:
            timestamp = time.time()
            
        memory = Memory(
            type=type,
            content=content,
            timestamp=timestamp
        )
        
        self._memory.append(memory)
        
        # Emit memory added event
        await self.event_bus.publish(
            SimulationEvent(
                type=EventType.MEMORY_ADDED,
                agent_id=self.agent_id,
                timestamp=timestamp,
                data={
                    "memory_type": type,
                    "content": content
                }
            )
        )

        if len(self._memory) > self._memory_capacity:
            # Remove least important memories when over capacity
            self._memory.sort(key=lambda m: m.importance * m.timestamp)
            self._memory = self._memory[-self._memory_capacity:]

    def _get_relevant_memories(self, limit: int = 10) -> List[Memory]:
        """Get most relevant recent memories for decision making."""
        if not self._memory:
            return []

        # For now, just return most recent memories
        # TODO: Implement better relevance scoring
        sorted_memories = sorted(
            self._memory,
            key=lambda m: m.timestamp * m.importance,
            reverse=True
        )
        return sorted_memories[:limit]
