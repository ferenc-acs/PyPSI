"""Tests for PyPSI need tanks, motivators, and emotional modulation."""

import math

import pytest

from pypsi.emotion.modulation import EmotionalState
from pypsi.needs import Motivator, NeedTank, NeedType


class TestNeedTankSpike:
    """Tests for the NeedTank U-signal spike mechanism."""

    def test_spike_forces_critical(self):
        """Spike should empty the tank and make it critical."""
        tank = NeedTank(need_type=NeedType.HUNGER, current_level=1.0, critical_threshold=0.2)

        tank.spike()

        assert tank.current_level == 0.0
        assert tank.is_critical()
        assert tank.bedarf() == pytest.approx(tank.target_level)


class TestEmotionalState:
    """Tests for EmotionalState modulation."""

    def test_arousal_modulates_resolution_and_threshold(self):
        """Arousal should map to resolution and selection threshold."""
        state = EmotionalState(arousal=0.0)

        assert state.resolution_level == pytest.approx(state.max_resolution)
        assert state.selection_threshold == pytest.approx(state.min_selection_threshold)

        state.set_arousal(1.0)
        assert state.resolution_level == pytest.approx(state.min_resolution)
        assert state.selection_threshold == pytest.approx(state.max_selection_threshold)


class TestMotivatorLogAccumulation:
    """Tests for logarithmic motivator pressure accumulation."""

    def test_log_pressure_accumulates_over_time(self):
        """Pressure should accumulate as log(1 + bedarf) over time."""
        motivator = Motivator(
            need_type=NeedType.HUNGER,
            decay_rate=0.0,
            max_pressure=10.0
        )

        motivator.accumulate(1.0, dt=1.0)
        first_pressure = motivator.accumulated_pressure

        expected_gain = math.log1p(1.0)
        assert first_pressure == pytest.approx(expected_gain)

        motivator.accumulate(1.0, dt=1.0)
        assert motivator.accumulated_pressure == pytest.approx(first_pressure + expected_gain)
        assert motivator.get_activity() == pytest.approx(motivator.accumulated_pressure)
