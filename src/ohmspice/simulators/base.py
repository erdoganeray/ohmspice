"""Base simulator class."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ohmspice.analysis.results import SimulationResults
    from ohmspice.circuit import Circuit


class Simulator(ABC):
    """Abstract base class for SPICE simulators.

    All simulator backends must implement this interface.

    Attributes:
        name: Simulator name (e.g., 'ltspice', 'ngspice').
    """

    name: str = "base"

    @classmethod
    @abstractmethod
    def is_available(cls) -> bool:
        """Check if this simulator is available on the system.

        Returns:
            True if the simulator is installed and accessible.
        """
        pass

    @classmethod
    @abstractmethod
    def find_executable(cls) -> Path | None:
        """Find the simulator executable path.

        Returns:
            Path to the executable, or None if not found.
        """
        pass

    @abstractmethod
    def run(
        self,
        circuit: "Circuit",
        *,
        timeout: float | None = None,
    ) -> "SimulationResults":
        """Run simulation on a circuit.

        Args:
            circuit: The circuit to simulate.
            timeout: Maximum time to wait for simulation (seconds).

        Returns:
            SimulationResults object with simulation data.

        Raises:
            SimulatorNotFoundError: If simulator executable not found.
            SimulationError: If simulation fails.
        """
        pass

    @abstractmethod
    def run_netlist(
        self,
        netlist_path: str | Path,
        *,
        timeout: float | None = None,
    ) -> "SimulationResults":
        """Run simulation on a netlist file.

        Args:
            netlist_path: Path to the netlist file.
            timeout: Maximum time to wait for simulation (seconds).

        Returns:
            SimulationResults object with simulation data.

        Raises:
            SimulatorNotFoundError: If simulator executable not found.
            SimulationError: If simulation fails.
            FileNotFoundError: If netlist file doesn't exist.
        """
        pass


class SimulatorError(Exception):
    """Base exception for simulator errors."""
    pass


class SimulatorNotFoundError(SimulatorError):
    """Raised when simulator executable is not found."""
    pass


class SimulationError(SimulatorError):
    """Raised when simulation fails."""
    pass
