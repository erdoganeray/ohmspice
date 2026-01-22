"""Passive components: Resistor, Capacitor, Inductor."""

from typing import Union

from ohmspice.components.base import TwoTerminalComponent


class Resistor(TwoTerminalComponent):
    """A resistor component.

    SPICE format: Rname node1 node2 value

    Example:
        >>> r1 = Resistor("R1", "in", "out", "1k")
        >>> r1.to_spice()
        'R1 in out 1k'
        >>> r1.value
        1000.0
    """

    PREFIX = "R"
    UNIT = "Ω"

    def __init__(
        self,
        name: str,
        node1: str,
        node2: str,
        value: Union[str, int, float],
    ) -> None:
        """Create a resistor.

        Args:
            name: Resistor name (must start with 'R').
            node1: First connection node.
            node2: Second connection node.
            value: Resistance value in ohms. Supports engineering notation
                (e.g., '1k' for 1000Ω, '4.7meg' for 4.7MΩ).
        """
        super().__init__(name, node1, node2, value)


class Capacitor(TwoTerminalComponent):
    """A capacitor component.

    SPICE format: Cname node+ node- value [IC=initial_voltage]

    Example:
        >>> c1 = Capacitor("C1", "out", "0", "100n")
        >>> c1.to_spice()
        'C1 out 0 100n'
        >>> c1.value
        1e-07
    """

    PREFIX = "C"
    UNIT = "F"

    def __init__(
        self,
        name: str,
        node1: str,
        node2: str,
        value: Union[str, int, float],
        initial_voltage: float | None = None,
    ) -> None:
        """Create a capacitor.

        Args:
            name: Capacitor name (must start with 'C').
            node1: Positive node.
            node2: Negative node.
            value: Capacitance value in farads. Supports engineering notation
                (e.g., '100n' for 100nF, '10u' for 10µF).
            initial_voltage: Optional initial voltage for transient analysis.
        """
        super().__init__(name, node1, node2, value)
        self.initial_voltage = initial_voltage

    def to_spice(self) -> str:
        """Generate SPICE netlist line."""
        base = super().to_spice()
        if self.initial_voltage is not None:
            return f"{base} IC={self.initial_voltage}"
        return base


class Inductor(TwoTerminalComponent):
    """An inductor component.

    SPICE format: Lname node1 node2 value [IC=initial_current]

    Example:
        >>> l1 = Inductor("L1", "in", "out", "10m")
        >>> l1.to_spice()
        'L1 in out 10m'
        >>> l1.value
        0.01
    """

    PREFIX = "L"
    UNIT = "H"

    def __init__(
        self,
        name: str,
        node1: str,
        node2: str,
        value: Union[str, int, float],
        initial_current: float | None = None,
    ) -> None:
        """Create an inductor.

        Args:
            name: Inductor name (must start with 'L').
            node1: First node.
            node2: Second node.
            value: Inductance value in henries. Supports engineering notation
                (e.g., '10m' for 10mH, '100u' for 100µH).
            initial_current: Optional initial current for transient analysis.
        """
        super().__init__(name, node1, node2, value)
        self.initial_current = initial_current

    def to_spice(self) -> str:
        """Generate SPICE netlist line."""
        base = super().to_spice()
        if self.initial_current is not None:
            return f"{base} IC={self.initial_current}"
        return base
