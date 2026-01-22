"""Tests for netlist generation."""

import pytest

from ohmspice import Circuit, NetlistGenerator


class TestNetlistGenerator:
    """Tests for NetlistGenerator class."""

    def test_generate(self):
        circuit = Circuit("Test")
        circuit.add_resistor("R1", "a", "b", "1k")

        generator = NetlistGenerator()
        netlist = generator.generate(circuit)

        assert "* Test" in netlist
        assert "R1 a b 1k" in netlist
        assert ".end" in netlist

    def test_save(self, tmp_path):
        circuit = Circuit("Test")
        circuit.add_resistor("R1", "a", "b", "1k")

        generator = NetlistGenerator()
        filepath = generator.save(circuit, tmp_path / "test")

        # Should add .cir extension
        assert filepath.suffix == ".cir"
        assert filepath.exists()

    def test_save_with_extension(self, tmp_path):
        circuit = Circuit("Test")
        circuit.add_resistor("R1", "a", "b", "1k")

        generator = NetlistGenerator()
        filepath = generator.save(circuit, tmp_path / "test.net")

        # Should keep .net extension
        assert filepath.suffix == ".net"

    def test_save_creates_directories(self, tmp_path):
        circuit = Circuit("Test")
        circuit.add_resistor("R1", "a", "b", "1k")

        generator = NetlistGenerator()
        filepath = generator.save(circuit, tmp_path / "subdir" / "test.cir")

        assert filepath.exists()
        assert filepath.parent.name == "subdir"
