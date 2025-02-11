"""
LLM Manager for handling AI model interactions.
"""
import os
import logging
from typing import Optional, Dict, Any
from ..models.location import LocationType
import httpx
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), '.env'))
logger = logging.getLogger(__name__)

class LLMManager:
    def __init__(self):
        """Initialize LLM Manager."""
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
            
        # Initialize httpx client for API calls
        self._client = httpx.AsyncClient(
            timeout=30.0,
            headers={"Authorization": f"Bearer {self.api_key}"}
        )
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._client.aclose()
        
    async def decide_intent(self, agent_name: str, personality: Dict[str, str], memories: list) -> Dict[str, str]:
        """Generate the next intent for an agent based on their personality and memories.
        
        Args:
            agent_name: Name of the agent
            personality: Dict containing role, traits, and goals
            memories: List of recent relevant memories
            
        Returns:
            Dict containing intent data with keys:
            - type: IntentType (e.g., MOVE, INTERACT)
            - target: Optional target for interaction
            - location: Optional location to move to
            - context: Additional context for the intent
        """
        # Format memories for prompt
        memory_text = "\n".join([f"- {m.type}: {m.content}" for m in memories]) if memories else "No recent memories."
        
        # Build prompt
        prompt = f"""As {agent_name}, an {personality['role']} who is {', '.join(personality['traits'])}, 
        with goals to {', '.join(personality['goals'])}, what would you do next?
        
        Recent memories:
        {memory_text}
        
        Respond in JSON format with:
        - type: EXPLORE or INTERACT
        - target: name of NPC to interact with (if INTERACT)
        - location: place to move to (if MOVE)
        - context: reason for this decision"""
        
        # Get LLM response
        response = await self.generate_text(
            prompt=prompt,
            system_prompt="You are an AI deciding the next action for an autonomous agent in a virtual world. Respond only with the requested JSON format.",
            temperature=0.8
        )
        
        # Parse and validate response
        if not response:
            logger.error("No response from LLM, using default intent")
            return {
                "type": "EXPLORE",
                "target": None,
                "location": LocationType.TOWN_SQUARE.name,
                "context": {"reason": "Returning to town square due to LLM error"}
            }
            
        try:
            content = response['choices'][0]['message']['content']
            logger.info(f"\nLLM Response for {agent_name}'s next action:\n{content}\n")
            
            # TODO: Add proper JSON parsing and validation
            # For now return dummy data for testing
            return {
                "type": "EXPLORE",
                "target": None,
                "location": LocationType.MARKET.name,
                "context": {"reason": "Exploring the town"}
            }
            
        except Exception as e:
            logger.error(f"Error parsing LLM response: {e}")
            logger.warning("Error parsing LLM response, using default intent")
            return {
                "type": "EXPLORE",
                "target": None,
                "location": LocationType.TOWN_SQUARE.name,
                "context": {"reason": "Returning to town square due to parsing error"}
            }
    
    async def generate_text(self, 
                          prompt: str,
                          system_prompt: Optional[str] = None,
                          temperature: float = 0.7,
                          max_tokens: int = 500) -> Dict[str, Any]:
        logger.info(f"\nSending prompt to LLM:\n{prompt}\n")
        if system_prompt:
            logger.info(f"System prompt:\n{system_prompt}\n")
        """
        Generate text using the LLM.
        
        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt to set context
            temperature: Controls randomness (0.0 to 1.0)
            max_tokens: Maximum tokens in the response
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = await self._client.post(
                "https://api.openai.com/v1/chat/completions",
                json={
                    "model": "gpt-4",
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens
                }
            )
            response.raise_for_status()
            result = response.json()
            logger.info(f"\n==== Raw LLM Response ====")
            logger.info(f"Model: {result.get('model')}")
            logger.info(f"Response: {result['choices'][0]['message']['content']}")
            logger.info(f"Tokens used: {result.get('usage', {})}")
            logger.info("==== End Response ====\n")
            return result
            
        except Exception as e:
            logger.error(f"Error in LLM call: {str(e)}")
            return None
    
    async def generate_embedding(self, text: str) -> list[float]:
        """
        Generate embedding vector for text.
        
        Args:
            text: Text to generate embedding for
        """
        try:
            response = await self._client.post(
                "https://api.openai.com/v1/embeddings",
                json={
                    "model": "text-embedding-ada-002",
                    "input": text
                }
            )
            response.raise_for_status()
            data = response.json()
            return data["data"][0]["embedding"]
            
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            raise