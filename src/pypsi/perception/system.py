"""Perception system for PyPSI - How the agent senses the environment.

This module implements the perception layer that translates raw environment
state into structured percepts that the agent can use for decision-making.

Key features:
- Sensory radius - agent can only perceive nearby tiles
- Resource detection - identify food, water, shelter
- Terrain awareness - understand what kind of ground is nearby
- Simple feature extraction for decision-making
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..environment.island import Island, Percept

from ..environment.island import GridPos, ResourceType, TerrainType


@dataclass
class PerceptionConfig:
    """Configuration for the perception system.
    
    Attributes:
        sensory_radius: How far the agent can see (in grid units)
        can_see_through_forest: Whether forests block vision
        resource_detection_threshold: Minimum resource amount to detect
    """
    sensory_radius: int = 5
    can_see_through_forest: bool = False
    resource_detection_threshold: float = 0.1


class PerceptionSystem:
    """The agent's sensory/perception system.
    
    The perception system translates raw environment state into a structured
    percept that the agent can use for decision-making. It handles:
    
    - Limited sensory radius (agent can't see everything)
    - Resource detection
    - Terrain awareness
    - Movement possibility detection
    
    This is the interface between the environment and the agent's
    cognitive processes.
    """
    
    def __init__(self, config: PerceptionConfig | None = None) -> None:
        """Initialize the perception system.
        
        Args:
            config: Perception configuration (uses defaults if None)
        """
        self.config = config or PerceptionConfig()
    
    def perceive(self, island: Island, agent_position: GridPos) -> Percept:
        """Generate a percept from the agent's current position.
        
        This is the main perception function - it examines the environment
        around the agent and returns a structured percept.
        
        Args:
            island: The island environment
            agent_position: Where the agent is located
            
        Returns:
            A Percept containing what the agent can sense
        """
        from ..environment.island import Direction, Percept, ResourceType
        
        # Get current tile info
        current_tile = island.get_tile(agent_position)
        if current_tile is None:
            raise ValueError(f"Invalid agent position: {agent_position}")
        
        # Detect nearby resources
        nearby_resources = self._detect_resources(island, agent_position)
        
        # Check movement possibilities
        can_move = self._check_movement_possibilities(island, agent_position)
        
        # Create percept
        percept = Percept(
            position=agent_position,
            terrain=current_tile.terrain,
            nearby_resources=nearby_resources,
            can_move_north=can_move[Direction.NORTH],
            can_move_south=can_move[Direction.SOUTH],
            can_move_east=can_move[Direction.EAST],
            can_move_west=can_move[Direction.WEST],
            current_resource=current_tile.resource,
            resource_amount=current_tile.resource_amount,
        )
        
        return percept
    
    def _detect_resources(
        self, 
        island: Island, 
        agent_position: GridPos
    ) -> list[tuple[ResourceType, GridPos, float]]:
        """Detect resources within sensory radius.
        
        Args:
            island: The island environment
            agent_position: Agent's current position
            
        Returns:
            List of (resource_type, position, distance) tuples
        """
        resources = []
        radius = self.config.sensory_radius
        
        # Check all tiles within sensory radius
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                # Skip the agent's own position
                if dx == 0 and dy == 0:
                    continue
                
                # Check if within circular radius
                if dx * dx + dy * dy > radius * radius:
                    continue
                
                pos = GridPos(agent_position.x + dx, agent_position.y + dy)
                tile = island.get_tile(pos)
                
                if tile is None:
                    continue
                
                # Check if forest blocks vision (if enabled)
                if (not self.config.can_see_through_forest and 
                    tile.terrain.name == 'FOREST'):
                    # Still detect but note it's blocked
                    pass
                
                # Check for resources
                if (tile.resource != ResourceType.NONE and 
                    tile.resource_amount >= self.config.resource_detection_threshold):
                    distance = (dx * dx + dy * dy) ** 0.5
                    resources.append((tile.resource, pos, distance))
        
        return resources
    
    def _check_movement_possibilities(
        self, 
        island: Island, 
        agent_position: GridPos
    ) -> dict:
        """Check which directions the agent can move.
        
        Args:
            island: The island environment
            agent_position: Agent's current position
            
        Returns:
            Dictionary mapping Direction to boolean (can move)
        """
        from ..environment.island import Direction
        
        can_move = {}
        for direction in [Direction.NORTH, Direction.SOUTH, Direction.EAST, Direction.WEST]:
            new_pos = agent_position + direction.to_pos()
            can_move[direction] = island.is_valid_position(new_pos)
        
        return can_move
    
    def get_visible_tiles(
        self, 
        island: Island, 
        agent_position: GridPos
    ) -> list[tuple[GridPos, TerrainType]]:
        """Get all terrain types visible to the agent.
        
        Useful for navigation and exploration behavior.
        
        Args:
            island: The island environment
            agent_position: Agent's current position
            
        Returns:
            List of (position, terrain_type) tuples
        """
        visible = []
        radius = self.config.sensory_radius
        
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                if dx * dx + dy * dy > radius * radius:
                    continue
                
                pos = GridPos(agent_position.x + dx, agent_position.y + dy)
                tile = island.get_tile(pos)
                
                if tile is not None:
                    visible.append((pos, tile.terrain))
        
        return visible


@dataclass
class SensoryMemory:
    """Short-term memory for recent percepts.
    
    The agent can remember recent percepts for a short time,
    allowing it to maintain some awareness even when things
    move out of immediate sensory range.
    
    Attributes:
        max_memory_size: How many percepts to remember
        memory_decay_time: How long percepts remain valid (in seconds)
        memories: List of recent percepts with timestamps
    """
    max_memory_size: int = 10
    memory_decay_time: float = 30.0  # seconds
    memories: list[tuple[float, Percept]] = field(default_factory=list)
    
    def add_percept(self, percept: Percept, timestamp: float) -> None:
        """Add a percept to sensory memory.
        
        Args:
            percept: The percept to remember
            timestamp: Current time (for decay calculations)
        """
        self.memories.append((timestamp, percept))
        
        # Trim to max size
        if len(self.memories) > self.max_memory_size:
            self.memories = self.memories[-self.max_memory_size:]
    
    def get_recent_percepts(self, current_time: float) -> list[Percept]:
        """Get percepts that haven't decayed yet.
        
        Args:
            current_time: Current timestamp
            
        Returns:
            List of still-valid percepts
        """
        valid = []
        for timestamp, percept in self.memories:
            if current_time - timestamp < self.memory_decay_time:
                valid.append(percept)
        return valid
    
    def clear_old_memories(self, current_time: float) -> None:
        """Remove percepts that have decayed.
        
        Args:
            current_time: Current timestamp
        """
        self.memories = [
            (t, p) for t, p in self.memories 
            if current_time - t < self.memory_decay_time
        ]
    
    def find_last_seen_resource(
        self, 
        resource_type: ResourceType,
        current_time: float
    ) -> GridPos | None:
        """Find where a resource was last seen.
        
        Searches through sensory memory for the most recent
        sighting of a specific resource type.
        
        Args:
            resource_type: Type of resource to find
            current_time: Current timestamp
            
        Returns:
            Position where resource was seen, or None
        """
        # Search in reverse chronological order
        for timestamp, percept in reversed(self.memories):
            if current_time - timestamp >= self.memory_decay_time:
                continue
            
            for res_type, pos, dist in percept.nearby_resources:
                if res_type == resource_type:
                    return pos
            
            # Also check current position
            if percept.current_resource == resource_type:
                return percept.position
        
        return None


def create_default_perception_system() -> PerceptionSystem:
    """Create a perception system with default settings."""
    return PerceptionSystem(PerceptionConfig())
