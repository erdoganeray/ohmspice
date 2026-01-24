"""Circuit templates for common electronic circuits.

This module provides ready-to-use circuit templates for filters,
amplifiers, oscillators, and power circuits.

Example:
    >>> from ohmspice.templates import filters
    >>> circuit = filters.rc_lowpass(fc=1000, r=1000)
    >>> print(circuit.to_netlist())
"""

from ohmspice.templates import amplifiers, filters, oscillators, power
from ohmspice.templates.base import CircuitTemplate, TemplateInfo, TemplateParameter


def list_all_templates() -> dict[str, list[TemplateInfo]]:
    """List all available templates organized by category.

    Returns:
        Dictionary with category names as keys and list of TemplateInfo as values.
    """
    return {
        "filters": filters.list_templates(),
        "amplifiers": amplifiers.list_templates(),
        "oscillators": oscillators.list_templates(),
        "power": power.list_templates(),
    }


def get_template(name: str) -> CircuitTemplate | None:
    """Get a template by name.

    Args:
        name: Template name (e.g., 'rc_lowpass', 'voltage_divider').

    Returns:
        CircuitTemplate instance or None if not found.
    """
    all_templates = {
        **filters.FILTER_TEMPLATES,
        **amplifiers.AMPLIFIER_TEMPLATES,
        **oscillators.OSCILLATOR_TEMPLATES,
        **power.POWER_TEMPLATES,
    }
    return all_templates.get(name)


__all__ = [
    # Base classes
    "CircuitTemplate",
    "TemplateInfo",
    "TemplateParameter",
    # Submodules
    "filters",
    "amplifiers",
    "oscillators",
    "power",
    # Functions
    "list_all_templates",
    "get_template",
]
