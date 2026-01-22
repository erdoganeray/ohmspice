"""Tests for Circuit class."""

import pytest

from ohmspice import Circuit


class TestCircuitCreation:
    """Tests for circuit creation."""

    def test_create_circuit(self):
        circuit = Circuit("Test Circuit")
        assert circuit.name == "Test Circuit"
        assert len(circuit.components) == 0
        assert len(circuit.analyses) == 0

    def test_repr(self):
        circuit = Circuit("Test")
        assert "Circuit" in repr(circuit)
        assert "Test" in repr(circuit)


class TestAddComponents:
    """Tests for adding components."""

    def test_add_resistor(self):
        circuit = Circuit("Test")
        circuit.add_resistor("R1", "in", "out", "1k")
        assert len(circuit) == 1
        assert circuit.components[0].name == "R1"

    def test_add_capacitor(self):
        circuit = Circuit("Test")
        circuit.add_capacitor("C1", "out", "0", "100n")
        assert len(circuit) == 1

    def test_add_inductor(self):
        circuit = Circuit("Test")
        circuit.add_inductor("L1", "in", "out", "10m")
        assert len(circuit) == 1

    def test_add_voltage_source(self):
        circuit = Circuit("Test")
        circuit.add_voltage_source("V1", "in", "0", ac=1)
        assert len(circuit) == 1

    def test_add_current_source(self):
        circuit = Circuit("Test")
        circuit.add_current_source("I1", "in", "0", dc=0.001)
        assert len(circuit) == 1

    def test_method_chaining(self):
        circuit = (
            Circuit("Test")
            .add_resistor("R1", "in", "out", "1k")
            .add_capacitor("C1", "out", "0", "100n")
        )
        assert len(circuit) == 2

    def test_duplicate_name_raises(self):
        circuit = Circuit("Test")
        circuit.add_resistor("R1", "in", "out", "1k")
        with pytest.raises(ValueError, match="already exists"):
            circuit.add_resistor("R1", "a", "b", "2k")


class TestAnalysis:
    """Tests for analysis commands."""

    def test_add_ac_analysis(self):
        circuit = Circuit("Test")
        circuit.add_ac_analysis(start=1, stop=1e6, points_per_decade=10)
        assert len(circuit.analyses) == 1
        assert ".ac" in circuit.analyses[0]

    def test_add_dc_analysis(self):
        circuit = Circuit("Test")
        circuit.add_dc_analysis("V1", 0, 10, 0.1)
        assert len(circuit.analyses) == 1
        assert ".dc" in circuit.analyses[0]

    def test_add_transient_analysis(self):
        circuit = Circuit("Test")
        circuit.add_transient_analysis(stop_time=1e-3)
        assert len(circuit.analyses) == 1
        assert ".tran" in circuit.analyses[0]

    def test_add_op_analysis(self):
        circuit = Circuit("Test")
        circuit.add_op_analysis()
        assert ".op" in circuit.analyses[0]


class TestNetlistGeneration:
    """Tests for netlist generation."""

    def test_basic_netlist(self):
        circuit = Circuit("RC Filter")
        circuit.add_voltage_source("V1", "in", "0", ac=1)
        circuit.add_resistor("R1", "in", "out", "1k")
        circuit.add_capacitor("C1", "out", "0", "159n")
        circuit.add_ac_analysis(start=1, stop=1e6)

        netlist = circuit.to_netlist()

        assert "* RC Filter" in netlist
        assert "V1 in 0 AC 1" in netlist
        assert "R1 in out 1k" in netlist
        assert "C1 out 0 159n" in netlist
        assert ".ac" in netlist
        assert ".end" in netlist

    def test_netlist_ends_with_end(self):
        circuit = Circuit("Test")
        netlist = circuit.to_netlist()
        assert netlist.strip().endswith(".end")

    def test_save_netlist(self, tmp_path):
        circuit = Circuit("Test")
        circuit.add_resistor("R1", "a", "b", "1k")

        filepath = tmp_path / "test.cir"
        circuit.save(str(filepath))

        assert filepath.exists()
        content = filepath.read_text()
        assert "R1 a b 1k" in content


class TestRCLowPassFilter:
    """Integration test for RC low-pass filter example."""

    def test_complete_rc_filter(self):
        """Test the complete RC low-pass filter from README."""
        circuit = Circuit("RC Low-Pass Filter")
        circuit.add_voltage_source("V1", "in", "0", ac=1)
        circuit.add_resistor("R1", "in", "out", "1k")
        circuit.add_capacitor("C1", "out", "0", "159n")
        circuit.add_ac_analysis(start=1, stop=1e6, points_per_decade=10)

        netlist = circuit.to_netlist()

        # Verify structure
        lines = netlist.strip().split("\n")
        assert lines[0] == "* RC Low-Pass Filter"
        assert lines[-1] == ".end"

        # Verify components present
        assert any("V1" in line for line in lines)
        assert any("R1" in line for line in lines)
        assert any("C1" in line for line in lines)
        assert any(".ac" in line for line in lines)
