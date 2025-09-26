"""
SYMBI Replication Kit

A comprehensive toolkit for replicating SYMBI protocol research,
conducting A/B tests, and analyzing constitutional AI interactions.

This package provides:
- A/B testing framework for SYMBI vs directive prompting
- CIQ (Clarity, Integrity, Quality) metric calculation
- Trust Receipt validation and analysis
- Statistical analysis tools for research replication
- Visualization utilities for results presentation

License: CC BY-NC-SA 4.0
"""

__version__ = "1.0.0"
__author__ = "SYMBI Core Protocol"
__email__ = "research@symbi.world"

from .ab_testing import ABTestFramework, SymbiTest, DirectiveTest
from .ciq_metrics import CIQCalculator, ClarityMetric, IntegrityMetric, QualityMetric
from .trust_receipts import TrustReceiptValidator, ReceiptAnalyzer
from .statistical_analysis import StatisticalAnalyzer, EffectSizeCalculator
from .visualization import ResultsVisualizer, CIQDashboard

__all__ = [
    "ABTestFramework",
    "SymbiTest", 
    "DirectiveTest",
    "CIQCalculator",
    "ClarityMetric",
    "IntegrityMetric", 
    "QualityMetric",
    "TrustReceiptValidator",
    "ReceiptAnalyzer",
    "StatisticalAnalyzer",
    "EffectSizeCalculator",
    "ResultsVisualizer",
    "CIQDashboard",
]