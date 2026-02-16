"""Tests for action module."""

import pytest
from pypsi.action import (
    ActionLibrary,
    ActionResult,
    EatAction,
    DrinkAction,
    RestAction,
    MoveAction,
    create_default_action_library,
)
from pypsi.environment import (
    Direction,
    GridPos,
    Island,
    Percept,
    ResourceType,
    TerrainType,
)
from pypsi.needs import NeedTankSystem, NeedType


class TestActionLibrary:
    """Tests for ActionLibrary."""
    
    def test_library_creation(self):
        library = create_default_action_library()
        assert "eat" in library.actions
        assert "drink" in library.actions
        assert "rest" in library.actions
        assert "move_north" in library.actions
    
    def test_get_action(self):
        library = create_default_action_library()
        eat_action = library.get_action("eat")
        assert eat_action is not None
        assert eat_action.name == "eat"
    
    def test_get_all_actions(self):
        library = create_default_action_library()
        actions = library.get_all_actions()
        assert len(actions) >= 7  # 4 moves + eat + drink + rest + explore
    
    def test_add_custom_action(self):
        library = ActionLibrary()
        custom_action = EatAction()  # Just using EatAction as a custom example
        custom_action.name = "custom_eat"
        library.add_action(custom_action)
        assert "custom_eat" in library.actions


class TestMoveAction:
    """Tests for MoveAction."""
    
    def test_move_action_creation(self):
        action = MoveAction(Direction.NORTH)
        assert action.name == "move_north"
        assert action.direction == Direction.NORTH
    
    def test_move_action_preconditions(self):
        island = Island(width=10, height=10)
        need_system = NeedTankSystem()
        
        # Place agent on a passable tile
        pos = GridPos(5, 5)
        island.occupy_tile(pos, "agent")
        
        # Create percept where north is passable
        percept = Percept(
            position=pos,
            terrain=TerrainType.GRASS,
            can_move_north=True,
            can_move_south=True,
            can_move_east=True,
            can_move_west=True,
        )
        
        action = MoveAction(Direction.NORTH)
        assert action.check_preconditions(island, pos, percept, need_system)
    
    def test_move_action_execution(self):
        island = Island(width=10, height=10)
        need_system = NeedTankSystem()
        
        pos = GridPos(5, 5)
        island.occupy_tile(pos, "agent")
        
        action = MoveAction(Direction.EAST)
        outcome = action.execute(island, pos, need_system)
        
        # Should either succeed or fail based on terrain
        assert outcome.result in (ActionResult.SUCCESS, ActionResult.FAILURE)


class TestEatAction:
    """Tests for EatAction."""
    
    def test_eat_action_creation(self):
        action = EatAction()
        assert action.name == "eat"
    
    def test_eat_action_value_for_need(self):
        action = EatAction()
        assert action.get_value_for_need(NeedType.HUNGER) == 1.0
        assert action.get_value_for_need(NeedType.THIRST) == 0.0
        assert action.get_value_for_need(NeedType.ENERGY) == 0.0
    
    def test_eat_action_preconditions(self):
        action = EatAction()
        island = Island(width=10, height=10)
        need_system = NeedTankSystem()
        
        # Position with food
        pos_with_food = GridPos(5, 5)
        island.get_tile(pos_with_food).resource = ResourceType.FOOD
        island.get_tile(pos_with_food).resource_amount = 1.0
        
        percept_with_food = Percept(
            position=pos_with_food,
            terrain=TerrainType.GRASS,
            current_resource=ResourceType.FOOD,
            resource_amount=1.0,
        )
        
        assert action.check_preconditions(island, pos_with_food, percept_with_food, need_system)
        
        # Position without food
        pos_no_food = GridPos(6, 6)
        percept_no_food = Percept(
            position=pos_no_food,
            terrain=TerrainType.GRASS,
            current_resource=ResourceType.NONE,
            resource_amount=0.0,
        )
        
        assert not action.check_preconditions(island, pos_no_food, percept_no_food, need_system)
    
    def test_eat_action_execution(self):
        action = EatAction()
        island = Island(width=10, height=10)
        need_system = NeedTankSystem()
        
        pos = GridPos(5, 5)
        island.get_tile(pos).resource = ResourceType.FOOD
        island.get_tile(pos).resource_amount = 1.0
        
        # Set hunger to half
        need_system.get_tank(NeedType.HUNGER).current_level = 0.5
        
        outcome = action.execute(island, pos, need_system)
        
        assert outcome.result == ActionResult.SUCCESS
        assert outcome.needs_satisfied[NeedType.HUNGER] > 0
        assert island.get_tile(pos).resource_amount < 1.0


class TestDrinkAction:
    """Tests for DrinkAction."""
    
    def test_drink_action_creation(self):
        action = DrinkAction()
        assert action.name == "drink"
    
    def test_drink_action_value_for_need(self):
        action = DrinkAction()
        assert action.get_value_for_need(NeedType.THIRST) == 1.0
        assert action.get_value_for_need(NeedType.HUNGER) == 0.0
    
    def test_drink_action_execution(self):
        action = DrinkAction()
        island = Island(width=10, height=10)
        need_system = NeedTankSystem()
        
        pos = GridPos(5, 5)
        island.get_tile(pos).resource = ResourceType.WATER
        island.get_tile(pos).resource_amount = 1.0
        
        outcome = action.execute(island, pos, need_system)
        
        assert outcome.result == ActionResult.SUCCESS
        assert outcome.needs_satisfied[NeedType.THIRST] > 0


class TestRestAction:
    """Tests for RestAction."""
    
    def test_rest_action_creation(self):
        action = RestAction()
        assert action.name == "rest"
    
    def test_rest_action_value_for_need(self):
        action = RestAction()
        assert action.get_value_for_need(NeedType.ENERGY) == 1.0
        assert action.get_value_for_need(NeedType.HUNGER) == 0.0


class TestActionOutcome:
    """Tests for ActionOutcome."""
    
    def test_outcome_creation(self):
        from pypsi.action import ActionOutcome
        outcome = ActionOutcome(
            result=ActionResult.SUCCESS,
            message="Test message",
            needs_satisfied={NeedType.HUNGER: 0.5},
        )
        assert outcome.result == ActionResult.SUCCESS
        assert outcome.message == "Test message"
        assert outcome.needs_satisfied[NeedType.HUNGER] == 0.5
