"""Pytest configuration and fixtures for OhmSPICE tests."""

import pytest


@pytest.fixture
def sample_circuit_data():
    """Sample circuit data for testing."""
    return {
        "name": "RC Low-Pass Filter",
        "description": "1kHz cutoff frequency low-pass filter",
        "components": [
            {"type": "resistor", "id": "R1", "node1": "in", "node2": "out", "value": "1k"},
            {"type": "capacitor", "id": "C1", "node1": "out", "node2": "0", "value": "159n"},
        ],
        "sources": [
            {"type": "voltage", "id": "V1", "node1": "in", "node2": "0", "dc": 0, "ac": 1}
        ],
        "analysis": {
            "type": "ac",
            "start": 1,
            "stop": 1000000,
            "points_per_decade": 10,
        },
    }


@pytest.fixture
def sample_netlist():
    """Sample SPICE netlist string."""
    return """* RC Low-Pass Filter
R1 in out 1k
C1 out 0 159n
V1 in 0 AC 1
.ac dec 10 1 1meg
.end"""
