"""
Strategy Base Interface — BoonMindX Capital Shield

Defines the contract for trading strategy plugins.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Protocol


class Action(str, Enum):
    """Trading action types."""

    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


@dataclass
class SignalDecision:
    """
    Signal decision from a strategy.

    Attributes:
        action: Trading action (BUY, SELL, or HOLD)
        confidence: Confidence level (0.0 to 1.0)
        reason: Human-readable reason for the decision
        meta: Optional metadata dictionary
    """

    action: Action
    confidence: float
    reason: str
    meta: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate SignalDecision fields."""
        if not isinstance(self.action, Action):
            raise ValueError(f"action must be Action enum, got {type(self.action)}")
        if not (0.0 <= self.confidence <= 1.0):
            raise ValueError(f"confidence must be between 0.0 and 1.0, got {self.confidence}")
        if not isinstance(self.reason, str) or not self.reason.strip():
            raise ValueError("reason must be a non-empty string")
        if not isinstance(self.meta, dict):
            raise ValueError(f"meta must be a dict, got {type(self.meta)}")


class Strategy(Protocol):
    """
    Protocol for trading strategy plugins.

    Strategies generate signals based on market data. Capital Shield
    then evaluates these signals against safety rails before execution.
    """

    @property
    def name(self) -> str:
        """Strategy name (unique identifier)."""
        ...

    @property
    def version(self) -> str:
        """Strategy version (semantic versioning recommended)."""
        ...

    def generate_signal(self, market_snapshot: Dict[str, Any]) -> SignalDecision:
        """
        Generate a trading signal based on market data.

        Args:
            market_snapshot: Dictionary containing market data:
                - price_history: List of prices
                - volume_history: List of volumes (optional)
                - asset: Asset symbol (optional)
                - Additional strategy-specific fields (optional)

        Returns:
            SignalDecision with action, confidence, reason, and optional metadata

        Raises:
            ValueError: If market_snapshot is invalid or missing required fields
        """
        ...


class StrategyBase(ABC):
    """
    Abstract base class for strategy implementations.

    Provides a concrete base class for strategies that prefer inheritance
    over Protocol. Implements Strategy protocol.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Strategy name (unique identifier)."""
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        """Strategy version (semantic versioning recommended)."""
        pass

    @abstractmethod
    def generate_signal(self, market_snapshot: Dict[str, Any]) -> SignalDecision:
        """
        Generate a trading signal based on market data.

        Args:
            market_snapshot: Dictionary containing market data

        Returns:
            SignalDecision with action, confidence, reason, and optional metadata
        """
        pass
