"""
Strategy Plugin Interface — BoonMindX Capital Shield

This module provides a plugin interface for external trading strategies.
Strategies generate signals (BUY/SELL/HOLD) that are then evaluated by
Capital Shield's safety rails before execution.
"""

from .strategy_base import Action, SignalDecision, Strategy
from .registry import register_strategy, get_strategy, list_strategies

__all__ = [
    "Action",
    "SignalDecision",
    "Strategy",
    "register_strategy",
    "get_strategy",
    "list_strategies",
]
