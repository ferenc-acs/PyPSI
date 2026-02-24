# PyPSI Package Layout

This folder contains the Python implementation of PSI Theory. The structure below reflects what is implemented today and what is planned next.

## Subpackages
- `core/`: Core PSI structures (Neuron, Synapse, Schema, Coordinate).
- `needs/`: Need tanks, motivators, motives, and motive selection.
- `emotion/`: Emotional modulation (`EmotionalState`) derived from arousal.
- `action/`: Action schemas and the action library.
- `perception/`: Perception system and sensory memory.
- `environment/`: Grid-based island world and percept definitions.
- `memory/`: Reserved for protocol/unified memory and decay (not implemented yet).
- `gui/`: Reserved for a Pygame UI module (not implemented yet).

## Top-Level Exports
- `__init__.py` re-exports key classes for convenience (needs, emotion, core structures, and environment types).
