"""Main FastAPI application module."""
import asyncio
import logging
import os
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Optional

from app.simulation.core.redis import init_redis, close_redis

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

from app.simulation.core.simulation_manager import SimulationManager
from app.simulation.ai.dialogue_manager import DialogueManager
from app.simulation.ai.llm_manager import LLMManager
from app.simulation.models.location import LocationType

app = FastAPI(title="KuroAI", description="KuroAI Simulation Backend")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global simulation manager instance
sim_manager: Optional[SimulationManager] = None

async def run_simulation_tick():
    """Background task to run simulation ticks."""
    while True:
        if sim_manager and sim_manager.is_running:
            try:
                await sim_manager.tick()
            except Exception as e:
                logger.error(f"Error in simulation tick: {e}")
        await asyncio.sleep(15)  # Tick every 15 seconds

@app.on_event("startup")
async def startup_event():
    """Initialize core components on startup."""
    global sim_manager
    
    # Initialize Redis
    try:
        redis_host = os.getenv("REDIS_HOST", "redis")
        redis_port = int(os.getenv("REDIS_PORT", "6379"))
        await init_redis(host=redis_host, port=redis_port)
        logger.info(f"Connected to Redis at {redis_host}:{redis_port}")
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {e}")
        raise
    
    # Initialize core components
    llm_manager = LLMManager()
    dialogue_manager = DialogueManager(llm_manager)
    sim_manager = SimulationManager(dialogue_manager, llm_manager)
    
    # Initialize Kuro (the main agent)
    sim_manager.initialize_agent(
        agent_id="kuro",
        name="Kuro",
        personality={
            "role": "Adventurer",
            "traits": ["curious", "friendly", "determined"],
            "goals": ["explore the world", "help others", "learn new things"]
        },
        start_location=LocationType.TOWN_SQUARE
    )
    
    # Start background task for simulation ticks
    asyncio.create_task(run_simulation_tick())

# Dependency to get simulation manager
async def get_sim_manager():
    """Dependency to get simulation manager."""
    if sim_manager is None:
        raise HTTPException(status_code=503, detail="Simulation manager not initialized")
    return sim_manager

# Import and include routers
from app.api.routes import router

app.include_router(
    router,
    prefix="/api",
    tags=["simulation"],
    dependencies=[Depends(get_sim_manager)]
)

@app.on_event("startup")
async def startup_event():
    """Start the simulation when the app starts."""
    await sim_manager.start()

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown."""
    # Stop simulation
    if sim_manager:
        sim_manager.stop()
    
    # Close Redis connection
    try:
        await close_redis()
        logger.info("Closed Redis connection")
    except Exception as e:
        logger.error(f"Error closing Redis connection: {e}")
