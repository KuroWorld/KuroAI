"""
Dialogue manager for handling NPC conversations using LLM.

This module is responsible for:
1. Handling dialogue generation using LLM
2. Maintaining conversation history
3. Managing dialogue context
"""
from typing import Dict, Optional, List, Tuple
from datetime import datetime
from dataclasses import dataclass

from ..models.npc import NPCProfile
from ..models.location import LocationType
from .llm_manager import LLMManager
from .prompts import PromptManager


@dataclass
class DialogueContext:
    """Represents the context for a dialogue interaction."""
    recent_events: List[str]
    current_topic: str
    emotional_state: str
    memory_context: Optional[str] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        """Set default timestamp if not provided."""
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class DialogueHistory:
    """Maintains a record of dialogue interactions."""
    speaker_name: str
    messages: List[Dict[str, str]]  # List of {role: content} messages
    context: DialogueContext
    started_at: datetime
    last_updated: datetime
    
    def add_message(self, role: str, content: str) -> None:
        """Add a new message to the history."""
        self.messages.append({"role": role, "content": content})
        self.last_updated = datetime.now()


class DialogueManager:
    """Manages NPC dialogue interactions."""

    def __init__(self, llm_manager: LLMManager):
        """
        Initialize the dialogue manager.

        Args:
            llm_manager: Instance of LLMManager for generating responses
        """
        self.llm_manager = llm_manager
        self._dialogue_histories: Dict[str, List[DialogueHistory]] = {}

    def _create_dialogue_context(
        self,
        npc: NPCProfile,
        current_topic: str,
        recent_events: Optional[List[str]] = None,
        memory_context: Optional[str] = None
    ) -> DialogueContext:
        """
        Create dialogue context for an interaction.

        Args:
            npc: The NPC profile
            current_topic: Current conversation topic
            recent_events: List of recent events (optional)
            memory_context: Relevant memory context (optional)

        Returns:
            DialogueContext: Created context object
        """
        if recent_events is None:
            recent_events = []  # Could be fetched from event system in the future

        return DialogueContext(
            recent_events=recent_events,
            current_topic=current_topic,
            emotional_state=npc.emotional_state,
            memory_context=memory_context,
            timestamp=datetime.now()
        )

    async def generate_dialogue(
        self,
        speaker: NPCProfile,
        listener: NPCProfile,
        current_topic: str,
        location: LocationType,
        previous_message: Optional[str] = None,
        recent_events: Optional[List[str]] = None,
        memory_context: Optional[str] = None
    ) -> Tuple[str, DialogueHistory]:
        """
        Generate dialogue between two NPCs.

        Args:
            speaker: The character speaking
            listener: The character being spoken to
            current_topic: Current conversation topic
            location: Current location
            previous_message: Previous message in conversation (optional)
            recent_events: List of recent events (optional)
            memory_context: Relevant memory context (optional)

        Returns:
            Tuple[str, DialogueHistory]: Generated dialogue and conversation history
        """
        # Create dialogue context
        context = self._create_dialogue_context(
            npc=npc,
            current_topic=current_topic,
            recent_events=recent_events,
            memory_context=memory_context
        )
        
        # Format prompts using PromptManager
        system_prompt, conversation_prompt = PromptManager.format_dialogue(
            npc_data={
                "name": speaker.name,
                "personality_traits": speaker.personality_traits,
                "location": location.value,
                "relationship": speaker.get_relationship(listener.name)
            },
            context={
                "recent_events": context.recent_events,
                "current_topic": context.current_topic,
                "emotional_state": speaker.emotional_state,
                "memory_context": context.memory_context,
                "listener": listener.name,
                "previous_message": previous_message
            }
        )
        
        # Generate response using LLM
        response = await self.llm_manager.generate_text(
            prompt=conversation_prompt,
            system_prompt=system_prompt
        )
        
        # Extract response text
        response_text = response["choices"][0]["message"]["content"]
        
        # Create dialogue history
        history = DialogueHistory(
            speaker_name=speaker.name,
            messages=[
                {"role": "previous", "content": previous_message} if previous_message else None,
                {"role": "npc", "content": response_text}
            ],
            context=context,
            started_at=datetime.now(),
            last_updated=datetime.now()
        )
        
        # Store history
        if npc.name not in self._dialogue_histories:
            self._dialogue_histories[npc.name] = []
        self._dialogue_histories[npc.name].append(history)
        
        return response_text, history

    def get_dialogue_history(
        self,
        npc_name: str,
        limit: Optional[int] = None
    ) -> List[DialogueHistory]:
        """
        Retrieve dialogue history for an NPC.

        Args:
            npc_name: Name of the NPC
            limit: Maximum number of history entries to return (optional)

        Returns:
            List[DialogueHistory]: List of dialogue history entries
        """
        histories = self._dialogue_histories.get(npc_name, [])
        if limit:
            return histories[-limit:]
        return histories
