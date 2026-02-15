"""Motivator system for PyPSI - PSI Theory cognitive architecture.

This module implements the motivational system of PSI Theory, which transforms
need deficits (Bedarf) into actionable motives through the Expectation × Value
principle.

The motivational cascade in PSI Theory:
1. **Need Tanks** (tanks.py): Generate Bedarf (deficit signals)
2. **Motivators**: Accumulate and transform Bedarf into activity signals
3. **Motives**: Combine drives with goals (schemas that can satisfy needs)
4. **Motivselektor**: Selects the strongest motive based on Erwartung × Wert

Key concepts:
- **Motivator**: The "drive" component - how strongly a need pushes for action
- **Motive**: Drive + Goal - a specific intention to act in a particular way
- **Motivselektor**: The decision mechanism that resolves competition between motives
- **Erwartung × Wert**: The selection principle combining success probability with value

Based on:
    Dörner, D. PSI Theory motivation system.
    See: https://en.wikipedia.org/wiki/Psi-Theory#Selection_of_Actions
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from .tanks import NeedTankSystem, NeedType


class Schema(Protocol):
    """Protocol for goal schemas that can satisfy needs.
    
    In PSI Theory, a schema represents a behavioral program or action pattern
    that can potentially satisfy one or more needs. Schemas have an associated
    value indicating how well they address specific needs.
    """
    
    def get_value_for_need(self, need_type: NeedType) -> float:
        """Get the satisfaction value this schema provides for a need.
        
        Args:
            need_type: The need type to check
            
        Returns:
            Value from 0.0 (no satisfaction) to 1.0 (full satisfaction)
        """
        ...
    
    def get_expectation(self) -> float:
        """Get the probability of successfully executing this schema.
        
        Returns:
            Probability from 0.0 (certain failure) to 1.0 (certain success)
        """
        ...


@dataclass
class Motivator:
    """Accumulates Bedarf (deficit) signals into motivational activity.
    
    A Motivator tracks the accumulated deficit for a specific need type,
    transforming raw Bedarf into an activity signal that drives behavior.
    The activity grows logarithmically with accumulated deficit, providing
    bounded growth that prevents any single need from completely dominating.
    
    In PSI Theory, motivators serve as the bridge between physiological/cognitive
    needs and the motivational system that drives action selection.
    
    Key concepts:
    - **Accumulated Bedarf**: Running sum of deficit signals over time
    - **Activity**: log(1 + accumulated_bedarf), bounded motivational signal
    - **Decay**: Gradual reduction of accumulated signal when need is satisfied
    
    Attributes:
        need_type: Which need this motivator tracks
        accumulated_bedarf: Running sum of deficit signals
        decay_rate: Rate at which accumulated bedarf decays
        max_accumulation: Upper bound for accumulated bedarf
    """
    
    need_type: NeedType
    accumulated_bedarf: float = 0.0
    decay_rate: float = 0.1
    max_accumulation: float = 10.0
    
    def accumulate(self, bedarf: float) -> float:
        """Add a Bedarf signal to the accumulated total.
        
        When a need tank reports a deficit, that signal is accumulated by
        the corresponding motivator. This allows temporary deficits to build
        up motivational pressure over time.
        
        The accumulation is bounded to prevent runaway growth.
        
        Args:
            bedarf: The deficit value to accumulate (typically from NeedTank.bedarf())
            
        Returns:
            The new accumulated bedarf value
        """
        self.accumulated_bedarf = min(
            self.max_accumulation,
            self.accumulated_bedarf + max(0.0, bedarf)
        )
        return self.accumulated_bedarf
    
    def decay(self, dt: float = 1.0) -> float:
        """Apply decay to the accumulated bedarf.
        
        Over time, accumulated motivational signals decay if not reinforced
        by continued deficits. This allows the system to "forget" about
        transient needs that were briefly unsatisfied.
        
        Args:
            dt: Time delta (default 1.0 = one time unit)
            
        Returns:
            The new accumulated bedarf value after decay
        """
        decay_amount = self.decay_rate * dt
        self.accumulated_bedarf = max(0.0, self.accumulated_bedarf - decay_amount)
        return self.accumulated_bedarf
    
    def get_activity(self) -> float:
        """Calculate the motivational activity signal.
        
        Activity is computed as log(1 + accumulated_bedarf), which provides:
        - Bounded growth (logarithmic)
        - Sensitivity to small deficits (steep near zero)
        - Diminishing returns for large deficits
        
        This transformation prevents any single need from completely
        dominating the motivational landscape while still allowing
        urgent needs to have strong influence.
        
        Returns:
            Activity value (0.0 to ~2.4 for default max_accumulation=10)
        """
        return math.log1p(self.accumulated_bedarf)
    
    def reset(self) -> None:
        """Reset accumulated bedarf to zero.
        
        Called when a need is fully satisfied or when reinitializing
        the motivational state.
        """
        self.accumulated_bedarf = 0.0
    
    def __repr__(self) -> str:
        """String representation showing motivator state."""
        return (
            f"Motivator({self.need_type.name}, "
            f"acc={self.accumulated_bedarf:.3f}, "
            f"activity={self.get_activity():.3f})"
        )


@dataclass
class Motive:
    """A motive combines a drive (motivator) with a goal (schema).
    
    In PSI Theory, a motive represents an intention to perform a specific
    action (schema) to satisfy a specific need (via its motivator). The
    strength of a motive is determined by the Expectation × Value principle
    (Erwartung × Wert).
    
    Key concepts:
    - **Motivator**: The drive source - which need pushes for satisfaction
    - **Goal**: The schema that can potentially satisfy the need
    - **Expectation** (Erwartung): Probability of successfully executing the goal
    - **Value** (Wert): How much the goal satisfies the need
    - **Strength**: Erwartung × Wert - the overall motivational force
    
    The Expectation × Value principle ensures that:
    - High-value but impossible goals are not selected (0 expectation)
    - Easy but worthless goals are not selected (0 value)
    - Only goals with both reasonable expectation and value compete
    
    Attributes:
        motivator: The Motivator providing the drive
        goal: The Schema representing how to satisfy the need
        expectation_override: Optional override for expectation calculation
    """
    
    motivator: Motivator
    goal: Schema
    expectation_override: float | None = None
    
    def calculate_strength(self) -> float:
        """Calculate motive strength using Expectation × Value.
        
        This implements the core selection principle of PSI Theory:
        Strength = Expectation × Value × Activity
        
        Where:
        - Expectation: Probability of goal success (0.0 to 1.0)
        - Value: How well goal satisfies the need (0.0 to 1.0)
        - Activity: Current motivational activity from accumulated deficits
        
        Returns:
            Motive strength (higher = more compelling motive)
        """
        expectation = self.get_expectation()
        value = self.goal.get_value_for_need(self.motivator.need_type)
        activity = self.motivator.get_activity()
        
        return expectation * value * activity
    
    def get_expectation(self) -> float:
        """Get the expectation (probability of success) for this motive.
        
        Uses the override if set, otherwise queries the goal schema.
        
        Returns:
            Probability from 0.0 (certain failure) to 1.0 (certain success)
        """
        if self.expectation_override is not None:
            return max(0.0, min(1.0, self.expectation_override))
        return max(0.0, min(1.0, self.goal.get_expectation()))
    
    def get_motive_strength(self) -> float:
        """Alias for calculate_strength() for API consistency."""
        return self.calculate_strength()
    
    def get_need_type(self) -> NeedType:
        """Get the need type this motive addresses."""
        return self.motivator.need_type
    
    def __repr__(self) -> str:
        """String representation showing motive details."""
        return (
            f"Motive({self.motivator.need_type.name} -> {type(self.goal).__name__}, "
            f"strength={self.calculate_strength():.3f}, "
            f"exp={self.get_expectation():.3f})"
        )


@dataclass
class Motivselektor:
    """Selects among competing motives using the Expectation × Value principle.
    
    The Motivselektor (motive selector) is the decision mechanism in PSI Theory
    that resolves competition between multiple active motives. It implements
    a form of rational action selection based on the principle that the
    strongest motive should guide behavior.
    
    Selection criteria (in order):
    1. Filter out motives with zero strength (impossible or worthless)
    2. Select the motive with highest Erwartung × Wert strength
    3. Return None if no viable motives exist
    
    The Motivselektor can optionally apply threshold filtering to prevent
    selection of very weak motives, and can implement various tie-breaking
    strategies when multiple motives have equal strength.
    
    Attributes:
        min_strength_threshold: Minimum strength for a motive to be considered
        tie_break_random: Whether to randomly break ties (vs deterministic)
    """
    
    min_strength_threshold: float = 0.01
    tie_break_random: bool = False
    
    def select_motive(self, candidates: list[Motive]) -> Motive | None:
        """Select the strongest motive from candidates.
        
        This is the core decision function of the motivational system.
        It evaluates all candidate motives using the Expectation × Value
        principle and returns the strongest one.
        
        The selection process:
        1. Calculate strength for each motive
        2. Filter out motives below min_strength_threshold
        3. Return the strongest motive, or None if no valid candidates
        
        Args:
            candidates: List of Motive objects to choose from
            
        Returns:
            The selected Motive, or None if no viable motives
        """
        if not candidates:
            return None
        
        # Calculate strengths and filter
        viable_candidates = []
        for motive in candidates:
            strength = motive.calculate_strength()
            if strength >= self.min_strength_threshold:
                viable_candidates.append((motive, strength))
        
        if not viable_candidates:
            return None
        
        # Find maximum strength
        max_strength = max(strength for _, strength in viable_candidates)
        
        # Get all candidates at max strength (for tie-breaking)
        best_candidates = [
            motive for motive, strength in viable_candidates
            if abs(strength - max_strength) < 1e-9
        ]
        
        # Select winner
        if len(best_candidates) == 1:
            return best_candidates[0]
        elif self.tie_break_random:
            import random
            return random.choice(best_candidates)
        else:
            # Deterministic: return first (most recently added)
            return best_candidates[0]
    
    def rank_motives(self, candidates: list[Motive]) -> list[tuple[Motive, float]]:
        """Rank all motives by strength.
        
        Useful for debugging and for action selection strategies that
        consider multiple options (e.g., planning with fallback).
        
        Args:
            candidates: List of Motive objects to rank
            
        Returns:
            List of (motive, strength) tuples, sorted by strength descending
        """
        ranked = [
            (motive, motive.calculate_strength())
            for motive in candidates
        ]
        ranked.sort(key=lambda x: x[1], reverse=True)
        return ranked
    
    def get_viable_motives(self, candidates: list[Motive]) -> list[Motive]:
        """Get all motives above the minimum strength threshold.
        
        Args:
            candidates: List of Motive objects to filter
            
        Returns:
            List of viable motives (may be empty)
        """
        return [
            motive for motive in candidates
            if motive.calculate_strength() >= self.min_strength_threshold
        ]


# Convenience functions for creating motivators from need systems

def create_motivators_from_system(
    need_system: NeedTankSystem,
    decay_rate: float = 0.1
) -> dict[NeedType, Motivator]:
    """Create a motivator for each need type in a NeedTankSystem.
    
    This convenience function initializes the motivational layer from
    an existing need tank system, creating one motivator per need type.
    
    Args:
        need_system: The NeedTankSystem to create motivators for
        decay_rate: Decay rate for all motivators (default 0.1)
        
    Returns:
        Dictionary mapping NeedType to Motivator
    """
    from .tanks import NeedType
    
    return {
        need_type: Motivator(
            need_type=need_type,
            decay_rate=decay_rate
        )
        for need_type in NeedType
    }


def update_motivators_from_bedarfe(
    motivators: dict[NeedType, Motivator],
    bedarfe: dict[NeedType, float],
    dt: float = 1.0
) -> None:
    """Update all motivators from current bedarf values.
    
    This is the main update function that connects the need system
    (tanks.py) to the motivational system. It should be called
    regularly (e.g., each simulation step).
    
    Args:
        motivators: Dictionary of motivators to update
        bedarfe: Dictionary of current bedarf values from NeedTankSystem
        dt: Time delta for decay calculation
    """
    for need_type, motivator in motivators.items():
        if need_type in bedarfe:
            motivator.accumulate(bedarfe[need_type])
        motivator.decay(dt)
