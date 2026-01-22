"""Base component class for SPICE circuits."""

from abc import ABC, abstractmethod
from typing import Any, Union

from ohmspice.components.utils import parse_value


class Component(ABC):
    """Abstract base class for all SPICE components.

    All components have a name and connect to nodes. The specific
    behavior and netlist format depends on the component type.

    Attributes:
        name: Component identifier (e.g., 'R1', 'C1', 'V1').
        node1: First connection node.
        node2: Second connection node.
    """

    def __init__(self, name: str, node1: str, node2: str) -> None:
        """Initialize a component.

        Args:
            name: Component identifier. Must start with appropriate letter
                for component type (R for resistor, C for capacitor, etc.).
            node1: First connection node name.
            node2: Second connection node name.

        Raises:
            ValueError: If name is empty or nodes are invalid.
        """
        if not name:
            raise ValueError("Component name cannot be empty")
        if not node1:
            raise ValueError("Node1 cannot be empty")
        if not node2:
            raise ValueError("Node2 cannot be empty")

        self.name = name
        self.node1 = self._normalize_node(node1)
        self.node2 = self._normalize_node(node2)

    @staticmethod
    def _normalize_node(node: str) -> str:
        """Normalize node name.

        Converts 'gnd' and 'GND' to '0' for SPICE compatibility.

        Args:
            node: Node name to normalize.

        Returns:
            Normalized node name.
        """
        if node.lower() == "gnd":
            return "0"
        return node

    @abstractmethod
    def to_spice(self) -> str:
        """Generate SPICE netlist line for this component.

        Returns:
            SPICE netlist format string for this component.
        """
        pass

    def __repr__(self) -> str:
        """Return string representation of component."""
        return f"{self.__class__.__name__}({self.name!r}, {self.node1!r}, {self.node2!r})"


class TwoTerminalComponent(Component):
    """Base class for two-terminal passive components with a value.

    This includes resistors, capacitors, and inductors.

    Attributes:
        value: Component value (parsed to float).
        value_str: Original value string for netlist output.
    """

    #: Component prefix letter (R, C, L, etc.)
    PREFIX: str = ""
    #: Component unit (Ω, F, H, etc.)
    UNIT: str = ""

    def __init__(
        self,
        name: str,
        node1: str,
        node2: str,
        value: Union[str, int, float],
    ) -> None:
        """Initialize a two-terminal component.

        Args:
            name: Component identifier.
            node1: First connection node.
            node2: Second connection node.
            value: Component value. Can be a number or string with
                engineering notation (e.g., '1k', '100n').

        Raises:
            ValueError: If name doesn't start with correct prefix or value is invalid.
        """
        super().__init__(name, node1, node2)

        # Validate name prefix
        if self.PREFIX and not name.upper().startswith(self.PREFIX):
            raise ValueError(
                f"{self.__class__.__name__} name must start with '{self.PREFIX}', got '{name}'"
            )

        # Store original string for netlist output
        self.value_str = str(value) if isinstance(value, (int, float)) else value

        # Parse value to float for calculations
        self.value = parse_value(value)

    def to_spice(self) -> str:
        """Generate SPICE netlist line.

        Returns:
            SPICE netlist format: NAME NODE1 NODE2 VALUE
        """
        return f"{self.name} {self.node1} {self.node2} {self.value_str}"

    def __repr__(self) -> str:
        """Return string representation."""
        return (
            f"{self.__class__.__name__}({self.name!r}, {self.node1!r}, "
            f"{self.node2!r}, {self.value_str!r})"
        )
