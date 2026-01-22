"""Netlist generation utilities."""

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ohmspice.circuit import Circuit


class NetlistGenerator:
    """SPICE netlist generator.

    This class provides utilities for generating and saving SPICE netlists
    from Circuit objects.

    Example:
        >>> generator = NetlistGenerator()
        >>> netlist = generator.generate(circuit)
        >>> generator.save(circuit, "circuit.cir")
    """

    def generate(self, circuit: "Circuit") -> str:
        """Generate SPICE netlist string from a circuit.

        Args:
            circuit: The circuit to generate netlist from.

        Returns:
            SPICE netlist as a string.
        """
        return circuit.to_netlist()

    def save(self, circuit: "Circuit", filepath: str | Path) -> Path:
        """Save circuit netlist to a file.

        Args:
            circuit: The circuit to save.
            filepath: Path to save the netlist file. Will be created
                with .cir extension if no extension provided.

        Returns:
            Path to the saved file.
        """
        path = Path(filepath)

        # Add .cir extension if not present
        if not path.suffix:
            path = path.with_suffix(".cir")

        # Create parent directories if needed
        path.parent.mkdir(parents=True, exist_ok=True)

        # Write netlist
        netlist = self.generate(circuit)
        path.write_text(netlist, encoding="utf-8")

        return path
