"""
Strategy Registry — BoonMindX Capital Shield

Manages registration and retrieval of strategy plugins.
"""

from typing import Dict, List, Optional

from .strategy_base import Strategy


class StrategyRegistry:
    """Registry for managing strategy plugins."""

    def __init__(self):
        """Initialize empty registry."""
        self._strategies: Dict[str, Strategy] = {}

    def register(self, strategy: Strategy) -> None:
        """
        Register a strategy plugin.

        Args:
            strategy: Strategy instance implementing Strategy protocol

        Raises:
            ValueError: If strategy name is already registered
        """
        if not strategy.name:
            raise ValueError("Strategy must have a non-empty name")
        if strategy.name in self._strategies:
            raise ValueError(f"Strategy '{strategy.name}' is already registered")
        self._strategies[strategy.name] = strategy

    def get(self, name: str) -> Optional[Strategy]:
        """
        Get a registered strategy by name.

        Args:
            name: Strategy name

        Returns:
            Strategy instance if found, None otherwise
        """
        return self._strategies.get(name)

    def list_all(self) -> List[str]:
        """
        List all registered strategy names.

        Returns:
            List of strategy names
        """
        return list(self._strategies.keys())

    def clear(self) -> None:
        """Clear all registered strategies (for testing)."""
        self._strategies.clear()


# Global registry instance
_registry = StrategyRegistry()


def register_strategy(strategy: Strategy) -> None:
    """
    Register a strategy plugin in the global registry.

    Args:
        strategy: Strategy instance implementing Strategy protocol

    Raises:
        ValueError: If strategy name is already registered
    """
    _registry.register(strategy)


def get_strategy(name: str) -> Optional[Strategy]:
    """
    Get a registered strategy by name.

    Args:
        name: Strategy name

    Returns:
        Strategy instance if found, None otherwise
    """
    return _registry.get(name)


def list_strategies() -> List[str]:
    """
    List all registered strategy names.

    Returns:
        List of strategy names
    """
    return _registry.list_all()
