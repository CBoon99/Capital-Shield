# External Strategy Integration Guide

**Legal-Safe Integration for Third-Party Trading Strategies**

---

## Overview

This guide explains how to integrate external trading strategies into Capital Shield's plugin interface while maintaining legal compliance and code safety.

**Key Principle**: Capital Shield is strategy-agnostic. You bring your own strategy logic, and Capital Shield enforces safety rails.

---

## Strategy Contract Summary

### Action Enum

```python
from strategies import Action

# Three possible actions:
Action.BUY   # Buy signal
Action.SELL  # Sell signal
Action.HOLD  # Hold/no action
```

### SignalDecision

```python
from strategies import SignalDecision, Action

decision = SignalDecision(
    action=Action.BUY,      # Required: Action enum
    confidence=0.75,       # Required: float between 0.0 and 1.0
    reason="Your logic",   # Required: non-empty string
    meta={"key": "value"} # Optional: dict for custom metadata
)
```

### Strategy Protocol

Your strategy must implement:

- `name: str` — Unique strategy identifier
- `version: str` — Strategy version (semantic versioning recommended)
- `generate_signal(market_snapshot: dict) -> SignalDecision` — Signal generation method

---

## Step-by-Step: Wrapping External Logic

### Step 1: License Check (CRITICAL)

**Before importing or copying any external code:**

1. **Identify the license**:
   - Check LICENSE file in the external repository
   - Check package metadata (setup.py, pyproject.toml)
   - Check header comments in source files

2. **Verify compatibility**:
   - ✅ **MIT/Apache 2.0**: Generally safe for commercial use
   - ✅ **BSD**: Generally safe for commercial use
   - ⚠️ **GPL/LGPL**: May require open-sourcing your code (consult legal)
   - ❌ **Proprietary/No License**: Do not use without explicit permission
   - ❌ **Unclear License**: Treat as inspiration only (see "Clean Room" below)

3. **Check attribution requirements**:
   - Some licenses require copyright notices
   - Some require license file inclusion
   - Document all attributions in your code

### Step 2: Choose Integration Method

#### Option A: Adapter Wrapper (RECOMMENDED)

**Prefer this method**: Create an adapter that calls the external module as a dependency.

```python
# my_strategy_adapter.py
from strategies import Action, SignalDecision, StrategyBase

# Import external module as dependency (not copy/paste)
import external_strategy_library  # Must be properly licensed

class MyStrategyAdapter(StrategyBase):
    @property
    def name(self) -> str:
        return "my_strategy_adapter"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    def generate_signal(self, market_snapshot: dict) -> SignalDecision:
        # Call external library (don't copy its code)
        external_result = external_strategy_library.analyze(
            prices=market_snapshot.get("price_history", []),
            volumes=market_snapshot.get("volume_history", [])
        )
        
        # Convert external result to SignalDecision
        if external_result.signal == "buy":
            action = Action.BUY
        elif external_result.signal == "sell":
            action = Action.SELL
        else:
            action = Action.HOLD
        
        return SignalDecision(
            action=action,
            confidence=external_result.confidence,
            reason=f"External strategy: {external_result.reason}",
            meta={
                "external_library": "external_strategy_library",
                "external_version": external_strategy_library.__version__,
                "attribution": "See LICENSE file for external library attribution"
            }
        )
```

**Benefits**:
- Keeps external code separate
- Respects original license
- Easy to update external dependency
- Clear attribution

#### Option B: Clean Room Implementation (For Unclear Licenses)

**If license is unclear or prohibits commercial use**:

1. **Do NOT import or copy the external code**
2. **Treat as inspiration only**
3. **Implement your own logic from scratch**
4. **Document that it's a clean-room implementation**

```python
# my_strategy_cleanroom.py
from strategies import Action, SignalDecision, StrategyBase

class MyStrategyCleanRoom(StrategyBase):
    """
    Clean-room implementation.
    
    This strategy was inspired by [external source] but implemented
    independently without copying or importing external code.
    """
    
    @property
    def name(self) -> str:
        return "my_strategy_cleanroom"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    def generate_signal(self, market_snapshot: dict) -> SignalDecision:
        # Your own implementation (not copied from external source)
        price_history = market_snapshot.get("price_history", [])
        
        if len(price_history) < 2:
            return SignalDecision(
                action=Action.HOLD,
                confidence=0.5,
                reason="Insufficient data",
                meta={}
            )
        
        # Your own logic here (clean-room implementation)
        # ...
        
        return SignalDecision(
            action=Action.BUY,
            confidence=0.75,
            reason="Your own reasoning",
            meta={}
        )
```

### Step 3: Register Your Strategy

```python
from strategies import register_strategy
from my_strategy_adapter import MyStrategyAdapter

strategy = MyStrategyAdapter()
register_strategy(strategy)
```

### Step 4: Use Your Strategy

```python
from strategies import generate_strategy_signal

market_data = {
    "price_history": [100, 102, 101, 105, 103],
    "volume_history": [1000, 1200, 1100, 1300, 1250],
    "asset": "BTC"
}

signal = generate_strategy_signal("my_strategy_adapter", market_data)
if signal:
    print(f"Action: {signal.action}, Confidence: {signal.confidence}")
```

---

## Licensing Checklist

**Before integrating any external code, verify:**

- [ ] **License identified**: I know the exact license of the external code
- [ ] **Commercial use allowed**: License permits commercial use (or I have explicit permission)
- [ ] **Attribution documented**: I've documented all required attributions
- [ ] **License file included**: If required, I've included the license file
- [ ] **No copying if prohibited**: I'm not copying code if license prohibits it
- [ ] **Adapter pattern used**: I'm using an adapter wrapper, not copy/paste
- [ ] **Dependencies declared**: External library is in requirements.txt with version
- [ ] **Legal review**: For GPL/LGPL or unclear licenses, I've consulted legal

### Common License Compatibility

| License | Commercial Use | Attribution Required | Copy Allowed | Adapter OK |
|---------|---------------|---------------------|--------------|------------|
| MIT | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |
| Apache 2.0 | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |
| BSD (3-clause) | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |
| GPL v3 | ⚠️ Consult legal | ✅ Yes | ⚠️ May require open-source | ⚠️ Consult legal |
| LGPL | ⚠️ Consult legal | ✅ Yes | ⚠️ May require open-source | ✅ Usually OK |
| Proprietary | ❌ No (without permission) | N/A | ❌ No | ❌ No |
| Unclear/None | ❌ Treat as inspiration only | N/A | ❌ No | ❌ No |

---

## Clean Room Notes

### When License is Unclear

**If you cannot determine the license of external code:**

1. **Do NOT import it**
2. **Do NOT copy it**
3. **Do NOT use it as a dependency**

**Instead**:
- Treat it as **inspiration only**
- Implement your own logic from scratch
- Document that it's a clean-room implementation
- Keep no trace of the original code in your implementation

### Clean Room Best Practices

- **Separate implementation**: Write your code independently
- **Different approach**: Use different algorithms/methods if possible
- **Document inspiration**: Note that you were inspired by [source] but implemented independently
- **No code similarity**: Avoid copying structure, variable names, or logic flow
- **Legal review**: Consider legal review for high-value integrations

---

## Example: Wrapping a Licensed Library

### Scenario: MIT-Licensed Strategy Library

```python
# requirements.txt
external-strategy-lib==1.2.3  # MIT License

# my_strategy.py
"""
Strategy adapter for external-strategy-lib.

External library: external-strategy-lib v1.2.3
License: MIT (see LICENSE file)
Attribution: Copyright (c) 2023 External Author
"""
from strategies import Action, SignalDecision, StrategyBase
import external_strategy_lib  # MIT-licensed, safe to use

class ExternalStrategyAdapter(StrategyBase):
    @property
    def name(self) -> str:
        return "external_strategy_adapter"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    def generate_signal(self, market_snapshot: dict) -> SignalDecision:
        # Call external library
        result = external_strategy_lib.analyze(
            prices=market_snapshot.get("price_history", []),
            volumes=market_snapshot.get("volume_history", [])
        )
        
        # Convert to SignalDecision
        action_map = {
            "buy": Action.BUY,
            "sell": Action.SELL,
            "hold": Action.HOLD
        }
        
        return SignalDecision(
            action=action_map.get(result.signal, Action.HOLD),
            confidence=result.confidence,
            reason=f"External strategy: {result.reason}",
            meta={
                "external_library": "external-strategy-lib",
                "external_version": "1.2.3",
                "license": "MIT"
            }
        )
```

---

## Legal Disclaimer

**This guide is for informational purposes only and does not constitute legal advice.**

- **Consult legal counsel** for specific licensing questions
- **Verify licenses** before integrating any external code
- **When in doubt, don't use** external code with unclear licenses
- **Prefer clean-room implementations** for unclear or restrictive licenses

---

## Summary

1. **Check license** before importing or copying
2. **Use adapter wrapper** (preferred) over copy/paste
3. **Document attributions** as required by license
4. **Clean room** if license is unclear
5. **Consult legal** for GPL/LGPL or high-value integrations

---

**Last Updated**: 2025-11-16  
**Status**: Legal-safe integration guide
