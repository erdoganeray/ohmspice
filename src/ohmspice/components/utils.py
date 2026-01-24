"""Utility functions for parsing and formatting component values.

Supports SPICE engineering notation:
- f = femto (1e-15)
- p = pico (1e-12)
- n = nano (1e-9)
- u = micro (1e-6)
- m = milli (1e-3)
- k = kilo (1e3)
- meg = mega (1e6)
- g = giga (1e9)
- t = tera (1e12)
"""

import re

# SPICE multiplier prefixes
MULTIPLIERS: dict[str, float] = {
    "f": 1e-15,
    "p": 1e-12,
    "n": 1e-9,
    "u": 1e-6,
    "µ": 1e-6,  # Unicode micro sign
    "m": 1e-3,
    "k": 1e3,
    "meg": 1e6,
    "g": 1e9,
    "t": 1e12,
}

# Reverse lookup for formatting
REVERSE_MULTIPLIERS: list[tuple[float, str]] = [
    (1e12, "T"),
    (1e9, "G"),
    (1e6, "meg"),
    (1e3, "k"),
    (1e0, ""),
    (1e-3, "m"),
    (1e-6, "u"),
    (1e-9, "n"),
    (1e-12, "p"),
    (1e-15, "f"),
]

# Pattern to match value with optional multiplier
# Note: 'meg' must come before 'm' for correct matching
VALUE_PATTERN = re.compile(
    r"^([+-]?\d+\.?\d*(?:[eE][+-]?\d+)?)\s*(meg|f|p|n|u|µ|m|k|g|t)?(.*)$", re.IGNORECASE
)


def parse_value(value: str | int | float) -> float:
    """Parse a SPICE value string into a float.

    Args:
        value: Value to parse. Can be a number or string with optional
            engineering notation suffix (e.g., '1k', '100n', '4.7meg').

    Returns:
        The parsed value as a float.

    Raises:
        ValueError: If the value cannot be parsed.

    Examples:
        >>> parse_value("1k")
        1000.0
        >>> parse_value("100n")
        1e-07
        >>> parse_value("4.7meg")
        4700000.0
        >>> parse_value(1000)
        1000.0
    """
    if isinstance(value, (int, float)):
        return float(value)

    if not isinstance(value, str):
        raise ValueError(f"Cannot parse value: {value}")

    value = value.strip()
    if not value:
        raise ValueError("Empty value string")

    match = VALUE_PATTERN.match(value)
    if not match:
        raise ValueError(f"Invalid value format: {value}")

    number_str, multiplier, unit = match.groups()
    number = float(number_str)

    if multiplier:
        multiplier_lower = multiplier.lower()
        if multiplier_lower in MULTIPLIERS:
            number *= MULTIPLIERS[multiplier_lower]
        else:
            raise ValueError(f"Unknown multiplier: {multiplier}")

    return number


def format_value(value: float, unit: str = "") -> str:
    """Format a float value using engineering notation.

    Args:
        value: The value to format.
        unit: Optional unit suffix (e.g., 'Ω', 'F', 'H').

    Returns:
        Formatted string with appropriate multiplier.

    Examples:
        >>> format_value(1000)
        '1k'
        >>> format_value(1e-9, 'F')
        '1nF'
        >>> format_value(4700000)
        '4.7meg'
    """
    if value == 0:
        return f"0{unit}"

    abs_value = abs(value)
    sign = "-" if value < 0 else ""

    for threshold, suffix in REVERSE_MULTIPLIERS:
        if abs_value >= threshold:
            scaled = abs_value / threshold
            # Format to avoid unnecessary decimals
            if scaled == int(scaled):
                return f"{sign}{int(scaled)}{suffix}{unit}"
            else:
                # Round to 3 significant digits
                formatted = f"{scaled:.3g}"
                return f"{sign}{formatted}{suffix}{unit}"

    # Fallback for very small values
    return f"{sign}{value}{unit}"
