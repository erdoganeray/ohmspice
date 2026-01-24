"""LTspice simulator backend."""

import os
import subprocess
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING

from ohmspice.simulators.base import (
    SimulationError,
    Simulator,
    SimulatorNotFoundError,
)

if TYPE_CHECKING:
    from ohmspice.analysis.results import SimulationResults
    from ohmspice.circuit import Circuit


class LTSpice(Simulator):
    """LTspice simulator backend.

    Supports running simulations using LTspice XVII on Windows and macOS.
    Linux support requires Wine.

    Example:
        >>> sim = LTSpice()
        >>> if sim.is_available():
        ...     results = sim.run(circuit)
        ...     freq = results.get_frequency()
        ...     vout = results.get_voltage("out")

    Attributes:
        executable: Path to the LTspice executable.
    """

    name = "ltspice"

    # Common installation paths
    WINDOWS_PATHS = [
        # New ADI LTspice (user-local installation)
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\ADI\LTspice\LTspice.exe"),
        # Legacy paths
        r"C:\Program Files\LTC\LTspiceXVII\XVIIx64.exe",
        r"C:\Program Files\LTC\LTspice\bin\LTspice.exe",
        r"C:\Program Files\ADI\LTspice\LTspice.exe",
        r"C:\Program Files (x86)\LTC\LTspiceIV\scad3.exe",
    ]

    MACOS_PATHS = [
        "/Applications/LTspice.app/Contents/MacOS/LTspice",
    ]

    def __init__(self, executable: str | Path | None = None) -> None:
        """Initialize LTspice simulator.

        Args:
            executable: Optional explicit path to LTspice executable.
                If not provided, attempts auto-detection.

        Raises:
            SimulatorNotFoundError: If LTspice cannot be found.
        """
        if executable:
            self.executable = Path(executable)
            if not self.executable.exists():
                raise SimulatorNotFoundError(f"LTspice not found at: {executable}")
        else:
            found = self.find_executable()
            if found is None:
                raise SimulatorNotFoundError(
                    "LTspice not found. Please install LTspice or provide "
                    "the executable path explicitly."
                )
            self.executable = found

    @classmethod
    def is_available(cls) -> bool:
        """Check if LTspice is available on the system."""
        return cls.find_executable() is not None

    @classmethod
    def find_executable(cls) -> Path | None:
        """Find LTspice executable.

        Searches common installation locations based on the operating system.

        Returns:
            Path to LTspice executable, or None if not found.
        """
        import platform

        system = platform.system()

        if system == "Windows":
            paths = cls.WINDOWS_PATHS
        elif system == "Darwin":  # macOS
            paths = cls.MACOS_PATHS
        else:  # Linux - check for Wine
            # TODO: Add Wine support
            return None

        for path_str in paths:
            path = Path(path_str)
            if path.exists():
                return path

        # Check if ltspice is in PATH
        import shutil

        ltspice_in_path = shutil.which("ltspice") or shutil.which("XVIIx64")
        if ltspice_in_path:
            return Path(ltspice_in_path)

        return None

    def run(
        self,
        circuit: "Circuit",
        *,
        timeout: float | None = 60.0,
    ) -> "SimulationResults":
        """Run simulation on a circuit.

        Creates a temporary netlist file, runs LTspice, and parses results.

        Args:
            circuit: The circuit to simulate.
            timeout: Maximum time to wait for simulation (seconds).

        Returns:
            SimulationResults with simulation data.

        Raises:
            SimulationError: If simulation fails.
        """
        # Create temporary netlist file
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".cir",
            delete=False,
            encoding="utf-8",
        ) as f:
            f.write(circuit.to_netlist())
            netlist_path = Path(f.name)

        try:
            return self.run_netlist(netlist_path, timeout=timeout)
        finally:
            # Clean up temporary files
            try:
                netlist_path.unlink(missing_ok=True)
                # Also clean up .raw and .log files
                netlist_path.with_suffix(".raw").unlink(missing_ok=True)
                netlist_path.with_suffix(".log").unlink(missing_ok=True)
            except OSError:
                pass

    def run_netlist(
        self,
        netlist_path: str | Path,
        *,
        timeout: float | None = 60.0,
    ) -> "SimulationResults":
        """Run simulation on a netlist file.

        Args:
            netlist_path: Path to the netlist file.
            timeout: Maximum time to wait for simulation (seconds).

        Returns:
            SimulationResults with simulation data.

        Raises:
            FileNotFoundError: If netlist file doesn't exist.
            SimulationError: If simulation fails.
        """
        from ohmspice.analysis.results import SimulationResults

        netlist_path = Path(netlist_path)
        if not netlist_path.exists():
            raise FileNotFoundError(f"Netlist file not found: {netlist_path}")

        # LTspice command line arguments
        # -b: batch mode (no GUI)
        # -Run: run simulation
        cmd = [str(self.executable), "-b", "-Run", str(netlist_path)]

        try:
            subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=netlist_path.parent,
            )
        except subprocess.TimeoutExpired as e:
            raise SimulationError(f"Simulation timed out after {timeout}s") from e
        except subprocess.SubprocessError as e:
            raise SimulationError(f"Failed to run LTspice: {e}") from e

        # Check for .raw output file
        raw_file = netlist_path.with_suffix(".raw")
        if not raw_file.exists():
            # Check log file for errors
            log_file = netlist_path.with_suffix(".log")
            error_msg = "Simulation failed - no output file generated"
            if log_file.exists():
                log_content = log_file.read_text(encoding="utf-8", errors="ignore")
                error_msg += f"\nLog:\n{log_content}"
            raise SimulationError(error_msg)

        return SimulationResults(raw_file)

    def __repr__(self) -> str:
        """Return string representation."""
        return f"LTSpice(executable={self.executable!r})"
