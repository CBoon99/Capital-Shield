"""
Relative Survival Alpha (RSA) Calculation

RSA is a composite metric that balances terminal equity performance
against maximum drawdown, providing a single score for strategy survival quality.

Formula (v1 locked 2025-11-16):
    TE_norm  = clamp(terminal_equity / initial_equity, 0.0, 2.0) mapped to [0, 1]
    MDD_norm = max_drawdown_fraction in [0, 1] (e.g., 0.35 for -35%)
    RSA = 0.5 * TE_norm + 0.5 * (1.0 - MDD_norm)

Interpretation:
    - RSA near 1.0: High terminal equity + low drawdown (excellent survival)
    - RSA near 0.5: Break-even equity + moderate drawdown (neutral)
    - RSA near 0.0: Low terminal equity or catastrophic drawdown (poor survival)
"""

def calculate_rsa(
    terminal_equity: float,
    initial_equity: float,
    max_drawdown_fraction: float
) -> float:
    """
    Calculate Relative Survival Alpha (RSA).
    
    Args:
        terminal_equity: Final equity value
        initial_equity: Starting equity value
        max_drawdown_fraction: Maximum drawdown as a fraction (0.0 to 1.0)
                               e.g., 0.35 for -35% drawdown
    
    Returns:
        RSA score between 0.0 and 1.0
    
    Examples:
        >>> calculate_rsa(15000, 10000, 0.10)  # +50% return, -10% MDD
        0.7  # (0.5 * 1.0) + (0.5 * 0.9)
        
        >>> calculate_rsa(10000, 10000, 0.35)  # Break-even, -35% MDD
        0.325  # (0.5 * 0.0) + (0.5 * 0.65)
        
        >>> calculate_rsa(5000, 10000, 0.60)  # -50% loss, -60% MDD
        0.0  # (0.5 * 0.0) + (0.5 * 0.4) = 0.2, but clamped
    """
    if initial_equity <= 0:
        raise ValueError("initial_equity must be positive")
    
    if not (0.0 <= max_drawdown_fraction <= 1.0):
        raise ValueError("max_drawdown_fraction must be between 0.0 and 1.0")
    
    # Terminal equity component: clamp to [0, 2] then normalize to [0, 1]
    te_ratio = terminal_equity / initial_equity
    te_clamped = max(0.0, min(2.0, te_ratio))
    te_norm = te_clamped / 2.0
    
    # Max drawdown component: convert drawdown to survival score
    mdd_norm = max_drawdown_fraction
    survival_score = 1.0 - mdd_norm
    
    # RSA: equal weighting of terminal equity and drawdown survival
    rsa = 0.5 * te_norm + 0.5 * survival_score
    
    return max(0.0, min(1.0, rsa))


def rsa_to_grade(rsa: float) -> str:
    """
    Convert RSA score to a letter grade for reporting.
    
    Args:
        rsa: RSA score between 0.0 and 1.0
    
    Returns:
        Letter grade (A+, A, B+, B, C+, C, D, F)
    """
    if rsa >= 0.95:
        return "A+"
    elif rsa >= 0.85:
        return "A"
    elif rsa >= 0.75:
        return "B+"
    elif rsa >= 0.65:
        return "B"
    elif rsa >= 0.55:
        return "C+"
    elif rsa >= 0.45:
        return "C"
    elif rsa >= 0.35:
        return "D"
    else:
        return "F"


def calculate_rsa_from_metrics(metrics: dict) -> float:
    """
    Calculate RSA from a standard metrics dictionary.
    
    Args:
        metrics: Dictionary containing:
            - 'final_equity' or 'terminal_equity'
            - 'starting_capital' or 'initial_equity'
            - 'max_drawdown' (as fraction, e.g., 0.35 for -35%)
    
    Returns:
        RSA score between 0.0 and 1.0
    
    Raises:
        KeyError: If required metrics are missing
    """
    terminal_equity = metrics.get('final_equity') or metrics.get('terminal_equity')
    initial_equity = metrics.get('starting_capital') or metrics.get('initial_equity')
    max_drawdown = abs(metrics.get('max_drawdown', 0.0))
    
    if terminal_equity is None:
        raise KeyError("metrics must contain 'final_equity' or 'terminal_equity'")
    if initial_equity is None:
        raise KeyError("metrics must contain 'starting_capital' or 'initial_equity'")
    
    return calculate_rsa(terminal_equity, initial_equity, max_drawdown)

