"""Power circuit templates.

This module provides ready-to-use power circuit templates including:
- Voltage Divider
- Half Wave Rectifier
- Full Wave Rectifier

Example:
    >>> from ohmspice.templates import power
    >>> circuit = power.voltage_divider(vout=5, vin=12)
    >>> print(circuit.to_netlist())
"""

from typing import Any

from ohmspice.circuit import Circuit
from ohmspice.components.utils import format_value
from ohmspice.templates.base import CircuitTemplate, TemplateInfo, TemplateParameter


class VoltageDividerTemplate(CircuitTemplate):
    """Voltage Divider template.

    A simple resistive voltage divider circuit.

    Formula: Vout = Vin * R2 / (R1 + R2)

    Given Vout/Vin ratio and R2 (or total resistance), R1 is calculated.
    """

    @classmethod
    def info(cls) -> TemplateInfo:
        return TemplateInfo(
            name="voltage_divider",
            display_name="Voltage Divider",
            description="Resistive voltage divider",
            category="power",
            parameters=[
                TemplateParameter("vout", "Output voltage", "V"),
                TemplateParameter("vin", "Input voltage", "V"),
                TemplateParameter(
                    "r2", "R2 (bottom) resistance", "Ω", required=False, default=10000
                ),
            ],
        )

    def calculate_values(self, **specs: Any) -> dict[str, Any]:
        """Calculate R1 and R2 for given voltage ratio.

        Args:
            vout: Desired output voltage.
            vin: Input voltage.
            r2: Bottom resistor value (default 10kΩ).

        Returns:
            Dictionary with 'r1' and 'r2' values.
        """
        vout = specs["vout"]
        vin = specs["vin"]
        r2 = specs.get("r2", 10000)

        if vout >= vin:
            raise ValueError("Vout must be less than Vin for voltage divider")

        # Vout/Vin = R2/(R1+R2)
        # R1 = R2 * (Vin/Vout - 1)
        ratio = vin / vout
        r1 = r2 * (ratio - 1)

        return {"r1": r1, "r2": r2}

    def create(self, **params: Any) -> Circuit:
        """Create Voltage Divider circuit."""
        vout = params["vout"]
        vin = params["vin"]
        r2 = params.get("r2", 10000)
        include_source = params.get("include_source", True)

        values = self.calculate_values(vout=vout, vin=vin, r2=r2)

        circuit = Circuit(f"Voltage Divider ({vin}V to {vout}V)")

        if include_source:
            circuit.add_voltage_source("V1", "in", "0", dc=vin)

        circuit.add_resistor("R1", "in", "out", format_value(values["r1"], "R"))
        circuit.add_resistor("R2", "out", "0", format_value(values["r2"], "R"))

        # DC analysis to verify divider ratio
        circuit.add_op_analysis()

        return circuit


class HalfWaveRectifierTemplate(CircuitTemplate):
    """Half Wave Rectifier template.

    Simple half-wave rectifier with optional filter capacitor.

    Note: Requires Diode component which will be added in future version.
    Current implementation uses simplified behavioral model.
    """

    @classmethod
    def info(cls) -> TemplateInfo:
        return TemplateInfo(
            name="half_wave_rectifier",
            display_name="Half Wave Rectifier",
            description="Simple half-wave rectifier with filter cap",
            category="power",
            parameters=[
                TemplateParameter(
                    "frequency", "AC input frequency", "Hz", required=False, default=60
                ),
                TemplateParameter("load_r", "Load resistance", "Ω", required=False, default=1000),
                TemplateParameter(
                    "filter_c", "Filter capacitor", "F", required=False, default=None
                ),
            ],
        )

    def calculate_values(self, **specs: Any) -> dict[str, Any]:
        """Calculate component values.

        Args:
            frequency: AC input frequency (default 60Hz).
            load_r: Load resistance (default 1kΩ).
            filter_c: Filter capacitor (optional).

        Returns:
            Dictionary with component values.
        """
        frequency = specs.get("frequency", 60)
        load_r = specs.get("load_r", 1000)
        filter_c = specs.get("filter_c")

        # If no filter cap specified, calculate for 10% ripple
        if filter_c is None:
            # Ripple voltage ≈ I/(f*C) => C = I/(f*Vripple)
            # For 10% ripple at 1V output: C = I/(f*0.1)
            filter_c = 1 / (frequency * load_r * 0.1)

        return {
            "frequency": frequency,
            "load_r": load_r,
            "filter_c": filter_c,
        }

    def create(self, **params: Any) -> Circuit:
        """Create Half Wave Rectifier circuit.

        Note: Uses simplified model until Diode component is available.
        """
        frequency = params.get("frequency", 60)
        load_r = params.get("load_r", 1000)
        filter_c = params.get("filter_c")
        include_source = params.get("include_source", True)

        values = self.calculate_values(frequency=frequency, load_r=load_r, filter_c=filter_c)

        circuit = Circuit(f"Half Wave Rectifier ({frequency}Hz)")

        if include_source:
            # AC sine source
            circuit.add_voltage_source(
                "V1", "in", "0", sine={"offset": 0, "amplitude": 10, "frequency": frequency}
            )

        # TODO: Add diode when Diode component is implemented
        # For now, just add load and filter
        circuit.add_resistor("Rload", "out", "0", format_value(values["load_r"], "R"))

        if values["filter_c"]:
            circuit.add_capacitor("Cfilter", "out", "0", format_value(values["filter_c"], "C"))

        # Transient analysis for a few cycles
        stop_time = 5 / frequency  # 5 cycles
        circuit.add_transient_analysis(stop_time=stop_time)

        return circuit


class FullWaveRectifierTemplate(CircuitTemplate):
    """Full Wave Rectifier template.

    Full-wave bridge rectifier with optional filter capacitor.

    Note: Requires Diode component which will be added in future version.
    """

    @classmethod
    def info(cls) -> TemplateInfo:
        return TemplateInfo(
            name="full_wave_rectifier",
            display_name="Full Wave Rectifier",
            description="Full-wave bridge rectifier with filter cap",
            category="power",
            parameters=[
                TemplateParameter(
                    "frequency", "AC input frequency", "Hz", required=False, default=60
                ),
                TemplateParameter("load_r", "Load resistance", "Ω", required=False, default=1000),
                TemplateParameter(
                    "filter_c", "Filter capacitor", "F", required=False, default=None
                ),
            ],
        )

    def calculate_values(self, **specs: Any) -> dict[str, Any]:
        """Calculate component values."""
        frequency = specs.get("frequency", 60)
        load_r = specs.get("load_r", 1000)
        filter_c = specs.get("filter_c")

        # Full-wave has twice the fundamental frequency
        if filter_c is None:
            filter_c = 1 / (2 * frequency * load_r * 0.1)

        return {
            "frequency": frequency,
            "load_r": load_r,
            "filter_c": filter_c,
        }

    def create(self, **params: Any) -> Circuit:
        """Create Full Wave Rectifier circuit."""
        frequency = params.get("frequency", 60)
        load_r = params.get("load_r", 1000)
        filter_c = params.get("filter_c")
        include_source = params.get("include_source", True)

        values = self.calculate_values(frequency=frequency, load_r=load_r, filter_c=filter_c)

        circuit = Circuit(f"Full Wave Rectifier ({frequency}Hz)")

        if include_source:
            circuit.add_voltage_source(
                "V1", "in", "0", sine={"offset": 0, "amplitude": 10, "frequency": frequency}
            )

        # TODO: Add diode bridge when Diode component is implemented
        circuit.add_resistor("Rload", "out", "0", format_value(values["load_r"], "R"))

        if values["filter_c"]:
            circuit.add_capacitor("Cfilter", "out", "0", format_value(values["filter_c"], "C"))

        stop_time = 5 / frequency
        circuit.add_transient_analysis(stop_time=stop_time)

        return circuit


# Template instances
_voltage_divider_template = VoltageDividerTemplate()
_half_wave_rectifier_template = HalfWaveRectifierTemplate()
_full_wave_rectifier_template = FullWaveRectifierTemplate()


# Factory functions
def voltage_divider(
    vout: float, vin: float, r2: float = 10000, include_source: bool = True
) -> Circuit:
    """Create a Voltage Divider.

    Args:
        vout: Desired output voltage.
        vin: Input voltage.
        r2: Bottom resistor in Ohms (default 10kΩ).
        include_source: Include DC voltage source (default True).

    Returns:
        Configured Circuit.

    Example:
        >>> circuit = voltage_divider(vout=3.3, vin=5)
        >>> print(circuit.to_netlist())
    """
    return _voltage_divider_template.create(
        vout=vout, vin=vin, r2=r2, include_source=include_source
    )


def half_wave_rectifier(
    frequency: float = 60,
    load_r: float = 1000,
    filter_c: float | None = None,
    include_source: bool = True,
) -> Circuit:
    """Create a Half Wave Rectifier.

    Args:
        frequency: AC input frequency in Hz (default 60Hz).
        load_r: Load resistance in Ohms (default 1kΩ).
        filter_c: Filter capacitor in Farads (optional, auto-calculated for 10% ripple).
        include_source: Include AC voltage source (default True).

    Returns:
        Configured Circuit.
    """
    return _half_wave_rectifier_template.create(
        frequency=frequency, load_r=load_r, filter_c=filter_c, include_source=include_source
    )


def full_wave_rectifier(
    frequency: float = 60,
    load_r: float = 1000,
    filter_c: float | None = None,
    include_source: bool = True,
) -> Circuit:
    """Create a Full Wave Rectifier.

    Args:
        frequency: AC input frequency in Hz (default 60Hz).
        load_r: Load resistance in Ohms (default 1kΩ).
        filter_c: Filter capacitor in Farads (optional, auto-calculated for 10% ripple).
        include_source: Include AC voltage source (default True).

    Returns:
        Configured Circuit.
    """
    return _full_wave_rectifier_template.create(
        frequency=frequency, load_r=load_r, filter_c=filter_c, include_source=include_source
    )


# Registry
POWER_TEMPLATES: dict[str, CircuitTemplate] = {
    "voltage_divider": _voltage_divider_template,
    "half_wave_rectifier": _half_wave_rectifier_template,
    "full_wave_rectifier": _full_wave_rectifier_template,
}


def list_templates() -> list[TemplateInfo]:
    """List all available power templates."""
    return [template.info() for template in POWER_TEMPLATES.values()]
