"""Prompt manager for formatting AI interactions."""
from typing import Dict, Any, Tuple, List
from dataclasses import dataclass

from .templates import dialogue, action


class PromptValidationError(Exception):
    """Raised when prompt data validation fails."""
    pass


@dataclass
class RequiredField:
    name: str
    field_type: type
    min_length: int = 0  # For strings and lists

class PromptManager:
    """Handles prompt formatting for AI interactions."""
    
    # Required fields for NPC data
    NPC_REQUIRED_FIELDS = [
        RequiredField("name", str, 1),
        RequiredField("personality_traits", list, 1),
        RequiredField("location", str, 1),
        RequiredField("relationship_with_kuro", str, 1)
    ]
    
    # Required fields for context data
    CONTEXT_REQUIRED_FIELDS = [
        RequiredField("recent_events", list),
        RequiredField("current_topic", str, 1),
        RequiredField("emotional_state", str, 1)
    ]
    
    @staticmethod
    def _validate_fields(data: Dict[str, Any], required_fields: List[RequiredField], context: str) -> None:
        """Validate required fields in the data.
        
        Args:
            data: Dictionary containing the data to validate
            required_fields: List of RequiredField objects defining validation rules
            context: Context string for error messages
            
        Raises:
            PromptValidationError: If validation fails
        """
        for field in required_fields:
            # Check if field exists
            if field.name not in data:
                raise PromptValidationError(f"{context}: Missing required field '{field.name}'")
            
            value = data[field.name]
            
            # Check type
            if not isinstance(value, field.field_type):
                raise PromptValidationError(
                    f"{context}: Field '{field.name}' must be of type {field.field_type.__name__}"
                )
            
            # Check minimum length for strings and lists
            if field.min_length > 0 and hasattr(value, "__len__"):
                if len(value) < field.min_length:
                    raise PromptValidationError(
                        f"{context}: Field '{field.name}' must have at least {field.min_length} items"
                    )
    
    @staticmethod
    def format_dialogue(
        npc_data: Dict[str, Any],
        context: Dict[str, Any],
        input_text: str
    ) -> Tuple[str, str]:
        """Format system and user prompts for NPC dialogue with validation.
        
        Args:
            npc_data: NPC information (name, traits, location, relationship)
            context: Current interaction context (events, topic, emotion)
            input_text: User's input to respond to
            
        Returns:
            Tuple of (system_prompt, user_prompt)
            
        Raises:
            PromptValidationError: If required fields are missing or invalid
        """
        if not input_text:
            raise PromptValidationError("Input text cannot be empty")
            
        PromptManager._validate_fields(npc_data, PromptManager.NPC_REQUIRED_FIELDS, "NPC Data")
        PromptManager._validate_fields(context, PromptManager.CONTEXT_REQUIRED_FIELDS, "Context")
        system_prompt = dialogue.SYSTEM.format(
            character_name=npc_data["name"],
            personality_traits=", ".join(npc_data["personality_traits"]),
            location=npc_data["location"],
            relationship=npc_data["relationship_with_kuro"]
        )
        
        user_prompt = dialogue.USER.format(
            recent_events=", ".join(context["recent_events"]),
            topic=context["current_topic"],
            emotional_state=context["emotional_state"],
            memory_context=context.get("memory_context", "None"),
            input_text=input_text
        )
        
        return system_prompt, user_prompt
    
    @staticmethod
    def format_action_decision(context: Dict[str, Any]) -> str:
        return action.DECISION.format(**context)