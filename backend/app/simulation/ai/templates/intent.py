"""Intent formation prompt templates."""
from typing import Dict, List

from ...models.intent import IntentType
from ..prompts import BasePrompt
from ...core.agent import Memory


class IntentFormationPrompt(BasePrompt):
    """Generates prompts for intent formation."""

    def generate(
        self,
        agent_name: str,
        personality: Dict[str, str],
        memories: List[Memory]
    ) -> str:
        memory_str = self._format_memories(memories)
        personality_str = self._format_personality(personality)
        valid_intents = [t.name for t in IntentType]

        return f"""You are {agent_name}, with the following traits:
{personality_str}

Your recent experiences:
{memory_str}

What would you like to do next? Consider:
1. Your personality and current state
2. Your recent experiences
3. Your goals and interests

Respond in JSON format:
{{
    "type": one of [{', '.join(valid_intents)}],
    "target": optional target of your intent,
    "location": optional location needed,
    "context": additional context as key-value pairs
}}"""

    def _format_memories(self, memories: List[Memory]) -> str:
        """Format memories into a readable string."""
        if not memories:
            return "No recent memories."

        memory_lines = []
        for memory in memories:
            content = memory.content
            if memory.type == "intent":
                line = (f"- {content['type'].lower()} "
                       f"{'with ' + content['target'] if content['target'] else ''} "
                       f"{'at ' + content['location'] if content['location'] else ''} "
                       f"({content['status'].lower()})")
            else:
                line = f"- {content}"
            memory_lines.append(line)

        return "\n".join(memory_lines)

    def _format_personality(self, personality: Dict[str, str]) -> str:
        """Format personality traits into a readable string."""
        return "\n".join(f"- {k}: {v}" for k, v in personality.items())
