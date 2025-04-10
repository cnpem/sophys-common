from abc import ABC, abstractmethod


class IEnumValidator(ABC):
    """Abstract base class for enum validation."""

    @abstractmethod
    def is_valid(self, enum_value) -> bool:
        """Check if acquisition time is valid."""
        pass

    @abstractmethod
    def format_to_enum(self, value) -> str:
        """Format an input value to its enum correspondent"""
        pass
