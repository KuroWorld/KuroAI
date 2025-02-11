"""Event bus implementation for the simulation."""
import asyncio
import logging
from typing import Callable, Dict, List, Set, Optional
from weakref import WeakSet

from .models import EventType, SimulationEvent

# Type alias for event handlers
EventHandler = Callable[[SimulationEvent], None]

logger = logging.getLogger(__name__)


class SimulationEventBus:
    """
    Event bus for the simulation system.
    
    Features:
    - Async event publishing
    - Type-safe event handling
    - Automatic cleanup of dead subscribers
    - Event filtering capabilities
    """
    
    def __init__(self) -> None:
        # Use WeakSet to automatically cleanup dead subscribers
        self._subscribers: Dict[EventType, WeakSet[EventHandler]] = {
            event_type: WeakSet() for event_type in EventType
        }
        self._global_subscribers: WeakSet[EventHandler] = WeakSet()
        
        # Track active subscriptions for debugging
        self._subscription_count: Dict[EventType, int] = {
            event_type: 0 for event_type in EventType
        }
        
        # Event processing
        self._queue: asyncio.Queue[SimulationEvent] = asyncio.Queue()
        self._processing: bool = False
        self._processor_task: Optional[asyncio.Task] = None
    
    def subscribe(
        self,
        handler: EventHandler,
        event_types: Optional[Set[EventType]] = None
    ) -> None:
        """
        Subscribe to specific event types or all events if types not specified.
        
        Args:
            handler: Async function to handle events
            event_types: Set of event types to subscribe to, or None for all
        """
        if event_types is None:
            self._global_subscribers.add(handler)
            logger.debug(f"Added global subscriber {handler.__name__}")
            return
            
        for event_type in event_types:
            self._subscribers[event_type].add(handler)
            self._subscription_count[event_type] += 1
            logger.debug(
                f"Added subscriber {handler.__name__} for {event_type.name}"
            )
    
    def unsubscribe(
        self,
        handler: EventHandler,
        event_types: Optional[Set[EventType]] = None
    ) -> None:
        """
        Unsubscribe from specific event types or all events.
        
        Args:
            handler: Previously subscribed handler
            event_types: Set of event types to unsubscribe from, or None for all
        """
        if event_types is None:
            self._global_subscribers.discard(handler)
            logger.debug(f"Removed global subscriber {handler.__name__}")
            return
            
        for event_type in event_types:
            self._subscribers[event_type].discard(handler)
            self._subscription_count[event_type] -= 1
            logger.debug(
                f"Removed subscriber {handler.__name__} from {event_type.name}"
            )
    
    async def publish(self, event: SimulationEvent) -> None:
        """
        Publish an event to all relevant subscribers.
        
        Args:
            event: The event to publish
        """
        await self._queue.put(event)
        
        # Start processor if not running
        if not self._processing:
            self._start_processor()
    
    def _start_processor(self) -> None:
        """Start the event processor task."""
        if self._processor_task is None or self._processor_task.done():
            self._processing = True
            self._processor_task = asyncio.create_task(self._process_events())
            logger.debug("Started event processor")
    
    async def _process_events(self) -> None:
        """Process events from the queue."""
        try:
            while self._processing:
                # Get next event
                event = await self._queue.get()
                
                # Process event
                await self._handle_event(event)
                
                # Mark as done
                self._queue.task_done()
                
                # Stop if queue empty
                if self._queue.empty():
                    self._processing = False
                    
        except Exception as e:
            logger.error(f"Error processing events: {e}")
            self._processing = False
        finally:
            logger.debug("Stopped event processor")
    
    async def _handle_event(self, event: SimulationEvent) -> None:
        """
        Handle a single event by dispatching to subscribers.
        
        Args:
            event: Event to handle
        """
        # Get relevant subscribers
        handlers = set(self._subscribers[event.type])
        handlers.update(self._global_subscribers)
        
        # Process with all handlers
        for handler in handlers:
            try:
                await handler(event)
            except Exception as e:
                logger.error(f"Error in event handler {handler.__name__}: {e}")
    
    def stop(self) -> None:
        """Stop the event processor."""
        self._processing = False
        if self._processor_task:
            self._processor_task.cancel()
            logger.debug("Cancelled event processor")
