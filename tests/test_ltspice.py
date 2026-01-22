"""Tests for LTspice simulator backend."""

import pytest

from ohmspice import Circuit
from ohmspice.simulators import LTSpice
from ohmspice.simulators.base import SimulatorNotFoundError


class TestLTSpiceDetection:
    """Tests for LTspice detection."""

    def test_is_available(self):
        """Check if LTspice availability detection works."""
        # This should not raise an error
        available = LTSpice.is_available()
        assert isinstance(available, bool)

    def test_find_executable(self):
        """Check if executable finding works."""
        path = LTSpice.find_executable()
        # Path can be None if LTspice not installed
        assert path is None or path.exists()

    @pytest.mark.skipif(not LTSpice.is_available(), reason="LTspice not installed")
    def test_create_instance(self):
        """Test creating LTspice instance when available."""
        sim = LTSpice()
        assert sim.executable.exists()


class TestLTSpiceNotAvailable:
    """Tests when LTspice is not available."""

    @pytest.mark.skipif(LTSpice.is_available(), reason="LTspice is installed")
    def test_create_raises_when_not_available(self):
        """Test that creating LTspice raises error when not installed."""
        with pytest.raises(SimulatorNotFoundError):
            LTSpice()


@pytest.mark.skipif(not LTSpice.is_available(), reason="LTspice not installed")
class TestLTSpiceSimulation:
    """Integration tests for LTspice simulation.

    These tests only run if LTspice is installed.
    """

    def test_run_simple_circuit(self):
        """Test running a simple RC circuit simulation."""
        circuit = Circuit("Test RC")
        circuit.add_voltage_source("V1", "in", "0", ac=1)
        circuit.add_resistor("R1", "in", "out", "1k")
        circuit.add_capacitor("C1", "out", "0", "159n")
        circuit.add_ac_analysis(start=1, stop=1e6, points_per_decade=10)

        sim = LTSpice()
        results = sim.run(circuit)

        # Check results
        assert results is not None
        freq = results.get_frequency()
        assert len(freq) > 0

    def test_run_netlist_file(self, tmp_path):
        """Test running simulation from netlist file."""
        circuit = Circuit("Test")
        circuit.add_voltage_source("V1", "in", "0", dc=5)
        circuit.add_resistor("R1", "in", "out", "1k")
        circuit.add_resistor("R2", "out", "0", "1k")
        circuit.add_op_analysis()

        netlist_path = tmp_path / "test.cir"
        circuit.save(str(netlist_path))

        sim = LTSpice()
        results = sim.run_netlist(netlist_path)

        assert results is not None

    def test_run_nonexistent_file_raises(self):
        """Test that running non-existent file raises error."""
        sim = LTSpice()
        with pytest.raises(FileNotFoundError):
            sim.run_netlist("nonexistent.cir")
