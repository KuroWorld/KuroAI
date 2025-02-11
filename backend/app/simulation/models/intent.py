"""Intent-related models for agent decision making."""
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, Optional


class IntentType(Enum):
    """Types of intents an agent can form."""
    EXPLORE = auto()      # Discover new locations/info
    INTERACT = auto()     # Talk to NPCs
    LEARN = auto()        # Learn specific information
    INVESTIGATE = auto()  # Look into mysteries/events


class IntentStatus(Enum):
    """Possible states of an intent."""
    FORMING = auto()    # Being decided by LLM
    ACTIVE = auto()     # Currently executing
    COMPLETED = auto()  # Successfully finished
    FAILED = auto()     # Failed to complete


@dataclass(frozen=True)
class Intent:
    """Represents an agent's formed intent."""
    agent_id: str
    type: IntentType
    target: Optional[str] = None
    location: Optional[str] = None
    status: IntentStatus = IntentStatus.FORMING
    context: Dict[str, str] = field(default_factory=dict)
