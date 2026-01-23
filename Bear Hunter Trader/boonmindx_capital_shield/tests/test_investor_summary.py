"""
Tests for investor summary generation
"""
import pytest
from live_sim.reporting import generate_investor_summary


class TestInvestorSummary:
    """Test investor summary generation"""
    
    def test_generate_investor_summary_contains_core_sections(self):
        """Test investor summary contains all required sections"""
        # Create minimal multi_results dict
        multi_results = {
            'datasets': [
                {
                    'dataset_name': 'test_dataset',
                    'baseline': {
                        'portfolio_metrics': {
                            'final_equity': 100000,
                            'pnl_percent': 5.0,
                            'max_drawdown': -0.10,
                            'total_trades': 10
                        }
                    },
                    'preset_scenarios': {
                        'conservative': {
                            'preset_config': {
                                'name': 'CONSERVATIVE',
                                'description': 'Test preset'
                            },
                            'results': {
                                'portfolio_metrics': {
                                    'final_equity': 105000,
                                    'pnl_percent': 5.0,
                                    'max_drawdown': -0.05,
                                    'total_trades': 8
                                },
                                'blocked_trades_count': 2
                            },
                            'comparison': {
                                'differences': {
                                    'pnl_diff_pct': 0.0,
                                    'drawdown_diff': 0.05,
                                    'drawdown_improvement_pct': 50.0
                                }
                            }
                        }
                    }
                }
            ],
            'presets_tested': ['conservative'],
            'total_datasets': 1,
            'engine_mode': 'MOCK'
        }
        
        markdown = generate_investor_summary(multi_results)
        
        # Check key sections exist
        assert 'Executive Summary' in markdown
        assert 'Methodology' in markdown
        assert 'Per-Dataset Summary' in markdown
        assert 'Preset Comparison' in markdown
        assert 'Risk & Limitations' in markdown
        
        # Check dataset header
        assert 'test_dataset' in markdown or 'Dataset:' in markdown
        
        # Check preset names present
        assert 'CONSERVATIVE' in markdown or 'conservative' in markdown
        
        # Check key phrases
        assert 'datasets' in markdown.lower()
        assert 'baseline' in markdown.lower()
    
    def test_generate_investor_summary_handles_empty_datasets(self):
        """Test investor summary handles empty dataset list"""
        multi_results = {
            'datasets': [],
            'presets_tested': ['conservative'],
            'total_datasets': 0
        }
        
        markdown = generate_investor_summary(multi_results)
        
        # Should still generate report structure
        assert 'Executive Summary' in markdown
        assert '0 datasets' in markdown or '0' in markdown
    
    def test_generate_investor_summary_includes_aggregate_stats(self):
        """Test investor summary includes aggregate statistics"""
        multi_results = {
            'datasets': [
                {
                    'dataset_name': 'dataset1',
                    'baseline': {
                        'portfolio_metrics': {
                            'final_equity': 100000,
                            'pnl_percent': 0.0,
                            'max_drawdown': -0.20,
                            'total_trades': 10
                        }
                    },
                    'preset_scenarios': {
                        'conservative': {
                            'preset_config': {'name': 'CONSERVATIVE'},
                            'results': {
                                'portfolio_metrics': {
                                    'final_equity': 100000,
                                    'pnl_percent': 0.0,
                                    'max_drawdown': -0.10,
                                    'total_trades': 8
                                }
                            },
                            'comparison': {
                                'differences': {
                                    'drawdown_improvement_pct': 50.0,
                                    'pnl_diff_pct': 0.0
                                }
                            }
                        }
                    }
                },
                {
                    'dataset_name': 'dataset2',
                    'baseline': {
                        'portfolio_metrics': {
                            'final_equity': 100000,
                            'pnl_percent': 0.0,
                            'max_drawdown': -0.15,
                            'total_trades': 10
                        }
                    },
                    'preset_scenarios': {
                        'conservative': {
                            'preset_config': {'name': 'CONSERVATIVE'},
                            'results': {
                                'portfolio_metrics': {
                                    'final_equity': 100000,
                                    'pnl_percent': 0.0,
                                    'max_drawdown': -0.08,
                                    'total_trades': 8
                                }
                            },
                            'comparison': {
                                'differences': {
                                    'drawdown_improvement_pct': 46.7,
                                    'pnl_diff_pct': 0.0
                                }
                            }
                        }
                    }
                }
            ],
            'presets_tested': ['conservative'],
            'total_datasets': 2
        }
        
        markdown = generate_investor_summary(multi_results)
        
        # Should include aggregate statistics
        assert 'Average' in markdown or 'average' in markdown
        assert 'datasets' in markdown.lower()

