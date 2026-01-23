"""
Tests for Strategy Plugin Interface — BoonMindX Capital Shield
"""

import pytest

from strategies import Action, SignalDecision, Strategy
from strategies.example_strategy import ExampleStrategy
from strategies.integration import generate_strategy_signal
from strategies.registry import (
    get_strategy,
    list_strategies,
    register_strategy,
    StrategyRegistry,
)


class TestSignalDecision:
    """Test SignalDecision dataclass validation."""

    def test_valid_signal_decision(self):
        """Test creating a valid SignalDecision."""
        decision = SignalDecision(
            action=Action.BUY,
            confidence=0.75,
            reason="Test signal",
            meta={"test": True},
        )
        assert decision.action == Action.BUY
        assert decision.confidence == 0.75
        assert decision.reason == "Test signal"
        assert decision.meta == {"test": True}

    def test_confidence_bounds_min(self):
        """Test confidence must be >= 0.0."""
        with pytest.raises(ValueError, match="confidence must be between"):
            SignalDecision(
                action=Action.BUY,
                confidence=-0.1,
                reason="Test",
            )

    def test_confidence_bounds_max(self):
        """Test confidence must be <= 1.0."""
        with pytest.raises(ValueError, match="confidence must be between"):
            SignalDecision(
                action=Action.BUY,
                confidence=1.1,
                reason="Test",
            )

    def test_confidence_bounds_valid(self):
        """Test confidence at bounds is valid."""
        # Min bound
        decision_min = SignalDecision(
            action=Action.HOLD,
            confidence=0.0,
            reason="Test",
        )
        assert decision_min.confidence == 0.0

        # Max bound
        decision_max = SignalDecision(
            action=Action.BUY,
            confidence=1.0,
            reason="Test",
        )
        assert decision_max.confidence == 1.0

    def test_action_enum_required(self):
        """Test action must be Action enum."""
        with pytest.raises(ValueError, match="action must be Action enum"):
            SignalDecision(
                action="BUY",  # type: ignore
                confidence=0.5,
                reason="Test",
            )

    def test_reason_required(self):
        """Test reason must be non-empty string."""
        with pytest.raises(ValueError, match="reason must be a non-empty string"):
            SignalDecision(
                action=Action.HOLD,
                confidence=0.5,
                reason="",
            )

        with pytest.raises(ValueError, match="reason must be a non-empty string"):
            SignalDecision(
                action=Action.HOLD,
                confidence=0.5,
                reason="   ",
            )

    def test_meta_defaults_to_empty_dict(self):
        """Test meta defaults to empty dict."""
        decision = SignalDecision(
            action=Action.HOLD,
            confidence=0.5,
            reason="Test",
        )
        assert decision.meta == {}


class TestStrategyRegistry:
    """Test strategy registry functionality."""

    def test_register_strategy(self):
        """Test registering a strategy."""
        registry = StrategyRegistry()
        strategy = ExampleStrategy()

        registry.register(strategy)
        assert registry.get("example_demo") == strategy

    def test_register_duplicate_strategy(self):
        """Test registering duplicate strategy raises error."""
        registry = StrategyRegistry()
        strategy1 = ExampleStrategy()
        strategy2 = ExampleStrategy()

        registry.register(strategy1)
        with pytest.raises(ValueError, match="already registered"):
            registry.register(strategy2)

    def test_get_strategy(self):
        """Test getting a registered strategy."""
        registry = StrategyRegistry()
        strategy = ExampleStrategy()

        registry.register(strategy)
        assert registry.get("example_demo") == strategy

    def test_get_nonexistent_strategy(self):
        """Test getting nonexistent strategy returns None."""
        registry = StrategyRegistry()
        assert registry.get("nonexistent") is None

    def test_list_strategies(self):
        """Test listing all registered strategies."""
        registry = StrategyRegistry()
        strategy = ExampleStrategy()

        assert registry.list_all() == []
        registry.register(strategy)
        assert "example_demo" in registry.list_all()

    def test_clear_strategies(self):
        """Test clearing all strategies."""
        registry = StrategyRegistry()
        strategy = ExampleStrategy()

        registry.register(strategy)
        assert len(registry.list_all()) == 1
        registry.clear()
        assert len(registry.list_all()) == 0


class TestGlobalRegistry:
    """Test global registry functions."""

    def test_register_strategy_global(self):
        """Test global register_strategy function."""
        # Clear any existing registrations
        registry = StrategyRegistry()
        registry.clear()

        strategy = ExampleStrategy()
        register_strategy(strategy)
        assert get_strategy("example_demo") == strategy

    def test_get_strategy_global(self):
        """Test global get_strategy function."""
        strategy = ExampleStrategy()
        register_strategy(strategy)
        assert get_strategy("example_demo") == strategy

    def test_list_strategies_global(self):
        """Test global list_strategies function."""
        strategy = ExampleStrategy()
        register_strategy(strategy)
        strategies = list_strategies()
        assert "example_demo" in strategies


class TestExampleStrategy:
    """Test example strategy implementation."""

    def test_strategy_properties(self):
        """Test strategy name and version."""
        strategy = ExampleStrategy()
        assert strategy.name == "example_demo"
        assert strategy.version == "1.0.0"

    def test_strategy_generate_signal_hold(self):
        """Test strategy generates HOLD signal with minimal data."""
        strategy = ExampleStrategy()
        market_data = {
            "price_history": [100, 102, 101],
        }

        signal = strategy.generate_signal(market_data)
        assert isinstance(signal, SignalDecision)
        assert signal.action == Action.HOLD
        assert 0.0 <= signal.confidence <= 1.0
        assert "demo" in signal.meta or "DEMO" in signal.reason

    def test_strategy_generate_signal_buy_rsi_low(self):
        """Test strategy generates BUY signal when RSI is low (demo only)."""
        strategy = ExampleStrategy()
        market_data = {
            "price_history": [100, 102, 101, 105, 103],
            "asset": "BTC",
            "rsi": 25,  # Below 30
        }

        signal = strategy.generate_signal(market_data)
        assert isinstance(signal, SignalDecision)
        assert signal.action == Action.BUY
        assert "demo" in signal.meta or "DEMO" in signal.reason

    def test_strategy_generate_signal_sell_rsi_high(self):
        """Test strategy generates SELL signal when RSI is high (demo only)."""
        strategy = ExampleStrategy()
        market_data = {
            "price_history": [100, 102, 101, 105, 103],
            "asset": "BTC",
            "rsi": 75,  # Above 70
        }

        signal = strategy.generate_signal(market_data)
        assert isinstance(signal, SignalDecision)
        assert signal.action == Action.SELL
        assert "demo" in signal.meta or "DEMO" in signal.reason

    def test_strategy_generate_signal_insufficient_data(self):
        """Test strategy handles insufficient data gracefully."""
        strategy = ExampleStrategy()
        market_data = {
            "price_history": [],  # Empty
        }

        signal = strategy.generate_signal(market_data)
        assert isinstance(signal, SignalDecision)
        assert signal.action == Action.HOLD
        assert "insufficient" in signal.reason.lower() or "insufficient" in signal.meta.get("error", "")

    def test_strategy_generate_signal_invalid_input(self):
        """Test strategy handles invalid input gracefully."""
        strategy = ExampleStrategy()

        with pytest.raises(ValueError, match="market_snapshot must be a dictionary"):
            strategy.generate_signal("not a dict")  # type: ignore


class TestStrategyIntegration:
    """Test strategy integration function."""

    def test_generate_strategy_signal_registered(self):
        """Test generating signal with registered strategy."""
        strategy = ExampleStrategy()
        register_strategy(strategy)

        market_data = {
            "price_history": [100, 102, 101, 105, 103],
            "asset": "BTC",
        }

        signal = generate_strategy_signal("example_demo", market_data)
        assert signal is not None
        assert isinstance(signal, SignalDecision)

    def test_generate_strategy_signal_nonexistent(self):
        """Test generating signal with nonexistent strategy returns None."""
        market_data = {
            "price_history": [100, 102, 101],
        }

        signal = generate_strategy_signal("nonexistent_strategy", market_data)
        assert signal is None

    def test_generate_strategy_signal_handles_exceptions(self):
        """Test integration handles strategy exceptions gracefully."""
        # Create a strategy that raises an exception
        class FailingStrategy:
            @property
            def name(self):
                return "failing"

            @property
            def version(self):
                return "1.0.0"

            def generate_signal(self, market_snapshot):
                raise RuntimeError("Strategy failure")

        register_strategy(FailingStrategy())

        market_data = {"price_history": [100, 102]}
        signal = generate_strategy_signal("failing", market_data)
        # Should return None on exception, not raise
        assert signal is None
