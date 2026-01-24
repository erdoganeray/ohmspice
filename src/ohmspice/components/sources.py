"""Source components: VoltageSource, CurrentSource."""

from ohmspice.components.base import Component


class VoltageSource(Component):
    """A voltage source component.

    Supports DC, AC, Pulse, and Sine waveforms.

    SPICE format examples:
        DC:    Vname n+ n- DC value
        AC:    Vname n+ n- AC magnitude [phase]
        PULSE: Vname n+ n- PULSE(v1 v2 td tr tf pw per)
        SINE:  Vname n+ n- SINE(vo va freq [td] [theta])

    Example:
        >>> v1 = VoltageSource("V1", "in", "0", dc=5)
        >>> v1.to_spice()
        'V1 in 0 DC 5'

        >>> v2 = VoltageSource("V2", "in", "0", ac=1)
        >>> v2.to_spice()
        'V2 in 0 AC 1'

        >>> v3 = VoltageSource("V3", "in", "0", dc=0, ac=1, ac_phase=0)
        >>> v3.to_spice()
        'V3 in 0 DC 0 AC 1 0'
    """

    PREFIX = "V"

    def __init__(
        self,
        name: str,
        node_pos: str,
        node_neg: str,
        *,
        dc: float | None = None,
        ac: float | None = None,
        ac_phase: float = 0,
        pulse: dict | None = None,
        sine: dict | None = None,
    ) -> None:
        """Create a voltage source.

        Args:
            name: Source name (must start with 'V').
            node_pos: Positive node.
            node_neg: Negative node.
            dc: DC voltage value.
            ac: AC magnitude for AC analysis.
            ac_phase: AC phase in degrees (default 0).
            pulse: Pulse parameters dict with keys:
                - v1: Initial value
                - v2: Pulsed value
                - td: Delay time (default 0)
                - tr: Rise time (default 0)
                - tf: Fall time (default 0)
                - pw: Pulse width
                - per: Period
            sine: Sine parameters dict with keys:
                - vo: DC offset
                - va: Amplitude
                - freq: Frequency in Hz
                - td: Delay time (default 0)
                - theta: Damping factor (default 0)

        Raises:
            ValueError: If name doesn't start with 'V' or no source type specified.
        """
        super().__init__(name, node_pos, node_neg)

        if not name.upper().startswith("V"):
            raise ValueError(f"Voltage source name must start with 'V', got '{name}'")

        self.dc = dc
        self.ac = ac
        self.ac_phase = ac_phase
        self.pulse = pulse
        self.sine = sine

        # Validate that at least one source type is specified
        if all(x is None for x in [dc, ac, pulse, sine]):
            raise ValueError("At least one source type (dc, ac, pulse, sine) must be specified")

    def to_spice(self) -> str:
        """Generate SPICE netlist line."""
        parts = [self.name, self.node1, self.node2]

        # DC value
        if self.dc is not None:
            parts.append(f"DC {self.dc}")

        # AC value
        if self.ac is not None:
            if self.ac_phase != 0:
                parts.append(f"AC {self.ac} {self.ac_phase}")
            else:
                parts.append(f"AC {self.ac}")

        # Pulse waveform
        if self.pulse is not None:
            p = self.pulse
            pulse_str = (
                f"PULSE({p.get('v1', 0)} {p.get('v2', 0)} "
                f"{p.get('td', 0)} {p.get('tr', 0)} {p.get('tf', 0)} "
                f"{p.get('pw', 0)} {p.get('per', 0)})"
            )
            parts.append(pulse_str)

        # Sine waveform
        if self.sine is not None:
            s = self.sine
            sine_str = f"SINE({s.get('vo', 0)} {s.get('va', 0)} {s.get('freq', 0)}"
            if s.get("td", 0) != 0 or s.get("theta", 0) != 0:
                sine_str += f" {s.get('td', 0)} {s.get('theta', 0)}"
            sine_str += ")"
            parts.append(sine_str)

        return " ".join(parts)

    def __repr__(self) -> str:
        """Return string representation."""
        params = []
        if self.dc is not None:
            params.append(f"dc={self.dc}")
        if self.ac is not None:
            params.append(f"ac={self.ac}")
        if self.pulse is not None:
            params.append(f"pulse={self.pulse}")
        if self.sine is not None:
            params.append(f"sine={self.sine}")
        params_str = ", ".join(params)
        return f"VoltageSource({self.name!r}, {self.node1!r}, {self.node2!r}, {params_str})"


class CurrentSource(Component):
    """A current source component.

    Supports DC and AC current sources.

    SPICE format: Iname n+ n- [DC value] [AC magnitude [phase]]

    Example:
        >>> i1 = CurrentSource("I1", "in", "0", dc=1e-3)
        >>> i1.to_spice()
        'I1 in 0 DC 0.001'
    """

    PREFIX = "I"

    def __init__(
        self,
        name: str,
        node_pos: str,
        node_neg: str,
        *,
        dc: float | None = None,
        ac: float | None = None,
        ac_phase: float = 0,
    ) -> None:
        """Create a current source.

        Args:
            name: Source name (must start with 'I').
            node_pos: Positive node (current flows from pos to neg).
            node_neg: Negative node.
            dc: DC current value in amperes.
            ac: AC magnitude for AC analysis.
            ac_phase: AC phase in degrees (default 0).

        Raises:
            ValueError: If name doesn't start with 'I' or no source type specified.
        """
        super().__init__(name, node_pos, node_neg)

        if not name.upper().startswith("I"):
            raise ValueError(f"Current source name must start with 'I', got '{name}'")

        self.dc = dc
        self.ac = ac
        self.ac_phase = ac_phase

        if dc is None and ac is None:
            raise ValueError("At least one source type (dc, ac) must be specified")

    def to_spice(self) -> str:
        """Generate SPICE netlist line."""
        parts = [self.name, self.node1, self.node2]

        if self.dc is not None:
            parts.append(f"DC {self.dc}")

        if self.ac is not None:
            if self.ac_phase != 0:
                parts.append(f"AC {self.ac} {self.ac_phase}")
            else:
                parts.append(f"AC {self.ac}")

        return " ".join(parts)

    def __repr__(self) -> str:
        """Return string representation."""
        params = []
        if self.dc is not None:
            params.append(f"dc={self.dc}")
        if self.ac is not None:
            params.append(f"ac={self.ac}")
        params_str = ", ".join(params)
        return f"CurrentSource({self.name!r}, {self.node1!r}, {self.node2!r}, {params_str})"
