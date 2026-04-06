"""Tests for the analyzer module."""

import pytest
from src.analyzer import MetricsAnalyzer


def test_analyzer_initialization():
    """Test that MetricsAnalyzer can be initialized."""
    analyzer = MetricsAnalyzer()
    assert analyzer.data is None


def test_get_summary_no_data():
    """Test get_summary with no data loaded."""
    analyzer = MetricsAnalyzer()
    result = analyzer.get_summary()
    assert result == "No data loaded."
