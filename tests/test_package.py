"""Test OhmSPICE package initialization."""

import ohmspice


def test_version():
    """Test that version is defined."""
    assert hasattr(ohmspice, "__version__")
    assert ohmspice.__version__ == "0.1.0"


def test_author():
    """Test that author is defined."""
    assert hasattr(ohmspice, "__author__")
    assert ohmspice.__author__ == "Eray Erdogan"
