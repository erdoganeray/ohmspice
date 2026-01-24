"""Oscillator circuit templates.

This module provides ready-to-use oscillator circuit templates including:
- Wien Bridge Oscillator
- Phase Shift Oscillator
- Colpitts Oscillator

Note: These templates provide the passive component networks.
Full oscillator operation requires active components (op-amps, transistors)
which will be added in future versions.

Example:
    >>> from ohmspice.templates import oscillators
    >>> circuit = oscillators.wien_bridge(frequency=1000)
    >>> print(circuit.to_netlist())
"""

import math
from typing import Any

from ohmspice.circuit import Circuit
from ohmspice.components.utils import format_value
from ohmspice.templates.base import CircuitTemplate, TemplateInfo, TemplateParameter


class WienBridgeTemplate(CircuitTemplate):
    """Wien Bridge Oscillator template.

    Classic oscillator using RC network.

    Formula: f = 1 / (2π * R * C)

    The Wien bridge requires R1 = R2 = R and C1 = C2 = C for oscillation.
    """

    @classmethod
    def info(cls) -> TemplateInfo:
        return TemplateInfo(
            name="wien_bridge",
            display_name="Wien Bridge Oscillator",
            description="RC oscillator using Wien bridge network",
            category="oscillators",
            parameters=[
                TemplateParameter("frequency", "Oscillation frequency", "Hz"),
                TemplateParameter("r", "Resistance value", "Ω", required=False, default=10000),
            ],
        )

    def calculate_values(self, **specs: Any) -> dict[str, Any]:
        """Calculate R and C for given frequency.

        Args:
            frequency: Desired oscillation frequency in Hz.
            r: Resistance in Ohms (default 10kΩ).

        Returns:
            Dictionary with 'r' and 'c' values.
        """
        frequency = specs["frequency"]
        r = specs.get("r", 10000)

        # f = 1 / (2π * R * C) => C = 1 / (2π * R * f)
        c = 1 / (2 * math.pi * r * frequency)

        return {"r": r, "c": c}

    def create(self, **params: Any) -> Circuit:
        """Create Wien Bridge Oscillator network.

        Creates the frequency-determining RC network.
        Full oscillator requires additional gain stage.
        """
        frequency = params["frequency"]
        r = params.get("r", 10000)
        include_source = params.get("include_source", True)

        values = self.calculate_values(frequency=frequency, r=r)

        circuit = Circuit(f"Wien Bridge Network ({frequency}Hz)")

        if include_source:
            circuit.add_voltage_source("V1", "in", "0", ac=1)

        # Series RC branch
        circuit.add_resistor("R1", "in", "mid", format_value(values["r"], "R"))
        circuit.add_capacitor("C1", "mid", "out", format_value(values["c"], "C"))

        # Parallel RC branch to ground
        circuit.add_resistor("R2", "out", "0", format_value(values["r"], "R"))
        circuit.add_capacitor("C2", "out", "0", format_value(values["c"], "C"))

        # AC analysis around oscillation frequency
        start_freq = frequency / 10
        stop_freq = frequency * 10
        circuit.add_ac_analysis(start=start_freq, stop=stop_freq, points_per_decade=50)

        return circuit


class PhaseShiftTemplate(CircuitTemplate):
    """Phase Shift Oscillator template.

    Uses 3-stage RC network to produce 180° phase shift.

    Formula: f = 1 / (2π * R * C * √6) for 3-stage
    """

    @classmethod
    def info(cls) -> TemplateInfo:
        return TemplateInfo(
            name="phase_shift",
            display_name="Phase Shift Oscillator",
            description="RC oscillator using 3-stage phase shift network",
            category="oscillators",
            parameters=[
                TemplateParameter("frequency", "Oscillation frequency", "Hz"),
                TemplateParameter("r", "Resistance value", "Ω", required=False, default=10000),
            ],
        )

    def calculate_values(self, **specs: Any) -> dict[str, Any]:
        """Calculate R and C for given frequency.

        Args:
            frequency: Desired oscillation frequency in Hz.
            r: Resistance in Ohms (default 10kΩ).

        Returns:
            Dictionary with 'r' and 'c' values.
        """
        frequency = specs["frequency"]
        r = specs.get("r", 10000)

        # f = 1 / (2π * R * C * √6) => C = 1 / (2π * R * f * √6)
        c = 1 / (2 * math.pi * r * frequency * math.sqrt(6))

        return {"r": r, "c": c}

    def create(self, **params: Any) -> Circuit:
        """Create Phase Shift Oscillator network.

        Creates the 3-stage RC phase shift network.
        Full oscillator requires additional gain stage with gain = 29.
        """
        frequency = params["frequency"]
        r = params.get("r", 10000)
        include_source = params.get("include_source", True)

        values = self.calculate_values(frequency=frequency, r=r)

        circuit = Circuit(f"Phase Shift Network ({frequency}Hz)")

        if include_source:
            circuit.add_voltage_source("V1", "in", "0", ac=1)

        # 3-stage RC network (each stage provides 60° phase shift at fc)
        r_fmt = format_value(values["r"], "R")
        c_fmt = format_value(values["c"], "C")

        # Stage 1
        circuit.add_capacitor("C1", "in", "n1", c_fmt)
        circuit.add_resistor("R1", "n1", "0", r_fmt)

        # Stage 2
        circuit.add_capacitor("C2", "n1", "n2", c_fmt)
        circuit.add_resistor("R2", "n2", "0", r_fmt)

        # Stage 3
        circuit.add_capacitor("C3", "n2", "out", c_fmt)
        circuit.add_resistor("R3", "out", "0", r_fmt)

        start_freq = frequency / 10
        stop_freq = frequency * 10
        circuit.add_ac_analysis(start=start_freq, stop=stop_freq, points_per_decade=50)

        return circuit


class ColpittsTemplate(CircuitTemplate):
    """Colpitts Oscillator template.

    LC oscillator with capacitive voltage divider.

    Formula: f = 1 / (2π * √(L * Ceq)) where Ceq = C1*C2/(C1+C2)
    """

    @classmethod
    def info(cls) -> TemplateInfo:
        return TemplateInfo(
            name="colpitts",
            display_name="Colpitts Oscillator",
            description="LC oscillator with capacitive feedback",
            category="oscillators",
            parameters=[
                TemplateParameter("frequency", "Oscillation frequency", "Hz"),
                TemplateParameter("l", "Inductance value", "H", required=False, default=None),
                TemplateParameter("c_ratio", "C1/C2 ratio", "", required=False, default=1),
            ],
        )

    def calculate_values(self, **specs: Any) -> dict[str, Any]:
        """Calculate L, C1, C2 for given frequency.

        Args:
            frequency: Desired oscillation frequency in Hz.
            l: Inductance in Henries (optional, calculated if not given).
            c_ratio: C1/C2 ratio (default 1).

        Returns:
            Dictionary with 'l', 'c1', 'c2' values.
        """
        frequency = specs["frequency"]
        inductance = specs.get("l")
        c_ratio = specs.get("c_ratio", 1)

        omega = 2 * math.pi * frequency

        if inductance is None:
            # Choose reasonable L value based on frequency
            # For audio, use mH range; for RF, use µH range
            if frequency < 1000:
                inductance = 0.1  # 100mH
            elif frequency < 1e6:
                inductance = 1e-3  # 1mH
            else:
                inductance = 1e-6  # 1µH

        # Ceq = 1 / (ω² * L)
        c_eq = 1 / (omega * omega * inductance)

        # C1*C2/(C1+C2) = Ceq
        # With C1 = ratio * C2:
        # ratio*C2*C2 / ((ratio+1)*C2) = Ceq
        # ratio*C2 / (ratio+1) = Ceq
        # C2 = Ceq * (ratio+1) / ratio
        c2 = c_eq * (c_ratio + 1) / c_ratio
        c1 = c_ratio * c2

        return {"l": inductance, "c1": c1, "c2": c2}

    def create(self, **params: Any) -> Circuit:
        """Create Colpitts Oscillator network.

        Creates the LC tank circuit with capacitive divider.
        Full oscillator requires active device (transistor/FET).
        """
        frequency = params["frequency"]
        inductance = params.get("l")
        c_ratio = params.get("c_ratio", 1)
        include_source = params.get("include_source", True)

        values = self.calculate_values(frequency=frequency, l=inductance, c_ratio=c_ratio)

        circuit = Circuit(f"Colpitts Tank ({frequency}Hz)")

        if include_source:
            circuit.add_voltage_source("V1", "in", "0", ac=1)

        # LC tank with capacitive divider
        circuit.add_inductor("L1", "in", "tap", format_value(values["l"], "L"))
        circuit.add_capacitor("C1", "in", "tap", format_value(values["c1"], "C"))
        circuit.add_capacitor("C2", "tap", "0", format_value(values["c2"], "C"))

        start_freq = frequency / 10
        stop_freq = frequency * 10
        circuit.add_ac_analysis(start=start_freq, stop=stop_freq, points_per_decade=50)

        return circuit


# Template instances
_wien_bridge_template = WienBridgeTemplate()
_phase_shift_template = PhaseShiftTemplate()
_colpitts_template = ColpittsTemplate()


# Factory functions
def wien_bridge(frequency: float, r: float = 10000, include_source: bool = True) -> Circuit:
    """Create a Wien Bridge Oscillator network.

    Args:
        frequency: Oscillation frequency in Hz.
        r: Resistance in Ohms (default 10kΩ).
        include_source: Include AC voltage source (default True).

    Returns:
        Configured Circuit.

    Example:
        >>> circuit = wien_bridge(frequency=1000)
        >>> print(circuit.to_netlist())
    """
    return _wien_bridge_template.create(frequency=frequency, r=r, include_source=include_source)


def phase_shift(frequency: float, r: float = 10000, include_source: bool = True) -> Circuit:
    """Create a Phase Shift Oscillator network.

    Args:
        frequency: Oscillation frequency in Hz.
        r: Resistance in Ohms (default 10kΩ).
        include_source: Include AC voltage source (default True).

    Returns:
        Configured Circuit.

    Example:
        >>> circuit = phase_shift(frequency=1000)
        >>> print(circuit.to_netlist())
    """
    return _phase_shift_template.create(frequency=frequency, r=r, include_source=include_source)


def colpitts(
    frequency: float,
    inductance: float | None = None,
    c_ratio: float = 1,
    include_source: bool = True,
) -> Circuit:
    """Create a Colpitts Oscillator network.

    Args:
        frequency: Oscillation frequency in Hz.
        inductance: Inductance in Henries (optional, auto-calculated based on frequency).
        c_ratio: C1/C2 ratio (default 1 for equal capacitors).
        include_source: Include AC voltage source (default True).

    Returns:
        Configured Circuit.

    Example:
        >>> circuit = colpitts(frequency=1e6)  # 1 MHz oscillator
        >>> print(circuit.to_netlist())
    """
    return _colpitts_template.create(
        frequency=frequency,
        l=inductance,
        c_ratio=c_ratio,
        include_source=include_source,
    )


# Registry
OSCILLATOR_TEMPLATES: dict[str, CircuitTemplate] = {
    "wien_bridge": _wien_bridge_template,
    "phase_shift": _phase_shift_template,
    "colpitts": _colpitts_template,
}


def list_templates() -> list[TemplateInfo]:
    """List all available oscillator templates."""
    return [template.info() for template in OSCILLATOR_TEMPLATES.values()]
