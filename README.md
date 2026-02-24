# PyPsi - PSI Theory Implementation in Python

A modern Python port of Dietrich Dörner's PSI cognitive architecture, focused on need-driven behavior, perception/action loops, and a runnable island demo.

## Overview

PSI (Ψ) is a unified theory of cognition, emotion, and motivation that explains complex behavior through simple, interacting mechanisms. This repository ports the original 2003 Delphi codebase to modern Python and includes a Pygame visualization demo.

![PyPSI Cognitive Architecture](docs/images/2026-02-24-pypsi-cognitive-architecture.png)

*The six need tanks (Hunger, Thirst, Energy, Certainty, Competence, Affiliation) connected by neural pathways, with emotional modulation.*

## Quick Start

```bash
# Install dependencies
uv sync

# Run tests
uv run pytest

# Run example
uv run python examples/simple_island.py
```

## Architecture

See [PROJECT_PLAN.md](PROJECT_PLAN.md) and [STATUS.md](STATUS.md) for the current architecture and implementation status. For module layout, see `src/pypsi/README.md`.

## License

MIT
