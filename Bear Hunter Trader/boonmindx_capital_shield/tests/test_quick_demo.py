"""
Tests for quick demo runner
"""
import os
import tempfile
import pytest
from pathlib import Path
from live_sim.quick_demo import main


class TestQuickDemo:
    """Test quick demo functionality"""
    
    def test_quick_demo_creates_output_files(self, tmp_path, monkeypatch):
        """Test that quick demo creates expected output files"""
        # Change to temp directory
        monkeypatch.chdir(tmp_path)
        
        # Run demo (may take a moment)
        main()
        
        # Check files exist
        json_path = tmp_path / "demo_multi_validation_summary.json"
        markdown_path = tmp_path / "DEMO_INVESTOR_VALIDATION_REPORT.md"
        
        assert json_path.exists(), "JSON summary should be created"
        assert markdown_path.exists(), "Markdown report should be created"
        
        # Check JSON structure
        import json
        with open(json_path) as f:
            summary = json.load(f)
        
        assert 'datasets' in summary
        assert 'presets_tested' in summary
        assert 'total_datasets' in summary
        
        # Check Markdown content
        with open(markdown_path) as f:
            markdown = f.read()
        
        assert 'Executive Summary' in markdown
        assert 'Methodology' in markdown
        assert 'CONSERVATIVE' in markdown or 'conservative' in markdown
        assert 'BALANCED' in markdown or 'balanced' in markdown
        assert 'AGGRESSIVE' in markdown or 'aggressive' in markdown
    
    def test_quick_demo_is_self_contained(self, tmp_path, monkeypatch):
        """Test that demo doesn't require external files"""
        # Change to temp directory (empty)
        monkeypatch.chdir(tmp_path)
        
        # Should run without external CSV files
        main()
        
        # Should have created output files
        assert (tmp_path / "demo_multi_validation_summary.json").exists()
        assert (tmp_path / "DEMO_INVESTOR_VALIDATION_REPORT.md").exists()

