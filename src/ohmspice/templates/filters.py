"""Filter circuit templates.

This module provides ready-to-use filter circuits including:
- RC Low-Pass Filter
- RC High-Pass Filter
- RLC Bandpass Filter
- RLC Notch Filter
- Butterworth Filter (future)
- Sallen-Key Filter (future)

Example:
    >>> from ohmspice.templates import filters
    >>> circuit = filters.rc_lowpass(fc=1000, r=1000)
    >>> print(circuit.to_netlist())
"""

import math
from typing import Any

from ohmspice.circuit import Circuit
from ohmspice.components.utils import format_value
from ohmspice.templates.base import CircuitTemplate, TemplateInfo, TemplateParameter


class RCLowPassTemplate(CircuitTemplate):
    """RC Low-Pass Filter template.

    A simple first-order low-pass filter using a resistor and capacitor.

    Formula: fc = 1 / (2π * R * C)

    Given fc and either R or C, the other value is calculated.
    If both R and C are given, fc is determined by them.
    """

    @classmethod
    def info(cls) -> TemplateInfo:
        return TemplateInfo(
            name="rc_lowpass",
            display_name="RC Low-Pass Filter",
            description="First-order low-pass filter with -20dB/decade rolloff",
            category="filters",
            parameters=[
                TemplateParameter("fc", "Cutoff frequency (-3dB point)", "Hz"),
                TemplateParameter("r", "Resistance value", "Ω", required=False, default=1000),
                TemplateParameter("c", "Capacitance value", "F", required=False),
            ],
        )

    def calculate_values(self, **specs: Any) -> dict[str, Any]:
        """Calculate R and C values for given cutoff frequency.

        Args:
            fc: Cutoff frequency in Hz.
            r: Resistance in Ohms (optional).
            c: Capacitance in Farads (optional).

        Returns:
            Dictionary with 'r' and 'c' values.

        Raises:
            ValueError: If neither r nor c is specified.
        """
        fc = specs["fc"]
        r = specs.get("r")
        c = specs.get("c")

        if r is not None and c is not None:
            # Both given, ignore fc for values (fc is determined by R and C)
            return {"r": r, "c": c}
        elif r is not None:
            # Calculate C from fc and R
            c = 1 / (2 * math.pi * fc * r)
            return {"r": r, "c": c}
        elif c is not None:
            # Calculate R from fc and C
            r = 1 / (2 * math.pi * fc * c)
            return {"r": r, "c": c}
        else:
            # Default: use R = 1kΩ
            r = 1000
            c = 1 / (2 * math.pi * fc * r)
            return {"r": r, "c": c}

    def create(self, **params: Any) -> Circuit:
        """Create RC Low-Pass Filter circuit.

        Args:
            fc: Cutoff frequency in Hz.
            r: Resistance (optional, default 1kΩ).
            c: Capacitance (optional, calculated from fc and r).
            include_source: Whether to include AC source (default True).

        Returns:
            Configured Circuit with AC analysis.
        """
        fc = params["fc"]
        r = params.get("r")
        c = params.get("c")
        include_source = params.get("include_source", True)

        values = self.calculate_values(fc=fc, r=r, c=c)

        circuit = Circuit(f"RC Low-Pass Filter (fc={fc}Hz)")

        if include_source:
            circuit.add_voltage_source("V1", "in", "0", ac=1)

        circuit.add_resistor("R1", "in", "out", format_value(values["r"], "R"))
        circuit.add_capacitor("C1", "out", "0", format_value(values["c"], "C"))

        # Add AC analysis covering frequencies around fc
        start_freq = fc / 100 if fc > 100 else 1
        stop_freq = fc * 100 if fc * 100 < 1e9 else 1e9
        circuit.add_ac_analysis(start=start_freq, stop=stop_freq, points_per_decade=20)

        return circuit


class RCHighPassTemplate(CircuitTemplate):
    """RC High-Pass Filter template.

    A simple first-order high-pass filter using a capacitor and resistor.

    Formula: fc = 1 / (2π * R * C)

    The capacitor is placed in series, resistor to ground.
    """

    @classmethod
    def info(cls) -> TemplateInfo:
        return TemplateInfo(
            name="rc_highpass",
            display_name="RC High-Pass Filter",
            description="First-order high-pass filter with -20dB/decade rolloff",
            category="filters",
            parameters=[
                TemplateParameter("fc", "Cutoff frequency (-3dB point)", "Hz"),
                TemplateParameter("r", "Resistance value", "Ω", required=False, default=1000),
                TemplateParameter("c", "Capacitance value", "F", required=False),
            ],
        )

    def calculate_values(self, **specs: Any) -> dict[str, Any]:
        """Calculate R and C values for given cutoff frequency."""
        fc = specs["fc"]
        r = specs.get("r")
        c = specs.get("c")

        if r is not None and c is not None:
            return {"r": r, "c": c}
        elif r is not None:
            c = 1 / (2 * math.pi * fc * r)
            return {"r": r, "c": c}
        elif c is not None:
            r = 1 / (2 * math.pi * fc * c)
            return {"r": r, "c": c}
        else:
            r = 1000
            c = 1 / (2 * math.pi * fc * r)
            return {"r": r, "c": c}

    def create(self, **params: Any) -> Circuit:
        """Create RC High-Pass Filter circuit."""
        fc = params["fc"]
        r = params.get("r")
        c = params.get("c")
        include_source = params.get("include_source", True)

        values = self.calculate_values(fc=fc, r=r, c=c)

        circuit = Circuit(f"RC High-Pass Filter (fc={fc}Hz)")

        if include_source:
            circuit.add_voltage_source("V1", "in", "0", ac=1)

        # High-pass: C in series, R to ground
        circuit.add_capacitor("C1", "in", "out", format_value(values["c"], "C"))
        circuit.add_resistor("R1", "out", "0", format_value(values["r"], "R"))

        start_freq = fc / 100 if fc > 100 else 1
        stop_freq = fc * 100 if fc * 100 < 1e9 else 1e9
        circuit.add_ac_analysis(start=start_freq, stop=stop_freq, points_per_decade=20)

        return circuit


class RLCBandpassTemplate(CircuitTemplate):
    """RLC Bandpass Filter template.

    A second-order bandpass filter using R, L, and C in series.

    Formulas:
        - Center frequency: fc = 1 / (2π * √(L*C))
        - Quality factor: Q = (1/R) * √(L/C)
        - Bandwidth: BW = fc / Q
    """

    @classmethod
    def info(cls) -> TemplateInfo:
        return TemplateInfo(
            name="rlc_bandpass",
            display_name="RLC Bandpass Filter",
            description="Second-order bandpass filter with series RLC",
            category="filters",
            parameters=[
                TemplateParameter("fc", "Center frequency", "Hz"),
                TemplateParameter("q", "Quality factor", "", required=False, default=10),
                TemplateParameter("r", "Resistance value", "Ω", required=False, default=100),
            ],
        )

    def calculate_values(self, **specs: Any) -> dict[str, Any]:
        """Calculate R, L, C values for given fc and Q.

        Args:
            fc: Center frequency in Hz.
            q: Quality factor.
            r: Resistance in Ohms.

        Returns:
            Dictionary with 'r', 'l', 'c' values.
        """
        fc = specs["fc"]
        q = specs.get("q", 10)
        r = specs.get("r", 100)

        # From formulas:
        # fc = 1 / (2π * √(LC))  =>  LC = 1 / (2π*fc)²
        # Q = (1/R) * √(L/C)  =>  √(L/C) = Q*R  =>  L/C = (Q*R)²
        #
        # Let LC = K where K = 1 / (2π*fc)²
        # and L/C = M where M = (Q*R)²
        # Then: L = √(K*M) and C = √(K/M)

        omega = 2 * math.pi * fc
        lc_product = 1 / (omega * omega)  # LC = 1/(ω²)
        l_over_c = (q * r) ** 2  # L/C = (QR)²

        inductance = math.sqrt(lc_product * l_over_c)
        c = math.sqrt(lc_product / l_over_c)

        return {"r": r, "l": inductance, "c": c}

    def create(self, **params: Any) -> Circuit:
        """Create RLC Bandpass Filter circuit."""
        fc = params["fc"]
        q = params.get("q", 10)
        r = params.get("r", 100)
        include_source = params.get("include_source", True)

        values = self.calculate_values(fc=fc, q=q, r=r)

        circuit = Circuit(f"RLC Bandpass Filter (fc={fc}Hz, Q={q})")

        if include_source:
            circuit.add_voltage_source("V1", "in", "0", ac=1)

        # Series RLC configuration
        circuit.add_resistor("R1", "in", "node1", format_value(values["r"], "R"))
        circuit.add_inductor("L1", "node1", "out", format_value(values["l"], "L"))
        circuit.add_capacitor("C1", "out", "0", format_value(values["c"], "C"))

        # Analysis range based on bandwidth
        bw = fc / q
        start_freq = max(1, fc - 5 * bw)
        stop_freq = fc + 5 * bw
        circuit.add_ac_analysis(start=start_freq, stop=stop_freq, points_per_decade=50)

        return circuit


class RLCNotchTemplate(CircuitTemplate):
    """RLC Notch (Band-Stop) Filter template.

    A notch filter that attenuates frequencies around the center frequency.
    Uses parallel LC tank circuit.
    """

    @classmethod
    def info(cls) -> TemplateInfo:
        return TemplateInfo(
            name="rlc_notch",
            display_name="RLC Notch Filter",
            description="Second-order notch (band-stop) filter",
            category="filters",
            parameters=[
                TemplateParameter("fc", "Notch frequency", "Hz"),
                TemplateParameter("q", "Quality factor", "", required=False, default=10),
                TemplateParameter("r", "Resistance value", "Ω", required=False, default=100),
            ],
        )

    def calculate_values(self, **specs: Any) -> dict[str, Any]:
        """Calculate R, L, C values for given fc and Q."""
        fc = specs["fc"]
        q = specs.get("q", 10)
        r = specs.get("r", 100)

        omega = 2 * math.pi * fc
        lc_product = 1 / (omega * omega)

        # For notch: Q = R / √(L/C)
        l_over_c = (r / q) ** 2
        inductance = math.sqrt(lc_product * l_over_c)
        c = math.sqrt(lc_product / l_over_c)

        return {"r": r, "l": inductance, "c": c}

    def create(self, **params: Any) -> Circuit:
        """Create RLC Notch Filter circuit."""
        fc = params["fc"]
        q = params.get("q", 10)
        r = params.get("r", 100)
        include_source = params.get("include_source", True)

        values = self.calculate_values(fc=fc, q=q, r=r)

        circuit = Circuit(f"RLC Notch Filter (fc={fc}Hz, Q={q})")

        if include_source:
            circuit.add_voltage_source("V1", "in", "0", ac=1)

        # Series R with parallel LC to ground
        circuit.add_resistor("R1", "in", "out", format_value(values["r"], "R"))
        circuit.add_inductor("L1", "out", "0", format_value(values["l"], "L"))
        circuit.add_capacitor("C1", "out", "0", format_value(values["c"], "C"))

        bw = fc / q
        start_freq = max(1, fc - 5 * bw)
        stop_freq = fc + 5 * bw
        circuit.add_ac_analysis(start=start_freq, stop=stop_freq, points_per_decade=50)

        return circuit


# Template instances for factory functions
_rc_lowpass_template = RCLowPassTemplate()
_rc_highpass_template = RCHighPassTemplate()
_rlc_bandpass_template = RLCBandpassTemplate()
_rlc_notch_template = RLCNotchTemplate()


# Factory functions (convenient API)
def rc_lowpass(
    fc: float, r: float | None = None, c: float | None = None, include_source: bool = True
) -> Circuit:
    """Create an RC Low-Pass Filter.

    Args:
        fc: Cutoff frequency in Hz.
        r: Resistance in Ohms (optional, default 1kΩ).
        c: Capacitance in Farads (optional, calculated from fc and r).
        include_source: Include AC voltage source (default True).

    Returns:
        Configured Circuit with AC analysis.

    Example:
        >>> circuit = rc_lowpass(fc=1000, r=1000)
        >>> print(circuit.to_netlist())
    """
    return _rc_lowpass_template.create(fc=fc, r=r, c=c, include_source=include_source)


def rc_highpass(
    fc: float, r: float | None = None, c: float | None = None, include_source: bool = True
) -> Circuit:
    """Create an RC High-Pass Filter.

    Args:
        fc: Cutoff frequency in Hz.
        r: Resistance in Ohms (optional, default 1kΩ).
        c: Capacitance in Farads (optional, calculated from fc and r).
        include_source: Include AC voltage source (default True).

    Returns:
        Configured Circuit with AC analysis.

    Example:
        >>> circuit = rc_highpass(fc=1000, r=1000)
        >>> print(circuit.to_netlist())
    """
    return _rc_highpass_template.create(fc=fc, r=r, c=c, include_source=include_source)


def rlc_bandpass(fc: float, q: float = 10, r: float = 100, include_source: bool = True) -> Circuit:
    """Create an RLC Bandpass Filter.

    Args:
        fc: Center frequency in Hz.
        q: Quality factor (default 10).
        r: Resistance in Ohms (default 100Ω).
        include_source: Include AC voltage source (default True).

    Returns:
        Configured Circuit with AC analysis.

    Example:
        >>> circuit = rlc_bandpass(fc=1000, q=10)
        >>> print(circuit.to_netlist())
    """
    return _rlc_bandpass_template.create(fc=fc, q=q, r=r, include_source=include_source)


def rlc_notch(fc: float, q: float = 10, r: float = 100, include_source: bool = True) -> Circuit:
    """Create an RLC Notch (Band-Stop) Filter.

    Args:
        fc: Notch frequency in Hz.
        q: Quality factor (default 10).
        r: Resistance in Ohms (default 100Ω).
        include_source: Include AC voltage source (default True).

    Returns:
        Configured Circuit with AC analysis.

    Example:
        >>> circuit = rlc_notch(fc=60, q=20)  # 60Hz hum filter
        >>> print(circuit.to_netlist())
    """
    return _rlc_notch_template.create(fc=fc, q=q, r=r, include_source=include_source)


# Registry of all filter templates
FILTER_TEMPLATES: dict[str, CircuitTemplate] = {
    "rc_lowpass": _rc_lowpass_template,
    "rc_highpass": _rc_highpass_template,
    "rlc_bandpass": _rlc_bandpass_template,
    "rlc_notch": _rlc_notch_template,
}


def list_templates() -> list[TemplateInfo]:
    """List all available filter templates.

    Returns:
        List of TemplateInfo for each filter template.
    """
    return [template.info() for template in FILTER_TEMPLATES.values()]
