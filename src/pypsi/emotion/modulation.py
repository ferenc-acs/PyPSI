"""Emotional modulation for PyPSI - PSI Theory cognitive architecture.

This module implements emotional modulation parameters that adjust
processing scope and action selection based on arousal/activation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Self


@dataclass
class EmotionalState:
    """Represents emotional modulation of processing and selection.

    PSI Theory links arousal/activation to two control parameters:
    - **Resolution Level**: Scope of processing (high arousal narrows scope)
    - **Selection Threshold**: Pickiness in action selection (high arousal increases selectivity)

    Both parameters are computed as linear functions of arousal between
    configurable bounds.
    """

    arousal: float = 0.5
    min_resolution: float = 0.2
    max_resolution: float = 1.0
    min_selection_threshold: float = 0.1
    max_selection_threshold: float = 0.9

    def __post_init__(self) -> None:
        """Validate emotional state parameters."""
        if not 0.0 <= self.arousal <= 1.0:
            raise ValueError(f"arousal must be in [0.0, 1.0], got {self.arousal}")
        if not 0.0 <= self.min_resolution <= 1.0:
            raise ValueError(
                f"min_resolution must be in [0.0, 1.0], got {self.min_resolution}"
            )
        if not 0.0 <= self.max_resolution <= 1.0:
            raise ValueError(
                f"max_resolution must be in [0.0, 1.0], got {self.max_resolution}"
            )
        if self.min_resolution > self.max_resolution:
            raise ValueError(
                "min_resolution must be <= max_resolution, "
                f"got {self.min_resolution} > {self.max_resolution}"
            )
        if not 0.0 <= self.min_selection_threshold <= 1.0:
            raise ValueError(
                "min_selection_threshold must be in [0.0, 1.0], "
                f"got {self.min_selection_threshold}"
            )
        if not 0.0 <= self.max_selection_threshold <= 1.0:
            raise ValueError(
                "max_selection_threshold must be in [0.0, 1.0], "
                f"got {self.max_selection_threshold}"
            )
        if self.min_selection_threshold > self.max_selection_threshold:
            raise ValueError(
                "min_selection_threshold must be <= max_selection_threshold, "
                f"got {self.min_selection_threshold} > {self.max_selection_threshold}"
            )

    @staticmethod
    def _clamp(value: float, min_value: float = 0.0, max_value: float = 1.0) -> float:
        """Clamp a value into a range."""
        return max(min_value, min(max_value, value))

    def set_arousal(self, arousal: float) -> Self:
        """Set arousal/activation level (clamped to [0, 1])."""
        self.arousal = self._clamp(arousal)
        return self

    def adjust_arousal(self, delta: float) -> Self:
        """Adjust arousal by a delta (clamped to [0, 1])."""
        return self.set_arousal(self.arousal + delta)

    @property
    def activation_level(self) -> float:
        """Alias for arousal/activation level."""
        return self.arousal

    @property
    def resolution_level(self) -> float:
        """Compute resolution level from arousal.

        Higher arousal narrows processing scope, reducing resolution.
        """
        arousal = self._clamp(self.arousal)
        return self.max_resolution - (self.max_resolution - self.min_resolution) * arousal

    @property
    def selection_threshold(self) -> float:
        """Compute selection threshold from arousal.

        Higher arousal increases selectivity (higher threshold).
        """
        arousal = self._clamp(self.arousal)
        return (
            self.min_selection_threshold
            + (self.max_selection_threshold - self.min_selection_threshold) * arousal
        )

    def __repr__(self) -> str:
        """String representation showing modulation state."""
        return (
            "EmotionalState("
            f"arousal={self.arousal:.3f}, "
            f"resolution={self.resolution_level:.3f}, "
            f"selection_threshold={self.selection_threshold:.3f})"
        )
