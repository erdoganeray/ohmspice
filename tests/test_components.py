"""Tests for component classes."""

import pytest

from ohmspice.components import (
    Capacitor,
    Component,
    CurrentSource,
    Inductor,
    Resistor,
    VoltageSource,
    format_value,
    parse_value,
)


class TestParseValue:
    """Tests for value parsing utility."""

    def test_parse_integer(self):
        assert parse_value(1000) == 1000.0

    def test_parse_float(self):
        assert parse_value(1.5) == 1.5

    def test_parse_string_no_suffix(self):
        assert parse_value("1000") == 1000.0

    def test_parse_kilo(self):
        assert parse_value("1k") == 1000.0
        assert parse_value("4.7k") == 4700.0

    def test_parse_mega(self):
        assert parse_value("1meg") == 1e6
        assert parse_value("4.7meg") == 4.7e6

    def test_parse_nano(self):
        assert parse_value("100n") == pytest.approx(1e-7)
        assert parse_value("159n") == pytest.approx(159e-9)

    def test_parse_micro(self):
        assert parse_value("10u") == pytest.approx(1e-5)
        assert parse_value("4.7u") == pytest.approx(4.7e-6)

    def test_parse_pico(self):
        assert parse_value("100p") == 1e-10

    def test_parse_milli(self):
        assert parse_value("10m") == 0.01

    def test_parse_case_insensitive(self):
        assert parse_value("1K") == 1000.0
        assert parse_value("1MEG") == 1e6

    def test_parse_empty_raises(self):
        with pytest.raises(ValueError):
            parse_value("")

    def test_parse_invalid_raises(self):
        with pytest.raises(ValueError):
            parse_value("abc")


class TestFormatValue:
    """Tests for value formatting utility."""

    def test_format_kilo(self):
        assert format_value(1000) == "1k"
        assert format_value(4700) == "4.7k"

    def test_format_mega(self):
        assert format_value(1e6) == "1meg"

    def test_format_nano(self):
        result = format_value(1e-9)
        assert "n" in result or "1e-09" in result

    def test_format_with_unit(self):
        result = format_value(1e-9, "F")
        assert "F" in result

    def test_format_zero(self):
        assert format_value(0) == "0"


class TestResistor:
    """Tests for Resistor component."""

    def test_create_with_string_value(self):
        r = Resistor("R1", "in", "out", "1k")
        assert r.name == "R1"
        assert r.node1 == "in"
        assert r.node2 == "out"
        assert r.value == 1000.0
        assert r.value_str == "1k"

    def test_create_with_numeric_value(self):
        r = Resistor("R1", "in", "out", 1000)
        assert r.value == 1000.0

    def test_to_spice(self):
        r = Resistor("R1", "in", "out", "1k")
        assert r.to_spice() == "R1 in out 1k"

    def test_gnd_normalized(self):
        r = Resistor("R1", "in", "gnd", "1k")
        assert r.node2 == "0"

    def test_invalid_name_raises(self):
        with pytest.raises(ValueError, match="must start with 'R'"):
            Resistor("C1", "in", "out", "1k")

    def test_repr(self):
        r = Resistor("R1", "in", "out", "1k")
        assert "Resistor" in repr(r)
        assert "R1" in repr(r)


class TestCapacitor:
    """Tests for Capacitor component."""

    def test_create(self):
        c = Capacitor("C1", "out", "0", "100n")
        assert c.name == "C1"
        assert c.value == pytest.approx(1e-7)

    def test_to_spice(self):
        c = Capacitor("C1", "out", "0", "100n")
        assert c.to_spice() == "C1 out 0 100n"

    def test_with_initial_condition(self):
        c = Capacitor("C1", "out", "0", "100n", initial_voltage=5.0)
        assert c.to_spice() == "C1 out 0 100n IC=5.0"

    def test_invalid_name_raises(self):
        with pytest.raises(ValueError, match="must start with 'C'"):
            Capacitor("R1", "out", "0", "100n")


class TestInductor:
    """Tests for Inductor component."""

    def test_create(self):
        l = Inductor("L1", "in", "out", "10m")
        assert l.name == "L1"
        assert l.value == 0.01

    def test_to_spice(self):
        l = Inductor("L1", "in", "out", "10m")
        assert l.to_spice() == "L1 in out 10m"

    def test_with_initial_condition(self):
        l = Inductor("L1", "in", "out", "10m", initial_current=0.1)
        assert "IC=0.1" in l.to_spice()


class TestVoltageSource:
    """Tests for VoltageSource component."""

    def test_create_dc(self):
        v = VoltageSource("V1", "in", "0", dc=5)
        assert v.dc == 5
        assert "DC 5" in v.to_spice()

    def test_create_ac(self):
        v = VoltageSource("V1", "in", "0", ac=1)
        assert v.ac == 1
        assert "AC 1" in v.to_spice()

    def test_create_dc_ac(self):
        v = VoltageSource("V1", "in", "0", dc=0, ac=1)
        spice = v.to_spice()
        assert "DC 0" in spice
        assert "AC 1" in spice

    def test_create_ac_with_phase(self):
        v = VoltageSource("V1", "in", "0", ac=1, ac_phase=90)
        assert "AC 1 90" in v.to_spice()

    def test_create_pulse(self):
        v = VoltageSource("V1", "in", "0", pulse={"v1": 0, "v2": 5, "pw": 1e-3, "per": 2e-3})
        assert "PULSE(" in v.to_spice()

    def test_create_sine(self):
        v = VoltageSource("V1", "in", "0", sine={"vo": 0, "va": 1, "freq": 1000})
        assert "SINE(" in v.to_spice()

    def test_invalid_name_raises(self):
        with pytest.raises(ValueError, match="must start with 'V'"):
            VoltageSource("I1", "in", "0", dc=5)

    def test_no_source_type_raises(self):
        with pytest.raises(ValueError, match="At least one source type"):
            VoltageSource("V1", "in", "0")


class TestCurrentSource:
    """Tests for CurrentSource component."""

    def test_create_dc(self):
        i = CurrentSource("I1", "in", "0", dc=0.001)
        assert i.dc == 0.001
        assert "DC 0.001" in i.to_spice()

    def test_create_ac(self):
        i = CurrentSource("I1", "in", "0", ac=1e-3)
        assert "AC 0.001" in i.to_spice()

    def test_invalid_name_raises(self):
        with pytest.raises(ValueError, match="must start with 'I'"):
            CurrentSource("V1", "in", "0", dc=0.001)
