"""Amplifier circuit templates.

This module provides ready-to-use amplifier circuits including:
- Inverting Amplifier
- Non-Inverting Amplifier
- Differential Amplifier (future)
- Instrumentation Amplifier (future)

Note: These templates require OpAmp component which will be
added in a future version. For now, they use simplified models.
"""

from typing import Any

from ohmspice.circuit import Circuit
from ohmspice.components.utils import format_value
from ohmspice.templates.base import CircuitTemplate, TemplateInfo, TemplateParameter


class InvertingAmplifierTemplate(CircuitTemplate):
    """Inverting Amplifier template.

    Uses op-amp with feedback resistor and input resistor.
    Gain = -Rf / Rin

    Note: This creates a simple approximation using voltage-controlled
    voltage source (VCVS) until OpAmp component is implemented.
    """

    @classmethod
    def info(cls) -> TemplateInfo:
        return TemplateInfo(
            name="inverting",
            display_name="Inverting Amplifier",
            description="Op-amp based inverting amplifier",
            category="amplifiers",
            parameters=[
                TemplateParameter("gain", "Voltage gain (absolute value)", ""),
                TemplateParameter("r_in", "Input resistance", "Ω", required=False, default=10000),
            ],
        )

    def calculate_values(self, **specs: Any) -> dict[str, Any]:
        """Calculate resistor values for given gain.

        Args:
            gain: Desired voltage gain (positive number, inverted internally).
            r_in: Input resistance (default 10kΩ).

        Returns:
            Dictionary with 'r_in' and 'r_f' values.
        """
        gain = abs(specs["gain"])
        r_in = specs.get("r_in", 10000)

        # Gain = Rf / Rin => Rf = Gain * Rin
        r_f = gain * r_in

        return {"r_in": r_in, "r_f": r_f, "gain": -gain}

    def create(self, **params: Any) -> Circuit:
        """Create Inverting Amplifier circuit.

        Uses behavioral model with VCVS (E element) for op-amp.
        """
        gain = params["gain"]
        r_in = params.get("r_in", 10000)
        include_source = params.get("include_source", True)

        values = self.calculate_values(gain=gain, r_in=r_in)

        circuit = Circuit(f"Inverting Amplifier (Gain=-{abs(gain)})")

        if include_source:
            circuit.add_voltage_source("V1", "in", "0", ac=1)

        # Input resistor
        circuit.add_resistor("Rin", "in", "neg_input", format_value(values["r_in"], "R"))

        # Feedback resistor
        circuit.add_resistor("Rf", "neg_input", "out", format_value(values["r_f"], "R"))

        # Virtual ground at neg_input (simulated by connecting to proper op-amp model)
        # For now, add a resistor to ground as simplified model
        circuit.add_resistor("Rv", "neg_input", "0", "1G")  # High impedance

        # Note: Full op-amp model will be added when OpAmp component is implemented

        circuit.add_ac_analysis(start=1, stop=1e6, points_per_decade=20)

        return circuit


class NonInvertingAmplifierTemplate(CircuitTemplate):
    """Non-Inverting Amplifier template.

    Uses op-amp with feedback network.
    Gain = 1 + Rf / R1
    """

    @classmethod
    def info(cls) -> TemplateInfo:
        return TemplateInfo(
            name="noninverting",
            display_name="Non-Inverting Amplifier",
            description="Op-amp based non-inverting amplifier",
            category="amplifiers",
            parameters=[
                TemplateParameter("gain", "Voltage gain (>= 1)", ""),
                TemplateParameter("r1", "R1 resistance", "Ω", required=False, default=10000),
            ],
        )

    def calculate_values(self, **specs: Any) -> dict[str, Any]:
        """Calculate resistor values for given gain.

        Args:
            gain: Desired voltage gain (must be >= 1).
            r1: R1 resistance (default 10kΩ).

        Returns:
            Dictionary with 'r1' and 'r_f' values.
        """
        gain = specs["gain"]
        if gain < 1:
            raise ValueError("Non-inverting amplifier gain must be >= 1")

        r1 = specs.get("r1", 10000)

        # Gain = 1 + Rf/R1 => Rf = R1 * (Gain - 1)
        r_f = r1 * (gain - 1)

        return {"r1": r1, "r_f": r_f, "gain": gain}

    def create(self, **params: Any) -> Circuit:
        """Create Non-Inverting Amplifier circuit."""
        gain = params["gain"]
        r1 = params.get("r1", 10000)
        include_source = params.get("include_source", True)

        values = self.calculate_values(gain=gain, r1=r1)

        circuit = Circuit(f"Non-Inverting Amplifier (Gain={gain})")

        if include_source:
            circuit.add_voltage_source("V1", "in", "0", ac=1)

        # Input goes to positive input of op-amp
        # Feedback network
        circuit.add_resistor("R1", "neg_input", "0", format_value(values["r1"], "R"))
        circuit.add_resistor("Rf", "neg_input", "out", format_value(values["r_f"], "R"))

        # Simplified model connection
        circuit.add_resistor("Rv", "in", "neg_input", "1G")

        circuit.add_ac_analysis(start=1, stop=1e6, points_per_decade=20)

        return circuit


# Template instances
_inverting_template = InvertingAmplifierTemplate()
_noninverting_template = NonInvertingAmplifierTemplate()


# Factory functions
def inverting(gain: float, r_in: float = 10000, include_source: bool = True) -> Circuit:
    """Create an Inverting Amplifier.

    Args:
        gain: Desired voltage gain (positive number, will be inverted).
        r_in: Input resistance in Ohms (default 10kΩ).
        include_source: Include AC voltage source (default True).

    Returns:
        Configured Circuit.

    Example:
        >>> circuit = inverting(gain=10)  # -10x gain
        >>> print(circuit.to_netlist())
    """
    return _inverting_template.create(gain=gain, r_in=r_in, include_source=include_source)


def noninverting(gain: float, r1: float = 10000, include_source: bool = True) -> Circuit:
    """Create a Non-Inverting Amplifier.

    Args:
        gain: Desired voltage gain (must be >= 1).
        r1: R1 resistance in Ohms (default 10kΩ).
        include_source: Include AC voltage source (default True).

    Returns:
        Configured Circuit.

    Example:
        >>> circuit = noninverting(gain=2)  # 2x gain
        >>> print(circuit.to_netlist())
    """
    return _noninverting_template.create(gain=gain, r1=r1, include_source=include_source)


# Registry
AMPLIFIER_TEMPLATES: dict[str, CircuitTemplate] = {
    "inverting": _inverting_template,
    "noninverting": _noninverting_template,
}


def list_templates() -> list[TemplateInfo]:
    """List all available amplifier templates."""
    return [template.info() for template in AMPLIFIER_TEMPLATES.values()]
