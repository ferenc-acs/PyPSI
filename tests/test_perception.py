"""Tests for perception module."""

import pytest
from pypsi.perception import (
    PerceptionConfig,
    PerceptionSystem,
    SensoryMemory,
    create_default_perception_system,
)
from pypsi.environment import (
    GridPos,
    Island,
    Percept,
    ResourceType,
    TerrainType,
    create_simple_island,
)


class TestPerceptionConfig:
    """Tests for PerceptionConfig."""
    
    def test_default_config(self):
        config = PerceptionConfig()
        assert config.sensory_radius == 5
        assert not config.can_see_through_forest
        assert config.resource_detection_threshold == 0.1
    
    def test_custom_config(self):
        config = PerceptionConfig(
            sensory_radius=10,
            can_see_through_forest=True,
            resource_detection_threshold=0.5,
        )
        assert config.sensory_radius == 10
        assert config.can_see_through_forest
        assert config.resource_detection_threshold == 0.5


class TestPerceptionSystem:
    """Tests for PerceptionSystem."""
    
    def test_system_creation(self):
        system = create_default_perception_system()
        assert system.config.sensory_radius == 5
    
    def test_perceive_basic(self):
        island = create_simple_island(20, 15)
        system = PerceptionSystem()
        
        # Find a valid position
        pos = GridPos(10, 10)
        while not island.get_tile(pos).is_passable():
            pos = GridPos(pos.x + 1, pos.y)
        
        percept = system.perceive(island, pos)
        
        assert isinstance(percept, Percept)
        assert percept.position == pos
        assert percept.terrain is not None
    
    def test_perceive_with_resources(self):
        island = create_simple_island(20, 15)
        system = PerceptionSystem(PerceptionConfig(sensory_radius=3))
        
        pos = GridPos(10, 10)
        while not island.get_tile(pos).is_passable():
            pos = GridPos(pos.x + 1, pos.y)
        
        # Place a resource nearby
        nearby_pos = GridPos(pos.x + 2, pos.y)
        if island.get_tile(nearby_pos):
            island.get_tile(nearby_pos).resource = ResourceType.FOOD
            island.get_tile(nearby_pos).resource_amount = 1.0
        
        percept = system.perceive(island, pos)
        
        # Should detect the food
        assert percept.has_nearby_resource(ResourceType.FOOD)
        
        nearest = percept.get_nearest_resource(ResourceType.FOOD)
        assert nearest is not None
        assert nearest[0] == nearby_pos
    
    def test_perceive_movement_possibilities(self):
        island = create_simple_island(20, 15)
        system = PerceptionSystem()
        
        # Find a grass tile
        pos = GridPos(10, 10)
        while not island.get_tile(pos) or island.get_tile(pos).terrain != TerrainType.GRASS:
            pos = GridPos(pos.x + 1, pos.y)
        
        percept = system.perceive(island, pos)
        
        # Should have at least some movement options on grass
        assert (percept.can_move_north or percept.can_move_south or 
                percept.can_move_east or percept.can_move_west)
    
    def test_get_visible_tiles(self):
        island = create_simple_island(20, 15)
        system = PerceptionSystem(PerceptionConfig(sensory_radius=2))
        
        pos = GridPos(10, 10)
        while not island.get_tile(pos).is_passable():
            pos = GridPos(pos.x + 1, pos.y)
        
        visible = system.get_visible_tiles(island, pos)
        
        # Should see tiles within radius 2 (approx 13 tiles in circle)
        assert len(visible) > 0
        assert len(visible) <= 25  # 5x5 grid minus corners


class TestSensoryMemory:
    """Tests for SensoryMemory."""
    
    def test_memory_creation(self):
        memory = SensoryMemory()
        assert memory.max_memory_size == 10
        assert memory.memory_decay_time == 30.0
    
    def test_add_and_retrieve_percept(self):
        memory = SensoryMemory()
        percept = Percept(
            position=GridPos(5, 5),
            terrain=TerrainType.GRASS,
        )
        
        memory.add_percept(percept, timestamp=0.0)
        recent = memory.get_recent_percepts(current_time=10.0)
        
        assert len(recent) == 1
        assert recent[0].position == GridPos(5, 5)
    
    def test_memory_decay(self):
        memory = SensoryMemory(memory_decay_time=5.0)
        percept = Percept(
            position=GridPos(5, 5),
            terrain=TerrainType.GRASS,
        )
        
        memory.add_percept(percept, timestamp=0.0)
        
        # Before decay
        recent = memory.get_recent_percepts(current_time=3.0)
        assert len(recent) == 1
        
        # After decay
        recent = memory.get_recent_percepts(current_time=10.0)
        assert len(recent) == 0
    
    def test_memory_size_limit(self):
        memory = SensoryMemory(max_memory_size=3)
        
        for i in range(5):
            percept = Percept(
                position=GridPos(i, i),
                terrain=TerrainType.GRASS,
            )
            memory.add_percept(percept, timestamp=float(i))
        
        # Should only keep last 3
        recent = memory.get_recent_percepts(current_time=10.0)
        assert len(recent) == 3
    
    def test_find_last_seen_resource(self):
        memory = SensoryMemory()
        
        percept = Percept(
            position=GridPos(0, 0),
            terrain=TerrainType.GRASS,
            nearby_resources=[(ResourceType.FOOD, GridPos(5, 5), 3.0)],
        )
        
        memory.add_percept(percept, timestamp=0.0)
        
        found_pos = memory.find_last_seen_resource(ResourceType.FOOD, current_time=5.0)
        assert found_pos == GridPos(5, 5)
        
        not_found = memory.find_last_seen_resource(ResourceType.WATER, current_time=5.0)
        assert not_found is None
    
    def test_clear_old_memories(self):
        memory = SensoryMemory(memory_decay_time=5.0)
        
        percept1 = Percept(position=GridPos(1, 1), terrain=TerrainType.GRASS)
        percept2 = Percept(position=GridPos(2, 2), terrain=TerrainType.GRASS)
        
        memory.add_percept(percept1, timestamp=0.0)
        memory.add_percept(percept2, timestamp=11.0)  # Within decay window (15-11=4 < 5)
        
        memory.clear_old_memories(current_time=15.0)
        
        # First percept should be cleared (15-0=15 > 5), second should remain (15-11=4 < 5)
        recent = memory.get_recent_percepts(current_time=15.0)
        assert len(recent) == 1
        assert recent[0].position == GridPos(2, 2)
