"""Action system for PyPSI - What the agent can do in the world.

This module implements the action schemas that allow the PSI agent
to interact with the environment. Actions are the bridge between
the agent's motivational system and the environment.

Key features:
- Action schemas with preconditions and effects
- Movement actions (navigation)
- Resource consumption actions (eat, drink, rest)
- Action selection based on motive strength
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..environment.island import GridPos, Island, Percept

from ..environment.island import ResourceType
from ..needs.tanks import NeedType


class ActionResult(Enum):
    """Result of executing an action."""
    SUCCESS = auto()      #: Action completed successfully
    FAILURE = auto()      #: Action failed (preconditions not met)
    IN_PROGRESS = auto()  #: Action is still executing (for multi-step actions)
    INVALID = auto()      #: Action cannot be executed in current state


from enum import Enum, auto


@dataclass
class ActionOutcome:
    """Outcome of executing an action.
    
    Attributes:
        result: Whether the action succeeded, failed, etc.
        message: Human-readable description of outcome
        needs_satisfied: Dict of need types to amount satisfied
        new_position: New position if action involved movement
    """
    result: ActionResult
    message: str = ""
    needs_satisfied: dict[NeedType, float] = field(default_factory=dict)
    new_position: GridPos | None = None


class Action(ABC):
    """Abstract base class for actions.
    
    An action represents something the agent can do in the environment.
    Each action has:
    - Preconditions that must be met
    - Effects that change the world or agent state
    - A cost (time, energy, etc.)
    
    Actions are the building blocks of behavior in PSI Theory.
    """
    
    def __init__(self, name: str, cost: float = 1.0) -> None:
        """Initialize an action.
        
        Args:
            name: Human-readable action name
            cost: Action cost (e.g., energy expenditure)
        """
        self.name = name
        self.cost = cost
    
    @abstractmethod
    def check_preconditions(
        self, 
        island: Island, 
        position: GridPos, 
        percept: Percept,
        need_system: NeedTankSystem
    ) -> bool:
        """Check if this action can be executed.
        
        Args:
            island: The environment
            position: Agent's current position
            percept: Current percept
            need_system: Agent's need system
            
        Returns:
            True if action can be executed
        """
        pass
    
    @abstractmethod
    def execute(
        self, 
        island: Island, 
        position: GridPos,
        need_system: NeedTankSystem
    ) -> ActionOutcome:
        """Execute the action.
        
        Args:
            island: The environment
            position: Agent's current position
            need_system: Agent's need system
            
        Returns:
            Outcome of the action
        """
        pass
    
    def get_value_for_need(self, need_type: NeedType) -> float:
        """Get how much this action satisfies a particular need.
        
        This is used by the motive system for action selection.
        
        Args:
            need_type: The need to check
            
        Returns:
            Value from 0.0 (no satisfaction) to 1.0 (full satisfaction)
        """
        # Default: actions don't satisfy any needs
        return 0.0
    
    def get_expectation(self) -> float:
        """Get the probability of successfully executing this action.
        
        Returns:
            Probability from 0.0 to 1.0
        """
        # Default: actions are always expected to succeed if preconditions are met
        return 1.0
    
    def __repr__(self) -> str:
        return f"Action({self.name})"


class MoveAction(Action):
    """Move in a cardinal direction."""
    
    def __init__(self, direction: Direction, cost: float = 0.1) -> None:
        """Initialize a move action.
        
        Args:
            direction: Direction to move
            cost: Movement cost (energy expenditure)
        """
        super().__init__(f"move_{direction.name.lower()}", cost)
        self.direction = direction
    
    def check_preconditions(
        self, 
        island: Island, 
        position: GridPos, 
        percept: Percept,
        need_system: NeedTankSystem
    ) -> bool:
        """Check if movement is possible."""
        from ..environment.island import Direction
        
        direction_map = {
            Direction.NORTH: percept.can_move_north,
            Direction.SOUTH: percept.can_move_south,
            Direction.EAST: percept.can_move_east,
            Direction.WEST: percept.can_move_west,
        }
        return direction_map.get(self.direction, False)
    
    def execute(
        self, 
        island: Island, 
        position: GridPos,
        need_system: NeedTankSystem
    ) -> ActionOutcome:
        """Execute the movement."""
        new_pos = position + self.direction.to_pos()
        
        if island.move_agent(position, new_pos, "agent"):
            return ActionOutcome(
                result=ActionResult.SUCCESS,
                message=f"Moved {self.direction.name}",
                new_position=new_pos
            )
        else:
            return ActionOutcome(
                result=ActionResult.FAILURE,
                message=f"Failed to move {self.direction.name}"
            )


class EatAction(Action):
    """Eat food at the current location."""
    
    def __init__(self, cost: float = 0.05) -> None:
        super().__init__("eat", cost)
    
    def check_preconditions(
        self, 
        island: Island, 
        position: GridPos, 
        percept: Percept,
        need_system: NeedTankSystem
    ) -> bool:
        """Check if there's food to eat."""
        return (percept.current_resource == ResourceType.FOOD and 
                percept.resource_amount > 0)
    
    def execute(
        self, 
        island: Island, 
        position: GridPos,
        need_system: NeedTankSystem
    ) -> ActionOutcome:
        """Consume food from the current tile."""
        from ..environment.island import ResourceType
        from ..needs.tanks import NeedType
        
        tile = island.get_tile(position)
        if tile and tile.resource == ResourceType.FOOD and tile.resource_amount > 0:
            consumed = tile.consume_resource(0.3)
            satisfaction = consumed * 0.8  # Convert to need satisfaction
            need_system.satisfy_need(NeedType.HUNGER, satisfaction)
            
            return ActionOutcome(
                result=ActionResult.SUCCESS,
                message=f"Ate food (satisfied hunger by {satisfaction:.2f})",
                needs_satisfied={NeedType.HUNGER: satisfaction}
            )
        
        return ActionOutcome(
            result=ActionResult.FAILURE,
            message="No food to eat"
        )
    
    def get_value_for_need(self, need_type: NeedType) -> float:
        """Eating satisfies hunger."""
        return 1.0 if need_type == NeedType.HUNGER else 0.0


class DrinkAction(Action):
    """Drink water at the current location."""
    
    def __init__(self, cost: float = 0.05) -> None:
        super().__init__("drink", cost)
    
    def check_preconditions(
        self, 
        island: Island, 
        position: GridPos, 
        percept: Percept,
        need_system: NeedTankSystem
    ) -> bool:
        """Check if there's water to drink."""
        return (percept.current_resource == ResourceType.WATER and 
                percept.resource_amount > 0)
    
    def execute(
        self, 
        island: Island, 
        position: GridPos,
        need_system: NeedTankSystem
    ) -> ActionOutcome:
        """Consume water from the current tile."""
        from ..environment.island import ResourceType
        from ..needs.tanks import NeedType
        
        tile = island.get_tile(position)
        if tile and tile.resource == ResourceType.WATER and tile.resource_amount > 0:
            consumed = tile.consume_resource(0.4)
            satisfaction = consumed * 0.9  # Water is very effective for thirst
            need_system.satisfy_need(NeedType.THIRST, satisfaction)
            
            return ActionOutcome(
                result=ActionResult.SUCCESS,
                message=f"Drank water (satisfied thirst by {satisfaction:.2f})",
                needs_satisfied={NeedType.THIRST: satisfaction}
            )
        
        return ActionOutcome(
            result=ActionResult.FAILURE,
            message="No water to drink"
        )
    
    def get_value_for_need(self, need_type: NeedType) -> float:
        """Drinking satisfies thirst."""
        return 1.0 if need_type == NeedType.THIRST else 0.0


class RestAction(Action):
    """Rest at the current location (needs shelter)."""
    
    def __init__(self, cost: float = 0.0) -> None:  # Resting doesn't cost energy
        super().__init__("rest", cost)
    
    def check_preconditions(
        self, 
        island: Island, 
        position: GridPos, 
        percept: Percept,
        need_system: NeedTankSystem
    ) -> bool:
        """Check if there's a shelter to rest in."""
        return (percept.current_resource == ResourceType.SHELTER and 
                percept.resource_amount > 0)
    
    def execute(
        self, 
        island: Island, 
        position: GridPos,
        need_system: NeedTankSystem
    ) -> ActionOutcome:
        """Rest to recover energy."""
        from ..environment.island import ResourceType
        from ..needs.tanks import NeedType
        
        tile = island.get_tile(position)
        if tile and tile.resource == ResourceType.SHELTER and tile.resource_amount > 0:
            # Resting doesn't consume the shelter, just uses it
            satisfaction = 0.3  # Rest recovers energy steadily
            need_system.satisfy_need(NeedType.ENERGY, satisfaction)
            
            return ActionOutcome(
                result=ActionResult.SUCCESS,
                message=f"Rested (recovered energy by {satisfaction:.2f})",
                needs_satisfied={NeedType.ENERGY: satisfaction}
            )
        
        return ActionOutcome(
            result=ActionResult.FAILURE,
            message="No shelter to rest in"
        )
    
    def get_value_for_need(self, need_type: NeedType) -> float:
        """Resting satisfies energy need."""
        return 1.0 if need_type == NeedType.ENERGY else 0.0


class ExploreAction(Action):
    """Move toward an unexplored or interesting area.
    
    This is a higher-level action that selects a movement direction
    based on the percept (e.g., toward visible resources).
    """
    
    def __init__(self, cost: float = 0.1) -> None:
        super().__init__("explore", cost)
        self.selected_direction: Direction | None = None
    
    def check_preconditions(
        self, 
        island: Island, 
        position: GridPos, 
        percept: Percept,
        need_system: NeedTankSystem
    ) -> bool:
        """Check if any movement is possible."""
        return (percept.can_move_north or percept.can_move_south or 
                percept.can_move_east or percept.can_move_west)
    
    def execute(
        self, 
        island: Island, 
        position: GridPos,
        need_system: NeedTankSystem
    ) -> ActionOutcome:
        """Move in an exploratory direction."""
        # For now, just pick a random valid direction
        # In a full implementation, this would use the percept to guide exploration
        import random
        
        from ..environment.island import Direction
        
        valid_directions = []
        percept = None  # We'd need to pass this in, but for simplicity...
        
        # This is a placeholder - in a real implementation,
        # we'd use the percept to choose wisely
        directions = list(Direction)[:4]  # Cardinal directions only
        random.shuffle(directions)
        
        for direction in directions:
            new_pos = position + direction.to_pos()
            if island.is_valid_position(new_pos):
                if island.move_agent(position, new_pos, "agent"):
                    return ActionOutcome(
                        result=ActionResult.SUCCESS,
                        message=f"Explored {direction.name}",
                        new_position=new_pos
                    )
        
        return ActionOutcome(
            result=ActionResult.FAILURE,
            message="No valid direction to explore"
        )


# Need to import Direction here to avoid circular imports
from ..environment.island import Direction


class ActionLibrary:
    """Library of available actions for the agent.
    
    This class manages all the actions the agent can perform,
    providing convenient access and filtering.
    """
    
    def __init__(self) -> None:
        """Initialize with default actions."""
        self.actions: dict[str, Action] = {}
        self._add_default_actions()
    
    def _add_default_actions(self) -> None:
        """Add the default set of actions."""
        # Movement actions
        for direction in [Direction.NORTH, Direction.SOUTH, Direction.EAST, Direction.WEST]:
            action = MoveAction(direction)
            self.actions[action.name] = action
        
        # Resource consumption actions
        self.actions["eat"] = EatAction()
        self.actions["drink"] = DrinkAction()
        self.actions["rest"] = RestAction()
        
        # Exploration
        self.actions["explore"] = ExploreAction()
    
    def get_action(self, name: str) -> Action | None:
        """Get an action by name."""
        return self.actions.get(name)
    
    def get_all_actions(self) -> list[Action]:
        """Get all available actions."""
        return list(self.actions.values())
    
    def get_executable_actions(
        self,
        island: Island,
        position: GridPos,
        percept: Percept,
        need_system: NeedTankSystem
    ) -> list[Action]:
        """Get actions that can be executed in the current state.
        
        Args:
            island: The environment
            position: Agent's position
            percept: Current percept
            need_system: Agent's need system
            
        Returns:
            List of actions with satisfied preconditions
        """
        executable = []
        for action in self.actions.values():
            if action.check_preconditions(island, position, percept, need_system):
                executable.append(action)
        return executable
    
    def add_action(self, action: Action) -> None:
        """Add a custom action to the library."""
        self.actions[action.name] = action


def create_default_action_library() -> ActionLibrary:
    """Create an action library with default actions."""
    return ActionLibrary()
