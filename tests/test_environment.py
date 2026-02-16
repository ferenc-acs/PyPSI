"""Tests for environment module."""

import pytest
from pypsi.environment import (
    Direction,
    GridPos,
    Island,
    Percept,
    ResourceType,
    TerrainType,
    Tile,
    create_simple_island,
)


class TestGridPos:
    """Tests for GridPos."""
    
    def test_grid_pos_creation(self):
        pos = GridPos(5, 10)
        assert pos.x == 5
        assert pos.y == 10
    
    def test_grid_pos_addition(self):
        pos1 = GridPos(1, 2)
        pos2 = GridPos(3, 4)
        result = pos1 + pos2
        assert result.x == 4
        assert result.y == 6
    
    def test_distance_to(self):
        pos1 = GridPos(0, 0)
        pos2 = GridPos(3, 4)
        assert pos2.distance_to(pos1) == 5.0
    
    def test_manhattan_distance(self):
        pos1 = GridPos(0, 0)
        pos2 = GridPos(3, 4)
        assert pos2.manhattan_distance(pos1) == 7


class TestDirection:
    """Tests for Direction enum."""
    
    def test_direction_to_pos(self):
        assert Direction.NORTH.to_pos() == GridPos(0, -1)
        assert Direction.EAST.to_pos() == GridPos(1, 0)
        assert Direction.SOUTH.to_pos() == GridPos(0, 1)
        assert Direction.WEST.to_pos() == GridPos(-1, 0)


class TestTile:
    """Tests for Tile."""
    
    def test_tile_creation(self):
        tile = Tile(x=5, y=10, terrain=TerrainType.GRASS)
        assert tile.x == 5
        assert tile.y == 10
        assert tile.terrain == TerrainType.GRASS
    
    def test_tile_passable(self):
        grass = Tile(0, 0, TerrainType.GRASS)
        water = Tile(0, 0, TerrainType.WATER)
        mountain = Tile(0, 0, TerrainType.MOUNTAIN)
        
        assert grass.is_passable()
        assert not water.is_passable()
        assert not mountain.is_passable()
    
    def test_has_resource(self):
        tile = Tile(0, 0, resource=ResourceType.FOOD, resource_amount=1.0)
        assert tile.has_resource()
        
        tile.consume_resource(0.5)
        assert tile.has_resource()
        
        tile.consume_resource(1.0)
        assert not tile.has_resource()
    
    def test_consume_resource(self):
        tile = Tile(0, 0, resource=ResourceType.FOOD, resource_amount=1.0)
        consumed = tile.consume_resource(0.3)
        assert consumed == 0.3
        assert tile.resource_amount == 0.7


class TestIsland:
    """Tests for Island."""
    
    def test_island_creation(self):
        island = Island(width=20, height=15)
        assert island.width == 20
        assert island.height == 15
        assert len(island.tiles) == 15
        assert len(island.tiles[0]) == 20
    
    def test_get_tile(self):
        island = create_simple_island(20, 15)
        tile = island.get_tile(GridPos(10, 10))
        assert tile is not None
        assert tile.x == 10
        assert tile.y == 10
    
    def test_get_tile_out_of_bounds(self):
        island = create_simple_island(10, 10)
        assert island.get_tile(GridPos(-1, 0)) is None
        assert island.get_tile(GridPos(0, -1)) is None
        assert island.get_tile(GridPos(10, 0)) is None
        assert island.get_tile(GridPos(0, 10)) is None
    
    def test_is_valid_position(self):
        island = create_simple_island(20, 15)
        center_x = island.width // 2
        center_y = island.height // 2
        
        # Center should be valid (likely grass/forest)
        assert island.is_valid_position(GridPos(center_x, center_y))
    
    def test_occupy_and_vacate_tile(self):
        island = create_simple_island(20, 15)
        center = GridPos(island.width // 2, island.height // 2)
        
        # Find a passable tile
        while not island.get_tile(center).is_passable():
            center = GridPos(center.x + 1, center.y)
        
        assert island.occupy_tile(center, "agent_1")
        assert island.get_tile(center).occupied_by == "agent_1"
        
        # Should fail if already occupied
        assert not island.occupy_tile(center, "agent_2")
        
        island.vacate_tile(center)
        assert island.get_tile(center).occupied_by is None
    
    def test_move_agent(self):
        island = create_simple_island(20, 15)
        start = GridPos(island.width // 2, island.height // 2)
        
        # Find a valid starting position
        while not island.get_tile(start).is_passable():
            start = GridPos(start.x + 1, start.y)
        
        island.occupy_tile(start, "agent")
        
        # Try to move to adjacent position
        target = GridPos(start.x + 1, start.y)
        if island.is_valid_position(target):
            assert island.move_agent(start, target, "agent")
            assert island.get_tile(start).occupied_by is None
            assert island.get_tile(target).occupied_by == "agent"
    
    def test_get_neighbors(self):
        island = create_simple_island(20, 15)
        center = GridPos(10, 10)
        neighbors = island.get_neighbors(center, diagonal=False)
        
        # Should have up to 4 neighbors (cardinal directions)
        assert len(neighbors) <= 4
        
        # With diagonal, up to 8
        neighbors_diag = island.get_neighbors(center, diagonal=True)
        assert len(neighbors_diag) <= 8


class TestPercept:
    """Tests for Percept."""
    
    def test_percept_creation(self):
        percept = Percept(
            position=GridPos(5, 5),
            terrain=TerrainType.GRASS,
            can_move_north=True,
            can_move_south=False,
        )
        assert percept.position.x == 5
        assert percept.terrain == TerrainType.GRASS
        assert percept.can_move_north
        assert not percept.can_move_south
    
    def test_has_nearby_resource(self):
        percept = Percept(
            position=GridPos(0, 0),
            terrain=TerrainType.GRASS,
            nearby_resources=[(ResourceType.FOOD, GridPos(1, 0), 1.0)],
        )
        assert percept.has_nearby_resource(ResourceType.FOOD)
        assert not percept.has_nearby_resource(ResourceType.WATER)


class TestCreateSimpleIsland:
    """Tests for create_simple_island factory function."""
    
    def test_create_simple_island(self):
        island = create_simple_island(30, 20)
        assert island.width == 30
        assert island.height == 20
        
        # Should have some variety of terrain
        terrains = set()
        for row in island.tiles:
            for tile in row:
                terrains.add(tile.terrain)
        
        # Should have at least grass and water
        assert TerrainType.GRASS in terrains or TerrainType.FOREST in terrains
        assert TerrainType.WATER in terrains
