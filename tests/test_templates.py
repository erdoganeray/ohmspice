"""Tests for circuit templates."""

import math

import pytest

from ohmspice.templates import filters, amplifiers, oscillators, power
from ohmspice.templates.base import CircuitTemplate, TemplateInfo, TemplateParameter


class TestTemplateBase:
    """Tests for template base classes."""

    def test_template_info_dataclass(self) -> None:
        """Test TemplateInfo dataclass."""
        info = TemplateInfo(
            name="test_template",
            display_name="Test Template",
            description="A test template",
            category="test",
            parameters=[
                TemplateParameter("param1", "First param", "Hz", required=True),
                TemplateParameter("param2", "Second param", "Ω", required=False, default=1000),
            ],
        )
        assert info.name == "test_template"
        assert info.display_name == "Test Template"
        assert len(info.parameters) == 2
        assert info.parameters[0].required is True
        assert info.parameters[1].default == 1000


class TestFilterTemplates:
    """Tests for filter templates."""

    def test_rc_lowpass_with_r(self) -> None:
        """Test RC low-pass filter with R specified."""
        circuit = filters.rc_lowpass(fc=1000, r=1000)
        assert circuit is not None
        assert "RC Low-Pass Filter" in circuit.name
        netlist = circuit.to_netlist()
        assert "R1" in netlist
        assert "C1" in netlist
        assert ".ac" in netlist

    def test_rc_lowpass_with_c(self) -> None:
        """Test RC low-pass filter with C specified."""
        circuit = filters.rc_lowpass(fc=1000, c=159e-9)
        netlist = circuit.to_netlist()
        assert "R1" in netlist
        assert "C1" in netlist

    def test_rc_lowpass_calculate_values(self) -> None:
        """Test RC low-pass value calculation."""
        template = filters._rc_lowpass_template
        values = template.calculate_values(fc=1000, r=1000)

        # fc = 1/(2π*R*C) => C = 1/(2π*fc*R)
        expected_c = 1 / (2 * math.pi * 1000 * 1000)
        assert values["r"] == 1000
        assert abs(values["c"] - expected_c) < 1e-12

    def test_rc_highpass(self) -> None:
        """Test RC high-pass filter."""
        circuit = filters.rc_highpass(fc=1000, r=1000)
        assert circuit is not None
        netlist = circuit.to_netlist()
        # High-pass: C in series, R to ground
        assert "C1 in" in netlist
        assert "R1 out 0" in netlist

    def test_rlc_bandpass(self) -> None:
        """Test RLC bandpass filter."""
        circuit = filters.rlc_bandpass(fc=1000, q=10, r=100)
        assert circuit is not None
        netlist = circuit.to_netlist()
        assert "R1" in netlist
        assert "L1" in netlist
        assert "C1" in netlist

    def test_rlc_notch(self) -> None:
        """Test RLC notch filter."""
        circuit = filters.rlc_notch(fc=60, q=20, r=100)
        assert circuit is not None
        netlist = circuit.to_netlist()
        assert "R1" in netlist
        assert "L1" in netlist
        assert "C1" in netlist

    def test_filter_templates_list(self) -> None:
        """Test filter template listing."""
        templates = filters.list_templates()
        assert len(templates) >= 4
        names = [t.name for t in templates]
        assert "rc_lowpass" in names
        assert "rc_highpass" in names
        assert "rlc_bandpass" in names
        assert "rlc_notch" in names


class TestAmplifierTemplates:
    """Tests for amplifier templates."""

    def test_inverting_amplifier(self) -> None:
        """Test inverting amplifier."""
        circuit = amplifiers.inverting(gain=10, r_in=10000)
        assert circuit is not None
        assert "Inverting Amplifier" in circuit.name
        netlist = circuit.to_netlist()
        assert "Rin" in netlist
        assert "Rf" in netlist

    def test_inverting_calculate_values(self) -> None:
        """Test inverting amplifier value calculation."""
        template = amplifiers._inverting_template
        values = template.calculate_values(gain=10, r_in=10000)

        # Rf = Gain * Rin
        assert values["r_in"] == 10000
        assert values["r_f"] == 100000  # 10 * 10k
        assert values["gain"] == -10

    def test_noninverting_amplifier(self) -> None:
        """Test non-inverting amplifier."""
        circuit = amplifiers.noninverting(gain=2, r1=10000)
        assert circuit is not None
        netlist = circuit.to_netlist()
        assert "R1" in netlist
        assert "Rf" in netlist

    def test_noninverting_calculate_values(self) -> None:
        """Test non-inverting amplifier value calculation."""
        template = amplifiers._noninverting_template
        values = template.calculate_values(gain=2, r1=10000)

        # Rf = R1 * (Gain - 1)
        assert values["r1"] == 10000
        assert values["r_f"] == 10000  # 10k * (2-1)

    def test_noninverting_invalid_gain(self) -> None:
        """Test non-inverting with invalid gain."""
        template = amplifiers._noninverting_template
        with pytest.raises(ValueError):
            template.calculate_values(gain=0.5, r1=10000)


class TestOscillatorTemplates:
    """Tests for oscillator templates."""

    def test_wien_bridge(self) -> None:
        """Test Wien bridge oscillator network."""
        circuit = oscillators.wien_bridge(frequency=1000, r=10000)
        assert circuit is not None
        netlist = circuit.to_netlist()
        assert "R1" in netlist
        assert "R2" in netlist
        assert "C1" in netlist
        assert "C2" in netlist

    def test_wien_bridge_calculate_values(self) -> None:
        """Test Wien bridge value calculation."""
        template = oscillators._wien_bridge_template
        values = template.calculate_values(frequency=1000, r=10000)

        # f = 1/(2π*R*C) => C = 1/(2π*R*f)
        expected_c = 1 / (2 * math.pi * 10000 * 1000)
        assert values["r"] == 10000
        assert abs(values["c"] - expected_c) < 1e-12

    def test_phase_shift(self) -> None:
        """Test phase shift oscillator network."""
        circuit = oscillators.phase_shift(frequency=1000)
        assert circuit is not None
        netlist = circuit.to_netlist()
        # 3 stages
        assert "R1" in netlist
        assert "R2" in netlist
        assert "R3" in netlist
        assert "C1" in netlist
        assert "C2" in netlist
        assert "C3" in netlist

    def test_colpitts(self) -> None:
        """Test Colpitts oscillator tank."""
        circuit = oscillators.colpitts(frequency=1e6)
        assert circuit is not None
        netlist = circuit.to_netlist()
        assert "L1" in netlist
        assert "C1" in netlist
        assert "C2" in netlist


class TestPowerTemplates:
    """Tests for power circuit templates."""

    def test_voltage_divider(self) -> None:
        """Test voltage divider."""
        circuit = power.voltage_divider(vout=3.3, vin=5, r2=10000)
        assert circuit is not None
        netlist = circuit.to_netlist()
        assert "R1" in netlist
        assert "R2" in netlist
        assert ".op" in netlist

    def test_voltage_divider_calculate_values(self) -> None:
        """Test voltage divider value calculation."""
        template = power._voltage_divider_template
        values = template.calculate_values(vout=5, vin=10, r2=10000)

        # R1 = R2 * (Vin/Vout - 1) = 10k * (10/5 - 1) = 10k
        assert values["r2"] == 10000
        assert values["r1"] == 10000

    def test_voltage_divider_invalid_ratio(self) -> None:
        """Test voltage divider with invalid ratio."""
        template = power._voltage_divider_template
        with pytest.raises(ValueError):
            template.calculate_values(vout=10, vin=5, r2=10000)  # Vout > Vin

    def test_half_wave_rectifier(self) -> None:
        """Test half wave rectifier."""
        circuit = power.half_wave_rectifier(frequency=60, load_r=1000)
        assert circuit is not None
        netlist = circuit.to_netlist()
        assert "Rload" in netlist
        assert "Cfilter" in netlist
        assert ".tran" in netlist

    def test_full_wave_rectifier(self) -> None:
        """Test full wave rectifier."""
        circuit = power.full_wave_rectifier(frequency=60, load_r=1000)
        assert circuit is not None
        netlist = circuit.to_netlist()
        assert "Rload" in netlist


class TestTemplateRegistry:
    """Tests for template registry functions."""

    def test_list_all_templates(self) -> None:
        """Test listing all templates."""
        from ohmspice.templates import list_all_templates

        all_templates = list_all_templates()
        assert "filters" in all_templates
        assert "amplifiers" in all_templates
        assert "oscillators" in all_templates
        assert "power" in all_templates

        # Check counts
        assert len(all_templates["filters"]) >= 4
        assert len(all_templates["amplifiers"]) >= 2
        assert len(all_templates["oscillators"]) >= 3
        assert len(all_templates["power"]) >= 3

    def test_get_template(self) -> None:
        """Test getting template by name."""
        from ohmspice.templates import get_template

        template = get_template("rc_lowpass")
        assert template is not None
        assert isinstance(template, CircuitTemplate)

        template = get_template("voltage_divider")
        assert template is not None

        template = get_template("nonexistent")
        assert template is None
