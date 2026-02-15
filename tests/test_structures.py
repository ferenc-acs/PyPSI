"""Tests for PyPSI core structures."""

import pytest
from pypsi.core import Neuron, Synapse, Schema, Coordinate, ConnectionType


class TestNeuron:
    """Tests for the Neuron class."""
    
    def test_neuron_creation(self):
        """Test basic neuron creation."""
        n = Neuron("test_neuron")
        assert n.name == "test_neuron"
        assert n.activation == 0.0
        assert len(n.outgoing_synapses) == 0
        assert len(n.incoming_synapses) == 0
    
    def test_neuron_activation(self):
        """Test activation methods."""
        n = Neuron("test")
        assert not n.is_active()
        
        n.activate(0.6)
        assert abs(n.activation - 0.6) < 1e-10
        assert n.is_active()
        
        n.deactivate(0.2)
        assert abs(n.activation - 0.4) < 1e-10
        assert not n.is_active()
    
    def test_activation_clamping(self):
        """Test that activation stays within [0, 1]."""
        n = Neuron("test")
        n.activate(2.0)
        assert n.activation == 1.0
        
        n.deactivate(5.0)
        assert n.activation == 0.0
    
    def test_invalid_activation(self):
        """Test that invalid activation raises error."""
        with pytest.raises(ValueError):
            Neuron("test", activation=1.5)
        with pytest.raises(ValueError):
            Neuron("test", activation=-0.1)


class TestSynapse:
    """Tests for the Synapse class."""
    
    def test_synapse_creation(self):
        """Test basic synapse creation."""
        n1 = Neuron("source")
        n2 = Neuron("target")
        syn = Synapse(n1, n2, ConnectionType.POR, 0.8)
        
        assert syn.source == n1
        assert syn.target == n2
        assert syn.connection_type == ConnectionType.POR
        assert syn.strength == 0.8
    
    def test_invalid_strength(self):
        """Test that invalid strength raises error."""
        n1 = Neuron("n1")
        n2 = Neuron("n2")
        with pytest.raises(ValueError):
            Synapse(n1, n2, ConnectionType.POR, 1.5)
        with pytest.raises(ValueError):
            Synapse(n1, n2, ConnectionType.POR, -0.1)
    
    def test_decay(self):
        """Test synapse decay mechanism."""
        n1 = Neuron("n1")
        n2 = Neuron("n2")
        syn = Synapse(n1, n2, ConnectionType.POR, 0.5)
        
        initial = syn.strength
        syn.decay(decay_constant=0.01)
        assert syn.strength < initial
        assert syn.strength >= 0.0
    
    def test_reinforce(self):
        """Test synapse reinforcement mechanism."""
        n1 = Neuron("n1")
        n2 = Neuron("n2")
        syn = Synapse(n1, n2, ConnectionType.POR, 0.5)
        
        initial = syn.strength
        syn.reinforce(reinforcement_value=0.1)
        assert syn.strength > initial
        assert syn.strength <= 1.0
    
    def test_reinforce_capped(self):
        """Test that reinforcement doesn't exceed 1.0."""
        n1 = Neuron("n1")
        n2 = Neuron("n2")
        syn = Synapse(n1, n2, ConnectionType.POR, 0.95)
        
        syn.reinforce(reinforcement_value=0.2)
        assert syn.strength == 1.0


class TestCoordinate:
    """Tests for the Coordinate class."""
    
    def test_coordinate_creation(self):
        """Test basic coordinate creation."""
        c = Coordinate(x=1.0, y=2.0, z=3.0)
        assert c.x == 1.0
        assert c.y == 2.0
        assert c.z == 3.0
    
    def test_default_coordinate(self):
        """Test coordinate with default values."""
        c = Coordinate()
        assert c.x == 0.0
        assert c.y == 0.0
        assert c.z == 0.0
    
    def test_coordinate_addition(self):
        """Test vector addition."""
        c1 = Coordinate(1.0, 2.0, 3.0)
        c2 = Coordinate(4.0, 5.0, 6.0)
        result = c1 + c2
        assert result.x == 5.0
        assert result.y == 7.0
        assert result.z == 9.0
    
    def test_coordinate_subtraction(self):
        """Test vector subtraction."""
        c1 = Coordinate(5.0, 5.0, 5.0)
        c2 = Coordinate(2.0, 3.0, 4.0)
        result = c1 - c2
        assert result.x == 3.0
        assert result.y == 2.0
        assert result.z == 1.0
    
    def test_magnitude(self):
        """Test vector magnitude calculation."""
        c = Coordinate(3.0, 4.0, 0.0)
        assert c.magnitude() == 5.0
        
        c = Coordinate(0.0, 0.0, 0.0)
        assert c.magnitude() == 0.0


class TestSchema:
    """Tests for the Schema class."""
    
    def test_schema_creation(self):
        """Test basic schema creation."""
        s = Schema("test_schema")
        assert s.name == "test_schema"
        assert len(s.interneurons) == 0
        assert len(s.sub_schemata) == 0
        assert len(s.coordinates) == 0
    
    def test_add_interneuron(self):
        """Test adding interneurons to schema."""
        s = Schema("test")
        n1 = Neuron("n1")
        n2 = Neuron("n2")
        
        s.add_interneuron(n1)
        assert len(s.interneurons) == 1
        assert s.interneurons[0] == n1
        
        s.add_interneuron(n2)
        assert len(s.interneurons) == 2
        # Check por/ret links created
        assert len(n1.outgoing_synapses) == 1
        assert len(n2.incoming_synapses) == 1
    
    def test_add_sub_schema(self):
        """Test adding sub-schema (hierarchical structure)."""
        parent = Schema("parent")
        child = Schema("child")
        
        parent_n = Neuron("parent_neuron")
        child_n = Neuron("child_neuron")
        parent.add_interneuron(parent_n)
        child.add_interneuron(child_n)
        
        parent.add_sub_schema("child_ref", child)
        assert "child_ref" in parent.sub_schemata
        # Check sub/sur links created
        assert len(parent_n.outgoing_synapses) == 1
        assert parent_n.outgoing_synapses[0].connection_type == ConnectionType.SUB
    
    def test_schema_coordinates(self):
        """Test coordinate management."""
        s = Schema("test")
        c = Coordinate(1.0, 2.0)
        
        s.set_coordinate("n1", "n2", c)
        retrieved = s.get_coordinate("n1", "n2")
        assert retrieved == c
        
        missing = s.get_coordinate("n2", "n3")
        assert missing is None
    
    def test_schema_activation(self):
        """Test schema activation."""
        s = Schema("test")
        n1 = Neuron("entry")
        n2 = Neuron("next")
        
        s.add_interneuron(n1)
        s.add_interneuron(n2)
        
        s.activate()
        assert n1.activation > 0


class TestNeuronConnections:
    """Tests for neuron connection methods."""
    
    def test_connect_to(self):
        """Test connect_to convenience method."""
        n1 = Neuron("n1")
        n2 = Neuron("n2")
        
        syn = n1.connect_to(n2, ConnectionType.POR, 0.7)
        assert syn in n1.outgoing_synapses
        assert syn in n2.incoming_synapses
        assert syn.connection_type == ConnectionType.POR
        assert syn.strength == 0.7
    
    def test_spread_activation(self):
        """Test activation spreading through synapses."""
        n1 = Neuron("n1", activation=1.0)
        n2 = Neuron("n2")
        
        n1.connect_to(n2, ConnectionType.POR, 1.0)
        n1.spread_activation()
        
        assert n2.activation > 0


class TestConnectionTypes:
    """Tests for ConnectionType enum."""
    
    def test_connection_types_exist(self):
        """Test that all connection types are defined."""
        assert ConnectionType.POR
        assert ConnectionType.RET
        assert ConnectionType.SUB
        assert ConnectionType.SUR
