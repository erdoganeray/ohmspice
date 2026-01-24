"""Circuit builder for creating SPICE circuits."""

from ohmspice.components.base import Component
from ohmspice.components.passive import Capacitor, Inductor, Resistor
from ohmspice.components.sources import CurrentSource, VoltageSource


class Circuit:
    """A SPICE circuit builder.

    This class provides a fluent API for building SPICE circuits by
    adding components and analysis commands.

    Example:
        >>> circuit = Circuit("RC Low-Pass Filter")
        >>> circuit.add_voltage_source("V1", "in", "0", ac=1)
        >>> circuit.add_resistor("R1", "in", "out", "1k")
        >>> circuit.add_capacitor("C1", "out", "0", "159n")
        >>> circuit.add_ac_analysis(start=1, stop=1e6, points_per_decade=10)
        >>> print(circuit.to_netlist())
        * RC Low-Pass Filter
        V1 in 0 AC 1
        R1 in out 1k
        C1 out 0 159n
        .ac dec 10 1 1meg
        .end

    Attributes:
        name: Circuit name (appears as comment in netlist).
        components: List of components in the circuit.
        analyses: List of analysis commands.
    """

    def __init__(self, name: str) -> None:
        """Create a new circuit.

        Args:
            name: Circuit name/title.
        """
        self.name = name
        self.components: list[Component] = []
        self.analyses: list[str] = []
        self._component_names: set[str] = set()

    def _add_component(self, component: Component) -> "Circuit":
        """Add a component to the circuit.

        Args:
            component: The component to add.

        Returns:
            Self for method chaining.

        Raises:
            ValueError: If a component with the same name already exists.
        """
        if component.name in self._component_names:
            raise ValueError(f"Component '{component.name}' already exists in circuit")

        self.components.append(component)
        self._component_names.add(component.name)
        return self

    def add_resistor(
        self,
        name: str,
        node1: str,
        node2: str,
        value: str | int | float,
    ) -> "Circuit":
        """Add a resistor to the circuit.

        Args:
            name: Resistor name (must start with 'R').
            node1: First connection node.
            node2: Second connection node.
            value: Resistance value (e.g., '1k', 1000, '4.7meg').

        Returns:
            Self for method chaining.
        """
        return self._add_component(Resistor(name, node1, node2, value))

    def add_capacitor(
        self,
        name: str,
        node1: str,
        node2: str,
        value: str | int | float,
        initial_voltage: float | None = None,
    ) -> "Circuit":
        """Add a capacitor to the circuit.

        Args:
            name: Capacitor name (must start with 'C').
            node1: Positive node.
            node2: Negative node.
            value: Capacitance value (e.g., '100n', '10u').
            initial_voltage: Optional initial voltage.

        Returns:
            Self for method chaining.
        """
        return self._add_component(Capacitor(name, node1, node2, value, initial_voltage))

    def add_inductor(
        self,
        name: str,
        node1: str,
        node2: str,
        value: str | int | float,
        initial_current: float | None = None,
    ) -> "Circuit":
        """Add an inductor to the circuit.

        Args:
            name: Inductor name (must start with 'L').
            node1: First node.
            node2: Second node.
            value: Inductance value (e.g., '10m', '100u').
            initial_current: Optional initial current.

        Returns:
            Self for method chaining.
        """
        return self._add_component(Inductor(name, node1, node2, value, initial_current))

    def add_voltage_source(
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
    ) -> "Circuit":
        """Add a voltage source to the circuit.

        Args:
            name: Source name (must start with 'V').
            node_pos: Positive node.
            node_neg: Negative node.
            dc: DC voltage value.
            ac: AC magnitude.
            ac_phase: AC phase in degrees.
            pulse: Pulse waveform parameters.
            sine: Sine waveform parameters.

        Returns:
            Self for method chaining.
        """
        return self._add_component(
            VoltageSource(
                name, node_pos, node_neg, dc=dc, ac=ac, ac_phase=ac_phase, pulse=pulse, sine=sine
            )
        )

    def add_current_source(
        self,
        name: str,
        node_pos: str,
        node_neg: str,
        *,
        dc: float | None = None,
        ac: float | None = None,
        ac_phase: float = 0,
    ) -> "Circuit":
        """Add a current source to the circuit.

        Args:
            name: Source name (must start with 'I').
            node_pos: Positive node.
            node_neg: Negative node.
            dc: DC current value.
            ac: AC magnitude.
            ac_phase: AC phase in degrees.

        Returns:
            Self for method chaining.
        """
        return self._add_component(
            CurrentSource(name, node_pos, node_neg, dc=dc, ac=ac, ac_phase=ac_phase)
        )

    def add_component(self, component: Component) -> "Circuit":
        """Add a pre-created component to the circuit.

        Args:
            component: The component to add.

        Returns:
            Self for method chaining.
        """
        return self._add_component(component)

    # Analysis commands

    def add_ac_analysis(
        self,
        start: float,
        stop: float,
        points_per_decade: int = 10,
        variation: str = "dec",
    ) -> "Circuit":
        """Add AC analysis command.

        Args:
            start: Start frequency in Hz.
            stop: Stop frequency in Hz.
            points_per_decade: Number of points per decade (for 'dec' variation).
            variation: Type of frequency variation: 'dec', 'oct', or 'lin'.

        Returns:
            Self for method chaining.
        """
        # Format frequencies
        start_str = self._format_frequency(start)
        stop_str = self._format_frequency(stop)

        self.analyses.append(f".ac {variation} {points_per_decade} {start_str} {stop_str}")
        return self

    def add_dc_analysis(
        self,
        source: str,
        start: float,
        stop: float,
        step: float,
    ) -> "Circuit":
        """Add DC sweep analysis command.

        Args:
            source: Name of the source to sweep.
            start: Start value.
            stop: Stop value.
            step: Step size.

        Returns:
            Self for method chaining.
        """
        self.analyses.append(f".dc {source} {start} {stop} {step}")
        return self

    def add_transient_analysis(
        self,
        stop_time: float,
        step_time: float | None = None,
        start_time: float = 0,
    ) -> "Circuit":
        """Add transient analysis command.

        Args:
            stop_time: Stop time in seconds.
            step_time: Maximum time step (optional).
            start_time: Start time for data output (default 0).

        Returns:
            Self for method chaining.
        """
        if step_time is not None:
            self.analyses.append(f".tran {step_time} {stop_time} {start_time}")
        else:
            self.analyses.append(f".tran {stop_time}")
        return self

    def add_op_analysis(self) -> "Circuit":
        """Add operating point analysis command.

        Returns:
            Self for method chaining.
        """
        self.analyses.append(".op")
        return self

    @staticmethod
    def _format_frequency(freq: float) -> str:
        """Format frequency for SPICE (e.g., 1e6 -> 1meg)."""
        if freq >= 1e12:
            return f"{freq / 1e12}t"
        elif freq >= 1e9:
            return f"{freq / 1e9}g"
        elif freq >= 1e6:
            return f"{freq / 1e6}meg"
        elif freq >= 1e3:
            return f"{freq / 1e3}k"
        else:
            return str(freq)

    def to_netlist(self) -> str:
        """Generate SPICE netlist string.

        Returns:
            Complete SPICE netlist as a string.
        """
        lines = [f"* {self.name}"]

        # Add all components
        for component in self.components:
            lines.append(component.to_spice())

        # Add analysis commands
        for analysis in self.analyses:
            lines.append(analysis)

        # End statement
        lines.append(".end")

        return "\n".join(lines)

    def save(self, filepath: str) -> None:
        """Save netlist to a file.

        Args:
            filepath: Path to save the netlist file.
        """
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(self.to_netlist())

    def __repr__(self) -> str:
        """Return string representation."""
        return f"Circuit({self.name!r}, components={len(self.components)})"

    def __len__(self) -> int:
        """Return number of components."""
        return len(self.components)
