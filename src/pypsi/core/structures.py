"""Core data structures for PyPSI - PSI Theory cognitive architecture.

This module implements the fundamental building blocks of PSI Theory:
- Neuron: Basic computational nodes
- Synapse: Connections between neurons (por/ret, sub/sur)
- Schema: Hierarchical memory structures composed of neuron chains

Based on:
    Dörner, D., Schaub, H., & Detje, F. (1999/2001). Das Leben von Ψ
    Institut für Theoretische Psychologie, Universität Bamberg
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any


class ConnectionType(Enum):
    """Types of synaptic connections in PSI Theory.
    
    PSI Theory uses two primary connection types:
    - por/ret: Sequential/chain connections (forward/backward)
    - sub/sur: Hierarchical connections (part/whole)
    """
    POR = auto()  #: Forward connection (German: "por" - sequential forward)
    RET = auto()  #: Backward connection (German: "ret" - sequential backward)
    SUB = auto()  #: Part/child connection (German: "sub" - subordinate)
    SUR = auto()  #: Whole/parent connection (German: "sur" - superordinate)


@dataclass
class Coordinate:
    """Spatial coordinates for interneuron links in sensory schemata.
    
    In PSI Theory, links between interneurons include spatial coordinates
    that represent motor commands for shifting attention (e.g., eye movements).
    A coordinate like [0, 3] means "move focus 3 units up."
    """
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    
    def __add__(self, other: Coordinate) -> Coordinate:
        """Add two coordinates (vector addition)."""
        return Coordinate(x=self.x + other.x, y=self.y + other.y, z=self.z + other.z)
    
    def __sub__(self, other: Coordinate) -> Coordinate:
        """Subtract two coordinates (vector subtraction)."""
        return Coordinate(x=self.x - other.x, y=self.y - other.y, z=self.z - other.z)
    
    def magnitude(self) -> float:
        """Calculate Euclidean magnitude of this coordinate vector."""
        return (self.x ** 2 + self.y ** 2 + self.z ** 2) ** 0.5


@dataclass
class Neuron:
    """Basic computational unit in the PSI cognitive architecture.
    
    Neurons ("Interknoten" or interneurons) are the fundamental building 
    blocks of all memory structures. They represent concepts, percepts, 
    actions, and situations in a unified format.
    
    Attributes:
        name: Human-readable identifier for this neuron
        id: Unique identifier (auto-generated if not provided)
        activation: Current activation level (0.0 to 1.0)
        outgoing_synapses: List of outgoing connections (por/sub)
        incoming_synapses: List of incoming connections (ret/sur)
        metadata: Additional data associated with this neuron
    """
    name: str
    id: str = field(default_factory=lambda: f"n_{id(Neuron)}")
    activation: float = 0.0
    outgoing_synapses: list[Synapse] = field(default_factory=list)
    incoming_synapses: list[Synapse] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    
    _id_counter: int = 0
    
    def __post_init__(self) -> None:
        """Generate unique ID if default was used."""
        if self.id.startswith("n_") and self.id == f"n_{id(Neuron)}":
            Neuron._id_counter += 1
            object.__setattr__(self, 'id', f"{self.name}_{Neuron._id_counter}")
        if not 0.0 <= self.activation <= 1.0:
            raise ValueError(f"Activation must be in [0.0, 1.0], got {self.activation}")
    
    def is_active(self, threshold: float = 0.5) -> bool:
        """Check if neuron exceeds activation threshold."""
        return self.activation >= threshold
    
    def activate(self, amount: float = 1.0) -> None:
        """Increase activation level (clamped to [0, 1])."""
        self.activation = min(1.0, self.activation + amount)
    
    def deactivate(self, amount: float = 0.1) -> None:
        """Decrease activation level (clamped to [0, 1])."""
        self.activation = max(0.0, self.activation - amount)
    
    def add_outgoing_synapse(self, synapse: Synapse) -> None:
        """Add an outgoing synapse and register with target."""
        if synapse.source is not self:
            raise ValueError("Synapse source must be this neuron")
        self.outgoing_synapses.append(synapse)
        synapse.target.incoming_synapses.append(synapse)
    
    def add_incoming_synapse(self, synapse: Synapse) -> None:
        """Add an incoming synapse and register with source."""
        if synapse.target is not self:
            raise ValueError("Synapse target must be this neuron")
        self.incoming_synapses.append(synapse)
        synapse.source.outgoing_synapses.append(synapse)
    
    def connect_to(self, target: Neuron, connection_type: ConnectionType, strength: float = 0.5) -> Synapse:
        """Create a synapse from this neuron to target."""
        synapse = Synapse(self, target, connection_type, strength)
        self.add_outgoing_synapse(synapse)
        return synapse
    
    def spread_activation(self) -> None:
        """Spread activation to connected neurons via outgoing synapses."""
        for synapse in self.outgoing_synapses:
            if synapse.strength > 0:
                spread_amount = self.activation * synapse.strength * 0.5
                synapse.target.activate(spread_amount)


@dataclass
class Synapse:
    """A connection between two neurons in the PSI network.
    
    Synapses form the structural basis of all memory in PSI Theory.
    They connect neurons in sequential chains (por/ret) and hierarchical
    structures (sub/sur).
    
    Attributes:
        source: The originating neuron
        target: The destination neuron
        connection_type: Type of connection (POR, RET, SUB, SUR)
        strength: Connection weight (0.0 to 1.0)
    """
    source: Neuron
    target: Neuron
    connection_type: ConnectionType
    strength: float = 0.5
    
    def __post_init__(self) -> None:
        """Validate synapse parameters after initialization."""
        if not 0.0 <= self.strength <= 1.0:
            raise ValueError(f"Strength must be in [0.0, 1.0], got {self.strength}")
    
    def decay(self, decay_constant: float = 0.01) -> None:
        """Apply PSI Theory decay formula: s := sqrt(s^2 - Z)"""
        new_strength_sq = max(0.0, self.strength ** 2 - decay_constant)
        self.strength = new_strength_sq ** 0.5
    
    def reinforce(self, reinforcement_value: float = 0.1) -> None:
        """Apply PSI Theory reinforcement formula: s := s + V"""
        self.strength = min(1.0, self.strength + reinforcement_value)


@dataclass
class Schema:
    """Hierarchical memory structure composed of interneuron chains.
    
    Schemata are the universal memory format in PSI Theory. They can
    represent sensory patterns, action sequences, episodes, and concepts.
    
    A schema consists of a chain of interneurons connected by por/ret
    links (sequential) with optional sub/sur links to component schemata.
    
    Attributes:
        name: Human-readable identifier for this schema
        id: Unique identifier
        interneurons: Ordered list of neurons forming the chain
        sub_schemata: Component schemata (connected via sub/sur links)
        coordinates: Spatial coordinates for interneuron links
        metadata: Additional data
    """
    name: str
    id: str = field(default_factory=lambda: f"s_{id(Schema)}")
    interneurons: list[Neuron] = field(default_factory=list)
    sub_schemata: dict[str, Schema] = field(default_factory=dict)
    coordinates: dict[tuple[str, str], Coordinate] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    
    _id_counter: int = 0
    
    def __post_init__(self) -> None:
        """Generate unique ID if default was used."""
        if self.id.startswith("s_") and self.id == f"s_{id(Schema)}":
            Schema._id_counter += 1
            object.__setattr__(self, 'id', f"{self.name}_{Schema._id_counter}")
    
    def add_interneuron(self, neuron: Neuron) -> None:
        """Add a neuron to the end of this schema's chain."""
        if self.interneurons:
            prev = self.interneurons[-1]
            prev.connect_to(neuron, ConnectionType.POR)
            neuron.connect_to(prev, ConnectionType.RET)
        self.interneurons.append(neuron)
    
    def add_sub_schema(self, name: str, schema: Schema) -> None:
        """Add a component schema (sub/sur relationship)."""
        self.sub_schemata[name] = schema
        if self.interneurons and schema.interneurons:
            parent_neuron = self.interneurons[0]
            child_neuron = schema.interneurons[0]
            parent_neuron.connect_to(child_neuron, ConnectionType.SUB)
            child_neuron.connect_to(parent_neuron, ConnectionType.SUR)
    
    def set_coordinate(self, from_neuron: str, to_neuron: str, coord: Coordinate) -> None:
        """Set spatial coordinate for a link between two neurons."""
        self.coordinates[(from_neuron, to_neuron)] = coord
    
    def get_coordinate(self, from_neuron: str, to_neuron: str) -> Coordinate | None:
        """Get coordinate for link between two neurons."""
        return self.coordinates.get((from_neuron, to_neuron))
    
    def activate(self) -> None:
        """Activate the first interneuron (entry point)."""
        if self.interneurons:
            self.interneurons[0].activate(1.0)
            self.interneurons[0].spread_activation()
    
    def get_active_neurons(self, threshold: float = 0.5) -> list[Neuron]:
        """Get all currently active neurons in this schema."""
        return [n for n in self.interneurons if n.is_active(threshold)]
