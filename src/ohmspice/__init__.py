"""OhmSPICE - Open-source SPICE toolkit with AI integration for electronic circuit design.

A hybrid toolkit that combines template-based circuit design with AI-powered capabilities,
enabling both offline CLI usage and intelligent circuit synthesis through LLM integration.

Example:
    >>> from ohmspice import Circuit
    >>> circuit = Circuit("RC Low-Pass Filter")
    >>> circuit.add_voltage_source("V1", "in", "0", ac=1)
    >>> circuit.add_resistor("R1", "in", "out", "1k")
    >>> circuit.add_capacitor("C1", "out", "0", "159n")
    >>> circuit.add_ac_analysis(start=1, stop=1e6)
    >>> print(circuit.to_netlist())
"""

__version__ = "0.1.0"
__author__ = "Eray Erdogan"

# Core classes
from ohmspice.circuit import Circuit

# Components
from ohmspice.components import (
    Capacitor,
    Component,
    CurrentSource,
    Inductor,
    Resistor,
    VoltageSource,
    format_value,
    parse_value,
)
from ohmspice.netlist import NetlistGenerator

# Simulators - import conditionally to avoid errors if dependencies missing
try:
    from ohmspice.simulators import LTSpice, Simulator
except ImportError:
    LTSpice = None  # type: ignore
    Simulator = None  # type: ignore

# Analysis results
try:
    from ohmspice.analysis import SimulationResults
except ImportError:
    SimulationResults = None  # type: ignore

__all__ = [
    # Version
    "__version__",
    "__author__",
    # Core
    "Circuit",
    "NetlistGenerator",
    # Components
    "Component",
    "Resistor",
    "Capacitor",
    "Inductor",
    "VoltageSource",
    "CurrentSource",
    # Utilities
    "parse_value",
    "format_value",
    # Simulators
    "Simulator",
    "LTSpice",
    # Results
    "SimulationResults",
]
