"""Base class for circuit templates.

This module provides the abstract base class for all circuit templates.
Templates are pre-configured circuit designs that can be customized
with parameters.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from ohmspice.circuit import Circuit


@dataclass
class TemplateParameter:
    """Describes a parameter for a circuit template.

    Attributes:
        name: Parameter name.
        description: Human-readable description.
        unit: Physical unit (e.g., 'Hz', 'Ω').
        required: Whether parameter is required.
        default: Default value if not required.
    """

    name: str
    description: str
    unit: str = ""
    required: bool = True
    default: Any = None


@dataclass
class TemplateInfo:
    """Metadata about a circuit template.

    Attributes:
        name: Template name (e.g., 'rc_lowpass').
        display_name: Human-readable name.
        description: Template description.
        category: Category (filters, amplifiers, etc.).
        parameters: List of template parameters.
    """

    name: str
    display_name: str
    description: str
    category: str
    parameters: list[TemplateParameter] = field(default_factory=list)


class CircuitTemplate(ABC):
    """Abstract base class for circuit templates.

    Templates provide pre-designed circuits that can be customized
    with component values. They also include formulas to calculate
    component values from specifications.

    Example:
        >>> class RCLowPassTemplate(CircuitTemplate):
        ...     @classmethod
        ...     def info(cls) -> TemplateInfo:
        ...         return TemplateInfo(
        ...             name='rc_lowpass',
        ...             display_name='RC Low-Pass Filter',
        ...             description='Simple first-order low-pass filter',
        ...             category='filters',
        ...             parameters=[
        ...                 TemplateParameter('fc', 'Cutoff frequency', 'Hz'),
        ...                 TemplateParameter('r', 'Resistance', 'Ω', required=False),
        ...                 TemplateParameter('c', 'Capacitance', 'F', required=False),
        ...             ]
        ...         )
        ...
        ...     def create(self, **params) -> Circuit:
        ...         fc = params['fc']
        ...         r = params.get('r')
        ...         c = params.get('c')
        ...         values = self.calculate_values(fc=fc, r=r, c=c)
        ...         circuit = Circuit('RC Low-Pass Filter')
        ...         circuit.add_resistor('R1', 'in', 'out', values['r'])
        ...         circuit.add_capacitor('C1', 'out', '0', values['c'])
        ...         return circuit
    """

    @classmethod
    @abstractmethod
    def info(cls) -> TemplateInfo:
        """Return template metadata.

        Returns:
            TemplateInfo with name, description, and parameters.
        """
        ...

    @abstractmethod
    def create(self, **params: Any) -> Circuit:
        """Create a circuit from parameters.

        Args:
            **params: Template-specific parameters.

        Returns:
            Configured Circuit instance.
        """
        ...

    @abstractmethod
    def calculate_values(self, **specs: Any) -> dict[str, Any]:
        """Calculate component values from specifications.

        This method implements the design equations for the template.
        For example, for an RC filter: C = 1 / (2π * R * fc)

        Args:
            **specs: Design specifications (e.g., fc, Q, gain).

        Returns:
            Dictionary of component values.
        """
        ...

    def validate_params(self, **params: Any) -> list[str]:
        """Validate parameters against template requirements.

        Args:
            **params: Parameters to validate.

        Returns:
            List of error messages (empty if valid).
        """
        errors = []
        info = self.info()

        for param in info.parameters:
            if param.required and param.name not in params:
                errors.append(f"Missing required parameter: {param.name}")

        return errors
