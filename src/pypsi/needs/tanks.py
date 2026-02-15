"""Need tank system for PyPSI - PSI Theory cognitive architecture.

This module implements the PSI Theory need/drive system based on the
"Wasserkessel" (water tank) model. Needs are represented as tanks that
continuously drain and must be periodically filled through satisfaction.

The gap between target level (Sollmarke) and current level (Ist-Zustand)
creates Bedarf (need/drive), which motivates behavior selection.

Based on:
    Dörner, D., Bartl, C., & others. PSI Theory need system.
    See: https://en.wikipedia.org/wiki/Psi-Theory#The_Dynamical_Sources_of_Behavior
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Self


class NeedType(Enum):
    """The six fundamental need types in PSI Theory.
    
    PSI Theory distinguishes between:
    - **Material needs**: Related to physical survival (physiological)
    - **Informational needs**: Related to cognitive processing and social needs
    
    Each need type has its own tank with different depletion rates and
    satisfaction mechanisms.
    """
    # Material needs (physiological)
    HUNGER = auto()      #: Need for fuel/food - energy intake
    THIRST = auto()      #: Need for water - hydration
    ENERGY = auto()      #: Need for rest/sleep - recuperation
    
    # Informational needs (cognitive/social)
    CERTAINTY = auto()   #: Need for predictability - understanding the world
    COMPETENCE = auto()  #: Need for efficacy - ability to achieve goals
    AFFILIATION = auto() #: Need for social connection - belonging
    
    def is_material(self) -> bool:
        """Check if this is a material (physiological) need."""
        return self in (NeedType.HUNGER, NeedType.THIRST, NeedType.ENERGY)
    
    def is_informational(self) -> bool:
        """Check if this is an informational (cognitive/social) need."""
        return self in (NeedType.CERTAINTY, NeedType.COMPETENCE, NeedType.AFFILIATION)


@dataclass
class NeedTank:
    """A single need tank implementing the "Wasserkessel" model.
    
    In PSI Theory, needs are modeled as tanks that continuously drain
    (representing ongoing consumption/requirements) and can be filled
    through satisfaction events.
    
    Key concepts:
    - **Sollmarke** (target_level): The optimal/desired level
    - **Ist-Zustand** (current_level): The actual current level
    - **Bedarf** (deficit): The gap between target and current (drives behavior)
    - **Critical threshold**: When needs become dangerously low
    
    Attributes:
        need_type: Which type of need this tank represents
        target_level: Optimal level (Sollmarke), typically 1.0
        current_level: Current fill level (Ist-Zustand), 0.0 to target_level
        depletion_rate: How fast the tank drains per time unit
        fill_rate: How fast satisfaction fills the tank
        critical_threshold: Level below which need is considered critical
    """
    need_type: NeedType
    target_level: float = 1.0
    current_level: float = 1.0
    depletion_rate: float = 0.01
    fill_rate: float = 0.5
    critical_threshold: float = 0.2
    
    def __post_init__(self) -> None:
        """Validate tank parameters."""
        if not 0.0 <= self.target_level <= 1.0:
            raise ValueError(f"target_level must be in [0.0, 1.0], got {self.target_level}")
        if not 0.0 <= self.current_level <= self.target_level:
            raise ValueError(
                f"current_level must be in [0.0, {self.target_level}], got {self.current_level}"
            )
        if self.depletion_rate < 0:
            raise ValueError(f"depletion_rate must be non-negative, got {self.depletion_rate}")
        if self.fill_rate < 0:
            raise ValueError(f"fill_rate must be non-negative, got {self.fill_rate}")
        if not 0.0 <= self.critical_threshold <= 1.0:
            raise ValueError(
                f"critical_threshold must be in [0.0, 1.0], got {self.critical_threshold}"
            )
    
    def update(self, dt: float = 1.0) -> Self:
        """Apply depletion over time.
        
        In PSI Theory, needs continuously drain - this represents the
        ongoing metabolic and cognitive costs of existence.
        
        Args:
            dt: Time delta (default 1.0 = one time unit)
            
        Returns:
            Self for method chaining
        """
        depletion = self.depletion_rate * dt
        self.current_level = max(0.0, self.current_level - depletion)
        return self
    
    def satisfy(self, amount: float | None = None) -> Self:
        """Fill the tank through satisfaction.
        
        When the agent successfully addresses a need (e.g., eats when hungry,
        rests when tired), the tank is filled.
        
        Args:
            amount: How much to fill (default uses fill_rate)
            
        Returns:
            Self for method chaining
        """
        fill_amount = amount if amount is not None else self.fill_rate
        self.current_level = min(self.target_level, self.current_level + fill_amount)
        return self
    
    def bedarf(self) -> float:
        """Calculate the deficit (Bedarf) that drives behavior.
        
        In PSI Theory, Bedarf is the gap between target and current level.
        This creates the "drive" that motivates the agent to select actions
        that will satisfy the need.
        
        Returns:
            Deficit value (target - current), 0.0 means fully satisfied
        """
        return self.target_level - self.current_level
    
    def is_critical(self) -> bool:
        """Check if the need is critically low.
        
        When needs fall below critical threshold, this triggers
        emergency responses and prioritization in action selection.
        
        Returns:
            True if current_level < critical_threshold
        """
        return self.current_level < self.critical_threshold
    
    def satisfaction_ratio(self) -> float:
        """Get the ratio of current to target level.
        
        Returns:
            Value from 0.0 (empty) to 1.0 (full)
        """
        if self.target_level == 0.0:
            return 0.0
        return self.current_level / self.target_level
    
    def __repr__(self) -> str:
        """String representation showing tank status."""
        return (
            f"NeedTank({self.need_type.name}, "
            f"current={self.current_level:.3f}, "
            f"target={self.target_level:.3f}, "
            f"bedarf={self.bedarf():.3f})"
        )


@dataclass
class NeedTankSystem:
    """Manages all six need tanks in the PSI cognitive architecture.
    
    The NeedTankSystem provides centralized management of all need states,
    including updates, querying deficits, and motive selection support.
    
    Each need type has default parameters tuned for typical PSI agent
    behavior, but these can be customized per agent.
    """
    
    # Default configuration for each need type
    # Format: (target, depletion_rate, fill_rate, critical_threshold)
    DEFAULT_CONFIG: dict[NeedType, tuple[float, float, float, float]] = field(
        default_factory=lambda: {
            # Material needs - deplete relatively quickly
            NeedType.HUNGER: (1.0, 0.02, 0.8, 0.15),      # Food every ~50 steps
            NeedType.THIRST: (1.0, 0.03, 0.9, 0.1),       # Water more urgent
            NeedType.ENERGY: (1.0, 0.015, 0.6, 0.2),      # Sleep less urgent
            
            # Informational needs - deplete more slowly
            NeedType.CERTAINTY: (1.0, 0.005, 0.3, 0.25),  # Curiosity
            NeedType.COMPETENCE: (1.0, 0.008, 0.4, 0.2),  # Achievement
            NeedType.AFFILIATION: (1.0, 0.01, 0.5, 0.15), # Social needs
        }
    )
    
    tanks: dict[NeedType, NeedTank] = field(default_factory=dict)
    
    def __post_init__(self) -> None:
        """Initialize tanks for all need types if not provided."""
        if not self.tanks:
            for need_type in NeedType:
                config = self.DEFAULT_CONFIG[need_type]
                self.tanks[need_type] = NeedTank(
                    need_type=need_type,
                    target_level=config[0],
                    current_level=config[0],  # Start full
                    depletion_rate=config[1],
                    fill_rate=config[2],
                    critical_threshold=config[3],
                )
    
    def get_tank(self, need_type: NeedType) -> NeedTank:
        """Get the tank for a specific need type.
        
        Args:
            need_type: The type of need to retrieve
            
        Returns:
            The NeedTank instance for that need type
        """
        return self.tanks[need_type]
    
    def get_bedarf(self, need_type: NeedType) -> float:
        """Get the deficit for a specific need.
        
        This is the primary interface for motive selection - agents
        compare Bedarf values to determine which need to address next.
        
        Args:
            need_type: The type of need to check
            
        Returns:
            Deficit value (higher = more urgent need)
        """
        return self.tanks[need_type].bedarf()
    
    def get_all_bedarfe(self) -> dict[NeedType, float]:
        """Get all deficits for motive selection.
        
        Returns a mapping of all need types to their current deficit.
        This is used by the motive generation system to create weighted
        candidate behaviors.
        
        Returns:
            Dictionary mapping NeedType to deficit value
        """
        return {need_type: tank.bedarf() for need_type, tank in self.tanks.items()}
    
    def update_all(self, dt: float = 1.0) -> None:
        """Update all tanks with time delta.
        
        This is the main time-step update that applies depletion to
        all need tanks. Should be called regularly (e.g., each simulation step).
        
        Args:
            dt: Time delta (default 1.0 = one time unit)
        """
        for tank in self.tanks.values():
            tank.update(dt)
    
    def satisfy_need(self, need_type: NeedType, amount: float | None = None) -> None:
        """Satisfy a specific need by filling its tank.
        
        Args:
            need_type: Which need to satisfy
            amount: How much to fill (None = use tank's fill_rate)
        """
        self.tanks[need_type].satisfy(amount)
    
    def get_critical_needs(self) -> list[NeedType]:
        """Get list of needs that are critically low.
        
        Returns:
            List of NeedType values below critical threshold
        """
        return [
            need_type for need_type, tank in self.tanks.items()
            if tank.is_critical()
        ]
    
    def has_critical_needs(self) -> bool:
        """Check if any need is critically low.
        
        Returns:
            True if at least one need is below critical threshold
        """
        return any(tank.is_critical() for tank in self.tanks.values())
    
    def get_most_urgent_need(self) -> NeedType:
        """Get the need with highest deficit (Bedarf).
        
        This is useful for simple action selection strategies.
        
        Returns:
            The NeedType with highest current deficit
        """
        return max(self.tanks.keys(), key=lambda nt: self.tanks[nt].bedarf())
    
    def get_total_bedarf(self) -> float:
        """Get sum of all deficits.
        
        Can be used as a measure of overall agent distress.
        
        Returns:
            Sum of all Bedarf values
        """
        return sum(tank.bedarf() for tank in self.tanks.values())
    
    def reset_all(self) -> None:
        """Reset all tanks to full (target level).
        
        Useful for reinitializing agent state or debugging.
        """
        for tank in self.tanks.values():
            tank.current_level = tank.target_level
    
    def __repr__(self) -> str:
        """String representation showing all tank statuses."""
        tanks_str = ", ".join(
            f"{nt.name}={tank.current_level:.2f}" 
            for nt, tank in sorted(self.tanks.items(), key=lambda x: x[0].name)
        )
        return f"NeedTankSystem({tanks_str})"
