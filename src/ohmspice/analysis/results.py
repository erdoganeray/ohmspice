"""Simulation results parsing and handling.

Supports parsing LTspice .raw binary files.
"""

import struct
from enum import Enum
from pathlib import Path
from typing import Any

import numpy as np


class AnalysisType(Enum):
    """Types of SPICE analysis."""

    OPERATING_POINT = "Operating Point"
    DC_SWEEP = "DC sweep"
    AC_ANALYSIS = "AC Analysis"
    TRANSIENT = "Transient Analysis"
    NOISE = "Noise Spectral Density"
    UNKNOWN = "Unknown"


class SimulationResults:
    """Container for SPICE simulation results.

    Parses LTspice .raw files and provides convenient access to
    simulation data.

    Example:
        >>> results = SimulationResults("circuit.raw")
        >>> freq = results.get_frequency()
        >>> vout_mag = results.get_voltage("out")
        >>> vout_phase = results.get_phase("out")

    Attributes:
        raw_file: Path to the .raw file.
        analysis_type: Type of analysis performed.
        variables: List of variable names.
        data: Dictionary mapping variable names to numpy arrays.
    """

    def __init__(self, raw_file: str | Path) -> None:
        """Load and parse a .raw file.

        Args:
            raw_file: Path to the LTspice .raw file.

        Raises:
            FileNotFoundError: If the file doesn't exist.
            ValueError: If the file format is invalid.
        """
        self.raw_file = Path(raw_file)
        if not self.raw_file.exists():
            raise FileNotFoundError(f"Raw file not found: {raw_file}")

        self.analysis_type = AnalysisType.UNKNOWN
        self.variables: list[str] = []
        self._variable_types: list[str] = []
        self._num_points = 0
        self._is_complex = False
        self.data: dict[str, np.ndarray] = {}

        self._parse()

    def _parse(self) -> None:
        """Parse the .raw file."""
        # Read raw file in binary mode
        content = self.raw_file.read_bytes()

        # LTspice .raw files have a text header followed by binary data
        # The header is ASCII/UTF-16 depending on version
        header_end = self._find_header_end(content)
        if header_end == -1:
            raise ValueError("Could not find end of header in .raw file")

        # Try to decode header as UTF-16 first, then ASCII
        try:
            header = content[:header_end].decode("utf-16-le")
        except UnicodeDecodeError:
            try:
                header = content[:header_end].decode("ascii", errors="ignore")
            except Exception:
                header = content[:header_end].decode("latin-1", errors="ignore")

        # Parse header
        self._parse_header(header)

        # Parse binary data
        binary_data = content[header_end:]
        self._parse_binary_data(binary_data)

    def _find_header_end(self, content: bytes) -> int:
        """Find the end of the header section."""
        # Look for "Binary:" or "Values:" marker
        markers = [b"Binary:\n", b"B\x00i\x00n\x00a\x00r\x00y\x00:\x00\n\x00"]

        for marker in markers:
            pos = content.find(marker)
            if pos != -1:
                return pos + len(marker)

        # Also check for ASCII "Values:" for ASCII format
        values_marker = content.find(b"Values:\n")
        if values_marker != -1:
            return values_marker + len(b"Values:\n")

        return -1

    def _parse_header(self, header: str) -> None:
        """Parse the text header."""
        lines = header.strip().split("\n")

        in_variables = False
        var_idx = 0

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Parse key-value pairs
            if ":" in line and not in_variables:
                key, _, value = line.partition(":")
                key = key.strip().lower()
                value = value.strip()

                if key == "plotname":
                    self.analysis_type = self._parse_analysis_type(value)
                elif key == "flags":
                    self._is_complex = "complex" in value.lower()
                elif key == "no. points":
                    self._num_points = int(value)
                elif key == "no. variables":
                    num_vars = int(value)
                    self.variables = [""] * num_vars
                    self._variable_types = [""] * num_vars
                elif key == "variables":
                    in_variables = True

            elif in_variables:
                # Variable definitions: index name type
                parts = line.split()
                if len(parts) >= 3:
                    try:
                        idx = int(parts[0])
                        name = parts[1]
                        var_type = parts[2]
                        if idx < len(self.variables):
                            self.variables[idx] = name
                            self._variable_types[idx] = var_type
                    except (ValueError, IndexError):
                        pass

    def _parse_analysis_type(self, plotname: str) -> AnalysisType:
        """Parse analysis type from plotname."""
        plotname_lower = plotname.lower()
        if "operating point" in plotname_lower:
            return AnalysisType.OPERATING_POINT
        elif "dc" in plotname_lower:
            return AnalysisType.DC_SWEEP
        elif "ac" in plotname_lower:
            return AnalysisType.AC_ANALYSIS
        elif "transient" in plotname_lower or "tran" in plotname_lower:
            return AnalysisType.TRANSIENT
        elif "noise" in plotname_lower:
            return AnalysisType.NOISE
        return AnalysisType.UNKNOWN

    def _parse_binary_data(self, data: bytes) -> None:
        """Parse binary data section."""
        if not self.variables or self._num_points == 0:
            return

        num_vars = len(self.variables)

        # Determine data format
        # LTspice uses double precision (8 bytes) for independent variable (time/freq)
        # and either double (8 bytes) or complex double (16 bytes) for dependent variables

        if self._is_complex:
            # AC analysis: first var is double, rest are complex (2 doubles)
            # Each point: 8 bytes + (num_vars-1)*16 bytes
            point_size = 8 + (num_vars - 1) * 16
        else:
            # Transient/DC: all doubles
            point_size = num_vars * 8

        expected_size = point_size * self._num_points
        if len(data) < expected_size:
            # Try with different assumptions
            self._num_points = len(data) // point_size

        # Initialize arrays
        for i, var_name in enumerate(self.variables):
            if self._is_complex and i > 0:
                self.data[var_name] = np.zeros(self._num_points, dtype=np.complex128)
            else:
                self.data[var_name] = np.zeros(self._num_points, dtype=np.float64)

        # Parse points
        offset = 0
        for point_idx in range(self._num_points):
            if offset + point_size > len(data):
                break

            for var_idx, var_name in enumerate(self.variables):
                if var_idx == 0 or not self._is_complex:
                    # Double precision
                    if offset + 8 <= len(data):
                        value = struct.unpack_from("<d", data, offset)[0]
                        self.data[var_name][point_idx] = value
                        offset += 8
                else:
                    # Complex (two doubles: real, imag)
                    if offset + 16 <= len(data):
                        real = struct.unpack_from("<d", data, offset)[0]
                        imag = struct.unpack_from("<d", data, offset + 8)[0]
                        self.data[var_name][point_idx] = complex(real, imag)
                        offset += 16

    def get_frequency(self) -> np.ndarray:
        """Get frequency values for AC analysis.

        Returns:
            Numpy array of frequency values.

        Raises:
            ValueError: If not an AC analysis or no frequency data.
        """
        # Look for frequency variable
        for name in ["frequency", "freq", "Frequency"]:
            if name in self.data:
                return np.abs(self.data[name])  # Frequency might be stored as complex

        # First variable is often the independent variable
        if self.variables and self.variables[0].lower() in ["frequency", "freq"]:
            return np.abs(self.data[self.variables[0]])

        raise ValueError("No frequency data found in results")

    def get_time(self) -> np.ndarray:
        """Get time values for transient analysis.

        Returns:
            Numpy array of time values.

        Raises:
            ValueError: If not a transient analysis or no time data.
        """
        for name in ["time", "Time"]:
            if name in self.data:
                return self.data[name].real if np.iscomplexobj(self.data[name]) else self.data[name]

        if self.variables and self.variables[0].lower() == "time":
            arr = self.data[self.variables[0]]
            return arr.real if np.iscomplexobj(arr) else arr

        raise ValueError("No time data found in results")

    def get_voltage(self, node: str) -> np.ndarray:
        """Get voltage magnitude at a node.

        Args:
            node: Node name (e.g., 'out', 'in').

        Returns:
            Numpy array of voltage magnitudes.

        Raises:
            KeyError: If node not found.
        """
        # Try various naming conventions
        candidates = [
            f"V({node})",
            f"v({node})",
            f"V({node.lower()})",
            f"V({node.upper()})",
            node,
        ]

        for name in candidates:
            if name in self.data:
                values = self.data[name]
                if np.iscomplexobj(values):
                    return np.abs(values)
                return values

        raise KeyError(f"Voltage at node '{node}' not found. Available: {list(self.data.keys())}")

    def get_phase(self, node: str) -> np.ndarray:
        """Get voltage phase at a node (in degrees).

        Args:
            node: Node name.

        Returns:
            Numpy array of phase values in degrees.

        Raises:
            KeyError: If node not found.
            ValueError: If data is not complex.
        """
        candidates = [
            f"V({node})",
            f"v({node})",
            f"V({node.lower()})",
            f"V({node.upper()})",
            node,
        ]

        for name in candidates:
            if name in self.data:
                values = self.data[name]
                if np.iscomplexobj(values):
                    return np.angle(values, deg=True)
                raise ValueError(f"Data for '{node}' is not complex, no phase available")

        raise KeyError(f"Voltage at node '{node}' not found")

    def get_current(self, component: str) -> np.ndarray:
        """Get current through a component.

        Args:
            component: Component name (e.g., 'R1', 'V1').

        Returns:
            Numpy array of current magnitudes.

        Raises:
            KeyError: If component current not found.
        """
        candidates = [
            f"I({component})",
            f"i({component})",
            f"I({component.lower()})",
            f"I({component.upper()})",
            f"Ix({component}:+)",
        ]

        for name in candidates:
            if name in self.data:
                values = self.data[name]
                if np.iscomplexobj(values):
                    return np.abs(values)
                return values

        raise KeyError(f"Current through '{component}' not found. Available: {list(self.data.keys())}")

    def get_variable(self, name: str) -> np.ndarray:
        """Get any variable by exact name.

        Args:
            name: Exact variable name as in the .raw file.

        Returns:
            Numpy array of values.

        Raises:
            KeyError: If variable not found.
        """
        if name in self.data:
            return self.data[name]
        raise KeyError(f"Variable '{name}' not found. Available: {list(self.data.keys())}")

    @property
    def variable_names(self) -> list[str]:
        """Get list of all variable names."""
        return list(self.data.keys())

    def __repr__(self) -> str:
        """Return string representation."""
        return (
            f"SimulationResults("
            f"type={self.analysis_type.value}, "
            f"points={self._num_points}, "
            f"variables={len(self.variables)})"
        )
