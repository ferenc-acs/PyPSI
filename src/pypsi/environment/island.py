"""Environment module for PyPSI - Simple grid-based island world.

This module implements a simple 2D grid environment where the PSI agent
can move around, find food, water, and rest areas. The environment is
inspired by the original PSI experiments with artificial islands.

Key features:
- Grid-based terrain with different tile types
- Resources that can be consumed (food, water)
- Spatial navigation for the agent
- Real-time updates for continuous simulation
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Generator


class TerrainType(Enum):
    """Types of terrain tiles in the environment."""
    WATER = auto()      #: Deep water - impassable
    SHALLOW = auto()    #: Shallow water - slow movement
    SAND = auto()       #: Beach/sand - normal movement
    GRASS = auto()      #: Grassland - normal movement, may have food
    FOREST = auto()     #: Forest - may have food, harder navigation
    MOUNTAIN = auto()   #: Mountains - impassable or slow


class ResourceType(Enum):
    """Types of resources that can exist in the environment."""
    FOOD = auto()       #: Edible food - satisfies hunger
    WATER = auto()      #: Drinkable water - satisfies thirst
    SHELTER = auto()    #: Rest spot - satisfies energy
    NONE = auto()       #: No resource


@dataclass
class Tile:
    """A single tile in the grid environment.
    
    Attributes:
        x: Grid x-coordinate
        y: Grid y-coordinate
        terrain: Type of terrain
        resource: Type of resource present (if any)
        resource_amount: How much resource is available (0-1)
        occupied_by: ID of agent occupying this tile (if any)
    """
    x: int
    y: int
    terrain: TerrainType = TerrainType.GRASS
    resource: ResourceType = ResourceType.NONE
    resource_amount: float = 0.0
    occupied_by: str | None = None
    
    def is_passable(self) -> bool:
        """Check if this tile can be traversed."""
        return self.terrain not in (TerrainType.WATER, TerrainType.MOUNTAIN)
    
    def has_resource(self) -> bool:
        """Check if this tile has an available resource."""
        return self.resource != ResourceType.NONE and self.resource_amount > 0
    
    def consume_resource(self, amount: float = 0.3) -> float:
        """Consume some of the resource on this tile.
        
        Returns:
            Amount actually consumed (may be less than requested if depleted)
        """
        if not self.has_resource():
            return 0.0
        consumed = min(self.resource_amount, amount)
        self.resource_amount -= consumed
        if self.resource_amount <= 0:
            self.resource = ResourceType.NONE
        return consumed
    
    def get_movement_cost(self) -> float:
        """Get the movement cost for traversing this tile."""
        costs = {
            TerrainType.WATER: float('inf'),
            TerrainType.SHALLOW: 2.0,
            TerrainType.SAND: 1.0,
            TerrainType.GRASS: 1.0,
            TerrainType.FOREST: 1.5,
            TerrainType.MOUNTAIN: float('inf'),
        }
        return costs.get(self.terrain, 1.0)


@dataclass
class GridPos:
    """Grid position coordinates."""
    x: int
    y: int
    
    def __add__(self, other: GridPos) -> GridPos:
        """Add two positions (vector addition)."""
        return GridPos(self.x + other.x, self.y + other.y)
    
    def distance_to(self, other: GridPos) -> float:
        """Calculate Euclidean distance to another position."""
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5
    
    def manhattan_distance(self, other: GridPos) -> int:
        """Calculate Manhattan distance to another position."""
        return abs(self.x - other.x) + abs(self.y - other.y)


class Direction(Enum):
    """Cardinal and diagonal directions for movement."""
    NORTH = (0, -1)
    NORTHEAST = (1, -1)
    EAST = (1, 0)
    SOUTHEAST = (1, 1)
    SOUTH = (0, 1)
    SOUTHWEST = (-1, 1)
    WEST = (-1, 0)
    NORTHWEST = (-1, -1)
    
    def __init__(self, dx: int, dy: int) -> None:
        self.dx = dx
        self.dy = dy
    
    def to_pos(self) -> GridPos:
        """Convert direction to position delta."""
        return GridPos(self.dx, self.dy)


@dataclass
class Island:
    """A grid-based island environment.
    
    The island consists of a grid of tiles with different terrain types.
    It's surrounded by water and has various resources scattered throughout.
    
    Attributes:
        width: Width of the grid
        height: Height of the grid
        tiles: 2D grid of tiles
    """
    width: int = 40
    height: int = 30
    tiles: list[list[Tile]] = field(default_factory=list)
    
    def __post_init__(self) -> None:
        """Initialize the grid if not provided."""
        if not self.tiles:
            self._generate_island()
    
    def _generate_island(self) -> None:
        """Generate a simple island with terrain and resources."""
        center_x = self.width // 2
        center_y = self.height // 2
        
        self.tiles = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                # Calculate distance from center
                dist_from_center = ((x - center_x) ** 2 + (y - center_y) ** 2) ** 0.5
                max_radius = min(self.width, self.height) * 0.45
                
                # Determine terrain based on distance from center
                if dist_from_center > max_radius:
                    terrain = TerrainType.WATER
                elif dist_from_center > max_radius * 0.9:
                    terrain = TerrainType.SHALLOW
                elif dist_from_center > max_radius * 0.75:
                    terrain = TerrainType.SAND
                elif dist_from_center > max_radius * 0.4:
                    terrain = TerrainType.GRASS
                else:
                    terrain = TerrainType.FOREST
                
                tile = Tile(x=x, y=y, terrain=terrain)
                
                # Add resources randomly
                if terrain == TerrainType.GRASS and self._should_place_resource(x, y, 0.05):
                    tile.resource = ResourceType.FOOD
                    tile.resource_amount = 1.0
                elif terrain == TerrainType.SAND and self._should_place_resource(x, y, 0.1):
                    tile.resource = ResourceType.SHELTER
                    tile.resource_amount = 1.0
                
                row.append(tile)
            self.tiles.append(row)
        
        # Add water sources (lakes/ponds)
        self._add_water_sources()
    
    def _should_place_resource(self, x: int, y: int, probability: float) -> bool:
        """Determine if a resource should be placed at this position.
        
        Uses a simple hash-based pseudo-random function for determinism.
        """
        import hashlib
        hash_input = f"{x}:{y}:resource"
        hash_val = int(hashlib.md5(hash_input.encode()).hexdigest(), 16)
        return (hash_val % 10000) / 10000 < probability
    
    def _add_water_sources(self) -> None:
        """Add some fresh water sources on the island."""
        import hashlib
        center_x = self.width // 2
        center_y = self.height // 2
        
        for y in range(self.height):
            for x in range(self.width):
                tile = self.tiles[y][x]
                if tile.terrain in (TerrainType.GRASS, TerrainType.FOREST):
                    hash_input = f"{x}:{y}:water"
                    hash_val = int(hashlib.md5(hash_input.encode()).hexdigest(), 16)
                    if (hash_val % 10000) / 10000 < 0.02:  # 2% chance
                        tile.resource = ResourceType.WATER
                        tile.resource_amount = 1.0
    
    def get_tile(self, pos: GridPos) -> Tile | None:
        """Get the tile at a position, or None if out of bounds."""
        if 0 <= pos.x < self.width and 0 <= pos.y < self.height:
            return self.tiles[pos.y][pos.x]
        return None
    
    def is_valid_position(self, pos: GridPos) -> bool:
        """Check if a position is within bounds and passable."""
        tile = self.get_tile(pos)
        return tile is not None and tile.is_passable() and tile.occupied_by is None
    
    def get_neighbors(self, pos: GridPos, diagonal: bool = False) -> list[tuple[GridPos, Direction]]:
        """Get neighboring positions.
        
        Args:
            pos: Center position
            diagonal: Whether to include diagonal neighbors
            
        Returns:
            List of (position, direction) tuples
        """
        directions = list(Direction) if diagonal else [
            Direction.NORTH, Direction.EAST, Direction.SOUTH, Direction.WEST
        ]
        
        neighbors = []
        for direction in directions:
            new_pos = pos + direction.to_pos()
            tile = self.get_tile(new_pos)
            if tile is not None and tile.is_passable():
                neighbors.append((new_pos, direction))
        
        return neighbors
    
    def find_resource(self, start: GridPos, resource_type: ResourceType, 
                      max_distance: int = 20) -> GridPos | None:
        """Find the nearest tile with a specific resource.
        
        Uses BFS to find the closest resource.
        
        Returns:
            Position of nearest resource, or None if not found
        """
        from collections import deque
        
        visited = {start}
        queue = deque([(start, 0)])
        
        while queue:
            pos, dist = queue.popleft()
            tile = self.get_tile(pos)
            
            if tile and tile.resource == resource_type and tile.resource_amount > 0:
                return pos
            
            if dist < max_distance:
                for neighbor_pos, _ in self.get_neighbors(pos, diagonal=False):
                    if neighbor_pos not in visited:
                        visited.add(neighbor_pos)
                        queue.append((neighbor_pos, dist + 1))
        
        return None
    
    def get_tiles_with_resource(self, resource_type: ResourceType) -> list[Tile]:
        """Get all tiles that have a specific resource."""
        tiles = []
        for row in self.tiles:
            for tile in row:
                if tile.resource == resource_type and tile.resource_amount > 0:
                    tiles.append(tile)
        return tiles
    
    def occupy_tile(self, pos: GridPos, agent_id: str) -> bool:
        """Mark a tile as occupied by an agent.
        
        Returns:
            True if successfully occupied, False otherwise
        """
        tile = self.get_tile(pos)
        if tile and tile.occupied_by is None and tile.is_passable():
            tile.occupied_by = agent_id
            return True
        return False
    
    def vacate_tile(self, pos: GridPos) -> None:
        """Remove occupation from a tile."""
        tile = self.get_tile(pos)
        if tile:
            tile.occupied_by = None
    
    def move_agent(self, from_pos: GridPos, to_pos: GridPos, agent_id: str) -> bool:
        """Move an agent from one tile to another.
        
        Returns:
            True if move was successful
        """
        if not self.is_valid_position(to_pos):
            return False
        
        self.vacate_tile(from_pos)
        return self.occupy_tile(to_pos, agent_id)


@dataclass
class Percept:
    """A percept represents what the agent can sense at its current position.
    
    This is the output of the perception system - a structured representation
    of the immediate environment that the agent can use for decision-making.
    
    Attributes:
        position: Current grid position
        terrain: Terrain type at current position
        nearby_resources: List of resources visible nearby
        agent_position: Where the agent is (for self-reference)
        can_move_north/south/east/west: Whether movement is possible
    """
    position: GridPos
    terrain: TerrainType
    nearby_resources: list[tuple[ResourceType, GridPos, float]] = field(default_factory=list)
    can_move_north: bool = False
    can_move_south: bool = False
    can_move_east: bool = False
    can_move_west: bool = False
    current_resource: ResourceType = ResourceType.NONE
    resource_amount: float = 0.0
    
    def has_nearby_resource(self, resource_type: ResourceType) -> bool:
        """Check if there's a specific resource type nearby."""
        return any(r[0] == resource_type for r in self.nearby_resources)
    
    def get_nearest_resource(self, resource_type: ResourceType) -> tuple[GridPos, float] | None:
        """Get the position and distance of the nearest resource of a type."""
        matching = [(pos, dist) for rtype, pos, dist in self.nearby_resources if rtype == resource_type]
        if not matching:
            return None
        return min(matching, key=lambda x: x[1])


def create_simple_island(width: int = 40, height: int = 30) -> Island:
    """Create a simple island environment.
    
    This is a convenience function for creating a standard island
    with reasonable default parameters.
    
    Args:
        width: Width of the island grid
        height: Height of the island grid
        
    Returns:
        A new Island instance
    """
    return Island(width=width, height=height)
