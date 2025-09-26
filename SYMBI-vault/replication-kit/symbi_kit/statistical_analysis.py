"""
Statistical Analysis: Research validation and hypothesis testing

This module provides statistical tools for validating SYMBI research
hypotheses and analyzing experimental results.
"""

import numpy as np
import pandas as pd
from scipy import stats
from scipy.stats import ttest_ind, mannwhitneyu, chi2_contingency, pearsonr
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import cohen_kappa_score
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import warnings


@dataclass
class StatisticalResult:
    """Result of a statistical test."""
    test_name: str
    statistic: float
    p_value: float
    effect_size: Optional[float]
    confidence_interval: Optional[Tuple[float, float]]
    interpretation: str
    significant: bool
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'test_name': self.test_name,
            'statistic': self.statistic,
            'p_value': self.p_value,
            'effect_size': self.effect_size,
            'confidence_interval': self.confidence_interval,
            'interpretation': self.interpretation,
            'significant': self.significant
        }


@dataclass
class ExperimentalData:
    """Container for experimental data."""
    constitutional_group: List[Dict[str, Any]]
    directive_group: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    
    def get_constitutional_ciq(self) -> Dict[str, List[float]]:
        """Extract CIQ metrics from constitutional group."""
        return self._extract_ciq_metrics(self.constitutional_group)
    
    def get_directive_ciq(self) -> Dict[str, List[float]]:
        """Extract CIQ metrics from directive group."""
        return self._extract_ciq_metrics(self.directive_group)
    
    def _extract_ciq_metrics(self, group: List[Dict[str, Any]]) -> Dict[str, List[float]]:
        """Extract CIQ metrics from a group."""
        metrics = {
            'clarity': [],
            'integrity': [],
            'quality': [],
            'composite': []
        }
        
        for interaction in group:
            ciq = interaction.get('ciq_metrics', {})
            metrics['clarity'].append(ciq.get('clarity', 0.0))
            metrics['integrity'].append(ciq.get('integrity', 0.0))
            metrics['quality'].append(ciq.get('quality', 0.0))
            
            # Calculate composite score
            composite = (
                ciq.get('clarity', 0.0) + 
                ciq.get('integrity', 0.0) + 
                ciq.get('quality', 0.0)
            ) / 3
            metrics['composite'].append(composite)
        
        return metrics


class HypothesisTest:
    """Base class for hypothesis testing."""
    
    def __init__(self, alpha: float = 0.05):
        """
        Initialize hypothesis test.
        
        Args:
            alpha: Significance level (default 0.05)
        """
        self.alpha = alpha
    
    def test_ciq_superiority(self, data: ExperimentalData) -> Dict[str, StatisticalResult]:
        """
        Test hypothesis that constitutional AI produces superior CIQ metrics.
        
        H0: Constitutional CIQ <= Directive CIQ
        H1: Constitutional CIQ > Directive CIQ (one-tailed)
        
        Args:
            data: Experimental data
            
        Returns:
            Dictionary of statistical results for each CIQ metric
        """
        constitutional_ciq = data.get_constitutional_ciq()
        directive_ciq = data.get_directive_ciq()
        
        results = {}
        
        for metric in ['clarity', 'integrity', 'quality', 'composite']:
            const_values = constitutional_ciq[metric]
            dir_values = directive_ciq[metric]
            
            # Perform one-tailed t-test
            result = self._perform_superiority_test(
                const_values, dir_values, metric
            )
            results[metric] = result
        
        return results
    
    def test_consistency_improvement(self, data: ExperimentalData) -> StatisticalResult:
        """
        Test hypothesis that constitutional AI improves consistency.
        
        Args:
            data: Experimental data
            
        Returns:
            Statistical result for consistency test
        """
        const_ciq = data.get_constitutional_ciq()
        dir_ciq = data.get_directive_ciq()
        
        # Calculate coefficient of variation for each group
        const_cv = self._calculate_coefficient_variation(const_ciq['composite'])
        dir_cv = self._calculate_coefficient_variation(dir_ciq['composite'])
        
        # Test if constitutional has lower CV (more consistent)
        # Using F-test for variance comparison
        const_var = np.var(const_ciq['composite'], ddof=1)
        dir_var = np.var(dir_ciq['composite'], ddof=1)
        
        f_stat = dir_var / const_var if const_var > 0 else float('inf')
        df1 = len(dir_ciq['composite']) - 1
        df2 = len(const_ciq['composite']) - 1
        
        p_value = 1 - stats.f.cdf(f_stat, df1, df2)
        
        effect_size = (dir_cv - const_cv) / max(dir_cv, const_cv) if max(dir_cv, const_cv) > 0 else 0
        
        interpretation = self._interpret_consistency_result(
            const_cv, dir_cv, p_value, self.alpha
        )
        
        return StatisticalResult(
            test_name="Consistency Improvement Test (F-test)",
            statistic=f_stat,
            p_value=p_value,
            effect_size=effect_size,
            confidence_interval=None,
            interpretation=interpretation,
            significant=p_value < self.alpha
        )
    
    def test_learning_curve(self, data: ExperimentalData) -> Dict[str, StatisticalResult]:
        """
        Test hypothesis that constitutional AI shows better learning curves.
        
        Args:
            data: Experimental data
            
        Returns:
            Statistical results for learning curve analysis
        """
        results = {}
        
        # Test constitutional group learning
        const_learning = self._analyze_learning_curve(data.constitutional_group)
        results['constitutional_learning'] = const_learning
        
        # Test directive group learning
        dir_learning = self._analyze_learning_curve(data.directive_group)
        results['directive_learning'] = dir_learning
        
        # Compare learning rates
        comparison = self._compare_learning_rates(
            data.constitutional_group, data.directive_group
        )
        results['learning_comparison'] = comparison
        
        return results
    
    def _perform_superiority_test(self, group1: List[float], group2: List[float], 
                                 metric_name: str) -> StatisticalResult:
        """Perform one-tailed superiority test."""
        if not group1 or not group2:
            return StatisticalResult(
                test_name=f"{metric_name.title()} Superiority Test",
                statistic=0.0,
                p_value=1.0,
                effect_size=0.0,
                confidence_interval=None,
                interpretation="Insufficient data for analysis",
                significant=False
            )
        
        # Check normality
        _, p_norm1 = stats.shapiro(group1) if len(group1) > 3 else (0, 0.1)
        _, p_norm2 = stats.shapiro(group2) if len(group2) > 3 else (0, 0.1)
        
        # Choose appropriate test
        if p_norm1 > 0.05 and p_norm2 > 0.05 and len(group1) > 10 and len(group2) > 10:
            # Use t-test for normal data
            statistic, p_value_two_tailed = ttest_ind(group1, group2, equal_var=False)
            p_value = p_value_two_tailed / 2 if statistic > 0 else 1 - (p_value_two_tailed / 2)
            test_name = f"{metric_name.title()} Superiority Test (Welch's t-test)"
        else:
            # Use Mann-Whitney U test for non-normal data
            statistic, p_value_two_tailed = mannwhitneyu(
                group1, group2, alternative='two-sided'
            )
            # Convert to one-tailed
            _, p_value = mannwhitneyu(group1, group2, alternative='greater')
            test_name = f"{metric_name.title()} Superiority Test (Mann-Whitney U)"
        
        # Calculate effect size (Cohen's d)
        effect_size = self._calculate_cohens_d(group1, group2)
        
        # Calculate confidence interval for difference in means
        ci = self._calculate_difference_ci(group1, group2)
        
        interpretation = self._interpret_superiority_result(
            np.mean(group1), np.mean(group2), p_value, effect_size, self.alpha
        )
        
        return StatisticalResult(
            test_name=test_name,
            statistic=statistic,
            p_value=p_value,
            effect_size=effect_size,
            confidence_interval=ci,
            interpretation=interpretation,
            significant=p_value < self.alpha
        )
    
    def _calculate_coefficient_variation(self, values: List[float]) -> float:
        """Calculate coefficient of variation."""
        if not values:
            return 0.0
        
        mean_val = np.mean(values)
        std_val = np.std(values, ddof=1)
        
        return std_val / mean_val if mean_val != 0 else 0.0
    
    def _analyze_learning_curve(self, interactions: List[Dict[str, Any]]) -> StatisticalResult:
        """Analyze learning curve for a group of interactions."""
        if len(interactions) < 3:
            return StatisticalResult(
                test_name="Learning Curve Analysis",
                statistic=0.0,
                p_value=1.0,
                effect_size=0.0,
                confidence_interval=None,
                interpretation="Insufficient data for learning curve analysis",
                significant=False
            )
        
        # Extract CIQ composite scores over time
        ciq_scores = []
        for interaction in interactions:
            ciq = interaction.get('ciq_metrics', {})
            composite = (
                ciq.get('clarity', 0.0) + 
                ciq.get('integrity', 0.0) + 
                ciq.get('quality', 0.0)
            ) / 3
            ciq_scores.append(composite)
        
        # Perform linear regression to test for trend
        x = np.arange(len(ciq_scores))
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, ciq_scores)
        
        interpretation = self._interpret_learning_curve(slope, p_value, r_value, self.alpha)
        
        return StatisticalResult(
            test_name="Learning Curve Analysis (Linear Regression)",
            statistic=slope,
            p_value=p_value,
            effect_size=r_value,  # Using correlation as effect size
            confidence_interval=(slope - 1.96 * std_err, slope + 1.96 * std_err),
            interpretation=interpretation,
            significant=p_value < self.alpha
        )
    
    def _compare_learning_rates(self, const_group: List[Dict[str, Any]], 
                               dir_group: List[Dict[str, Any]]) -> StatisticalResult:
        """Compare learning rates between groups."""
        # Calculate learning rates for each group
        const_rate = self._calculate_learning_rate(const_group)
        dir_rate = self._calculate_learning_rate(dir_group)
        
        # Simple comparison (could be enhanced with more sophisticated methods)
        rate_difference = const_rate - dir_rate
        
        # Use bootstrap to estimate confidence interval
        ci = self._bootstrap_learning_rate_difference(const_group, dir_group)
        
        # Simple significance test (rate difference vs 0)
        p_value = 0.05 if abs(rate_difference) > 0.01 else 0.5  # Simplified
        
        interpretation = self._interpret_learning_rate_comparison(
            const_rate, dir_rate, p_value, self.alpha
        )
        
        return StatisticalResult(
            test_name="Learning Rate Comparison",
            statistic=rate_difference,
            p_value=p_value,
            effect_size=rate_difference,
            confidence_interval=ci,
            interpretation=interpretation,
            significant=p_value < self.alpha
        )
    
    def _calculate_learning_rate(self, interactions: List[Dict[str, Any]]) -> float:
        """Calculate learning rate from interactions."""
        if len(interactions) < 2:
            return 0.0
        
        ciq_scores = []
        for interaction in interactions:
            ciq = interaction.get('ciq_metrics', {})
            composite = (
                ciq.get('clarity', 0.0) + 
                ciq.get('integrity', 0.0) + 
                ciq.get('quality', 0.0)
            ) / 3
            ciq_scores.append(composite)
        
        # Calculate slope of linear regression
        x = np.arange(len(ciq_scores))
        slope, _, _, _, _ = stats.linregress(x, ciq_scores)
        
        return slope
    
    def _bootstrap_learning_rate_difference(self, const_group: List[Dict[str, Any]], 
                                          dir_group: List[Dict[str, Any]], 
                                          n_bootstrap: int = 1000) -> Tuple[float, float]:
        """Bootstrap confidence interval for learning rate difference."""
        differences = []
        
        for _ in range(n_bootstrap):
            # Resample with replacement
            const_sample = np.random.choice(len(const_group), len(const_group), replace=True)
            dir_sample = np.random.choice(len(dir_group), len(dir_group), replace=True)
            
            const_resampled = [const_group[i] for i in const_sample]
            dir_resampled = [dir_group[i] for i in dir_sample]
            
            const_rate = self._calculate_learning_rate(const_resampled)
            dir_rate = self._calculate_learning_rate(dir_resampled)
            
            differences.append(const_rate - dir_rate)
        
        # Calculate 95% confidence interval
        ci_lower = np.percentile(differences, 2.5)
        ci_upper = np.percentile(differences, 97.5)
        
        return (ci_lower, ci_upper)
    
    def _calculate_cohens_d(self, group1: List[float], group2: List[float]) -> float:
        """Calculate Cohen's d effect size."""
        if not group1 or not group2:
            return 0.0
        
        n1, n2 = len(group1), len(group2)
        mean1, mean2 = np.mean(group1), np.mean(group2)
        var1, var2 = np.var(group1, ddof=1), np.var(group2, ddof=1)
        
        # Pooled standard deviation
        pooled_std = np.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))
        
        if pooled_std == 0:
            return 0.0
        
        return (mean1 - mean2) / pooled_std
    
    def _calculate_difference_ci(self, group1: List[float], group2: List[float], 
                               confidence: float = 0.95) -> Tuple[float, float]:
        """Calculate confidence interval for difference in means."""
        if not group1 or not group2:
            return (0.0, 0.0)
        
        n1, n2 = len(group1), len(group2)
        mean1, mean2 = np.mean(group1), np.mean(group2)
        var1, var2 = np.var(group1, ddof=1), np.var(group2, ddof=1)
        
        # Standard error of difference
        se_diff = np.sqrt(var1/n1 + var2/n2)
        
        # Degrees of freedom (Welch's formula)
        df = (var1/n1 + var2/n2)**2 / ((var1/n1)**2/(n1-1) + (var2/n2)**2/(n2-1))
        
        # Critical t-value
        alpha = 1 - confidence
        t_crit = stats.t.ppf(1 - alpha/2, df)
        
        # Confidence interval
        diff = mean1 - mean2
        margin = t_crit * se_diff
        
        return (diff - margin, diff + margin)
    
    def _interpret_superiority_result(self, mean1: float, mean2: float, 
                                    p_value: float, effect_size: float, 
                                    alpha: float) -> str:
        """Interpret superiority test result."""
        if p_value < alpha:
            if effect_size < 0.2:
                effect_desc = "small"
            elif effect_size < 0.5:
                effect_desc = "medium"
            else:
                effect_desc = "large"
            
            return (f"Constitutional AI significantly outperforms directive AI "
                   f"(p={p_value:.4f}, Cohen's d={effect_size:.3f}, {effect_desc} effect)")
        else:
            return (f"No significant difference found between constitutional and directive AI "
                   f"(p={p_value:.4f})")
    
    def _interpret_consistency_result(self, const_cv: float, dir_cv: float, 
                                    p_value: float, alpha: float) -> str:
        """Interpret consistency test result."""
        if p_value < alpha:
            improvement = ((dir_cv - const_cv) / dir_cv) * 100
            return (f"Constitutional AI shows significantly better consistency "
                   f"(CV: {const_cv:.3f} vs {dir_cv:.3f}, {improvement:.1f}% improvement, "
                   f"p={p_value:.4f})")
        else:
            return (f"No significant difference in consistency "
                   f"(CV: {const_cv:.3f} vs {dir_cv:.3f}, p={p_value:.4f})")
    
    def _interpret_learning_curve(self, slope: float, p_value: float, 
                                r_value: float, alpha: float) -> str:
        """Interpret learning curve analysis."""
        if p_value < alpha:
            if slope > 0:
                trend = "positive learning trend"
            else:
                trend = "negative learning trend"
            
            strength = "strong" if abs(r_value) > 0.7 else "moderate" if abs(r_value) > 0.3 else "weak"
            
            return (f"Significant {trend} detected "
                   f"(slope={slope:.4f}, r={r_value:.3f}, {strength} correlation, "
                   f"p={p_value:.4f})")
        else:
            return (f"No significant learning trend detected "
                   f"(slope={slope:.4f}, p={p_value:.4f})")
    
    def _interpret_learning_rate_comparison(self, const_rate: float, dir_rate: float, 
                                          p_value: float, alpha: float) -> str:
        """Interpret learning rate comparison."""
        if p_value < alpha:
            if const_rate > dir_rate:
                return (f"Constitutional AI shows significantly faster learning "
                       f"(rate: {const_rate:.4f} vs {dir_rate:.4f}, p={p_value:.4f})")
            else:
                return (f"Directive AI shows significantly faster learning "
                       f"(rate: {dir_rate:.4f} vs {const_rate:.4f}, p={p_value:.4f})")
        else:
            return (f"No significant difference in learning rates "
                   f"({const_rate:.4f} vs {dir_rate:.4f}, p={p_value:.4f})")


class PowerAnalysis:
    """Statistical power analysis for experimental design."""
    
    def __init__(self):
        """Initialize power analysis."""
        pass
    
    def calculate_sample_size(self, effect_size: float, power: float = 0.8, 
                            alpha: float = 0.05) -> int:
        """
        Calculate required sample size for detecting an effect.
        
        Args:
            effect_size: Expected Cohen's d effect size
            power: Desired statistical power (default 0.8)
            alpha: Significance level (default 0.05)
            
        Returns:
            Required sample size per group
        """
        # Using approximation for two-sample t-test
        z_alpha = stats.norm.ppf(1 - alpha/2)
        z_beta = stats.norm.ppf(power)
        
        n = 2 * ((z_alpha + z_beta) / effect_size) ** 2
        
        return int(np.ceil(n))
    
    def calculate_power(self, n: int, effect_size: float, alpha: float = 0.05) -> float:
        """
        Calculate statistical power for given sample size and effect size.
        
        Args:
            n: Sample size per group
            effect_size: Cohen's d effect size
            alpha: Significance level
            
        Returns:
            Statistical power
        """
        z_alpha = stats.norm.ppf(1 - alpha/2)
        delta = effect_size * np.sqrt(n/2)
        
        power = 1 - stats.norm.cdf(z_alpha - delta) + stats.norm.cdf(-z_alpha - delta)
        
        return power
    
    def minimum_detectable_effect(self, n: int, power: float = 0.8, 
                                 alpha: float = 0.05) -> float:
        """
        Calculate minimum detectable effect size.
        
        Args:
            n: Sample size per group
            power: Desired power
            alpha: Significance level
            
        Returns:
            Minimum detectable Cohen's d
        """
        z_alpha = stats.norm.ppf(1 - alpha/2)
        z_beta = stats.norm.ppf(power)
        
        effect_size = (z_alpha + z_beta) * np.sqrt(2/n)
        
        return effect_size


class DescriptiveAnalysis:
    """Descriptive statistical analysis of experimental data."""
    
    def __init__(self):
        """Initialize descriptive analysis."""
        pass
    
    def summarize_groups(self, data: ExperimentalData) -> Dict[str, Any]:
        """
        Generate descriptive statistics for both groups.
        
        Args:
            data: Experimental data
            
        Returns:
            Summary statistics
        """
        const_ciq = data.get_constitutional_ciq()
        dir_ciq = data.get_directive_ciq()
        
        summary = {
            'constitutional': self._calculate_group_stats(const_ciq),
            'directive': self._calculate_group_stats(dir_ciq),
            'comparison': self._compare_groups(const_ciq, dir_ciq)
        }
        
        return summary
    
    def _calculate_group_stats(self, ciq_metrics: Dict[str, List[float]]) -> Dict[str, Any]:
        """Calculate descriptive statistics for a group."""
        stats_dict = {}
        
        for metric, values in ciq_metrics.items():
            if values:
                stats_dict[metric] = {
                    'n': len(values),
                    'mean': np.mean(values),
                    'std': np.std(values, ddof=1),
                    'median': np.median(values),
                    'min': np.min(values),
                    'max': np.max(values),
                    'q25': np.percentile(values, 25),
                    'q75': np.percentile(values, 75),
                    'cv': np.std(values, ddof=1) / np.mean(values) if np.mean(values) != 0 else 0
                }
            else:
                stats_dict[metric] = {
                    'n': 0,
                    'mean': 0,
                    'std': 0,
                    'median': 0,
                    'min': 0,
                    'max': 0,
                    'q25': 0,
                    'q75': 0,
                    'cv': 0
                }
        
        return stats_dict
    
    def _compare_groups(self, const_ciq: Dict[str, List[float]], 
                      dir_ciq: Dict[str, List[float]]) -> Dict[str, Any]:
        """Compare descriptive statistics between groups."""
        comparison = {}
        
        for metric in const_ciq.keys():
            const_values = const_ciq[metric]
            dir_values = dir_ciq[metric]
            
            if const_values and dir_values:
                const_mean = np.mean(const_values)
                dir_mean = np.mean(dir_values)
                
                comparison[metric] = {
                    'mean_difference': const_mean - dir_mean,
                    'percent_improvement': ((const_mean - dir_mean) / dir_mean * 100) if dir_mean != 0 else 0,
                    'const_better': const_mean > dir_mean
                }
            else:
                comparison[metric] = {
                    'mean_difference': 0,
                    'percent_improvement': 0,
                    'const_better': False
                }
        
        return comparison


class VisualizationTools:
    """Tools for visualizing statistical results."""
    
    def __init__(self):
        """Initialize visualization tools."""
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
    
    def plot_ciq_comparison(self, data: ExperimentalData, 
                           save_path: Optional[str] = None) -> None:
        """
        Create comparison plots for CIQ metrics.
        
        Args:
            data: Experimental data
            save_path: Optional path to save the plot
        """
        const_ciq = data.get_constitutional_ciq()
        dir_ciq = data.get_directive_ciq()
        
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        fig.suptitle('CIQ Metrics Comparison: Constitutional vs Directive AI', fontsize=16)
        
        metrics = ['clarity', 'integrity', 'quality', 'composite']
        
        for i, metric in enumerate(metrics):
            ax = axes[i//2, i%2]
            
            # Box plot
            data_to_plot = [const_ciq[metric], dir_ciq[metric]]
            labels = ['Constitutional', 'Directive']
            
            bp = ax.boxplot(data_to_plot, labels=labels, patch_artist=True)
            bp['boxes'][0].set_facecolor('lightblue')
            bp['boxes'][1].set_facecolor('lightcoral')
            
            ax.set_title(f'{metric.title()} Scores')
            ax.set_ylabel('Score')
            ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        plt.show()
    
    def plot_learning_curves(self, data: ExperimentalData, 
                           save_path: Optional[str] = None) -> None:
        """
        Plot learning curves for both groups.
        
        Args:
            data: Experimental data
            save_path: Optional path to save the plot
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Constitutional group learning curve
        const_scores = self._extract_temporal_scores(data.constitutional_group)
        if const_scores:
            ax1.plot(const_scores, 'o-', color='blue', linewidth=2, markersize=6)
            ax1.set_title('Constitutional AI Learning Curve')
            ax1.set_xlabel('Interaction Number')
            ax1.set_ylabel('CIQ Composite Score')
            ax1.grid(True, alpha=0.3)
            
            # Add trend line
            x = np.arange(len(const_scores))
            z = np.polyfit(x, const_scores, 1)
            p = np.poly1d(z)
            ax1.plot(x, p(x), "--", color='red', alpha=0.7, linewidth=2)
        
        # Directive group learning curve
        dir_scores = self._extract_temporal_scores(data.directive_group)
        if dir_scores:
            ax2.plot(dir_scores, 'o-', color='red', linewidth=2, markersize=6)
            ax2.set_title('Directive AI Learning Curve')
            ax2.set_xlabel('Interaction Number')
            ax2.set_ylabel('CIQ Composite Score')
            ax2.grid(True, alpha=0.3)
            
            # Add trend line
            x = np.arange(len(dir_scores))
            z = np.polyfit(x, dir_scores, 1)
            p = np.poly1d(z)
            ax2.plot(x, p(x), "--", color='blue', alpha=0.7, linewidth=2)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        plt.show()
    
    def plot_effect_sizes(self, results: Dict[str, StatisticalResult], 
                         save_path: Optional[str] = None) -> None:
        """
        Plot effect sizes from statistical tests.
        
        Args:
            results: Statistical test results
            save_path: Optional path to save the plot
        """
        metrics = []
        effect_sizes = []
        significance = []
        
        for metric, result in results.items():
            if result.effect_size is not None:
                metrics.append(metric.title())
                effect_sizes.append(result.effect_size)
                significance.append(result.significant)
        
        if not metrics:
            print("No effect sizes to plot")
            return
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        colors = ['green' if sig else 'gray' for sig in significance]
        bars = ax.bar(metrics, effect_sizes, color=colors, alpha=0.7)
        
        # Add significance indicators
        for i, (bar, sig) in enumerate(zip(bars, significance)):
            if sig:
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                       '*', ha='center', va='bottom', fontsize=16, fontweight='bold')
        
        ax.set_title('Effect Sizes (Cohen\'s d) for CIQ Metrics')
        ax.set_ylabel('Effect Size')
        ax.axhline(y=0, color='black', linestyle='-', alpha=0.3)
        ax.axhline(y=0.2, color='red', linestyle='--', alpha=0.5, label='Small effect')
        ax.axhline(y=0.5, color='orange', linestyle='--', alpha=0.5, label='Medium effect')
        ax.axhline(y=0.8, color='green', linestyle='--', alpha=0.5, label='Large effect')
        
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        plt.show()
    
    def _extract_temporal_scores(self, interactions: List[Dict[str, Any]]) -> List[float]:
        """Extract CIQ composite scores in temporal order."""
        scores = []
        
        for interaction in interactions:
            ciq = interaction.get('ciq_metrics', {})
            composite = (
                ciq.get('clarity', 0.0) + 
                ciq.get('integrity', 0.0) + 
                ciq.get('quality', 0.0)
            ) / 3
            scores.append(composite)
        
        return scores


class ReplicationAnalysis:
    """Complete replication analysis pipeline."""
    
    def __init__(self, alpha: float = 0.05):
        """
        Initialize replication analysis.
        
        Args:
            alpha: Significance level
        """
        self.alpha = alpha
        self.hypothesis_test = HypothesisTest(alpha)
        self.power_analysis = PowerAnalysis()
        self.descriptive = DescriptiveAnalysis()
        self.visualization = VisualizationTools()
    
    def run_complete_analysis(self, data: ExperimentalData, 
                            output_dir: Optional[str] = None) -> Dict[str, Any]:
        """
        Run complete replication analysis.
        
        Args:
            data: Experimental data
            output_dir: Optional directory for saving outputs
            
        Returns:
            Complete analysis results
        """
        results = {
            'descriptive_stats': self.descriptive.summarize_groups(data),
            'hypothesis_tests': {},
            'power_analysis': {},
            'visualizations_created': []
        }
        
        # Hypothesis testing
        results['hypothesis_tests']['ciq_superiority'] = (
            self.hypothesis_test.test_ciq_superiority(data)
        )
        
        results['hypothesis_tests']['consistency_improvement'] = (
            self.hypothesis_test.test_consistency_improvement(data)
        )
        
        results['hypothesis_tests']['learning_curves'] = (
            self.hypothesis_test.test_learning_curve(data)
        )
        
        # Power analysis
        for metric, test_result in results['hypothesis_tests']['ciq_superiority'].items():
            if test_result.effect_size:
                n_per_group = len(data.constitutional_group)
                power = self.power_analysis.calculate_power(
                    n_per_group, abs(test_result.effect_size), self.alpha
                )
                results['power_analysis'][metric] = {
                    'observed_power': power,
                    'effect_size': test_result.effect_size,
                    'sample_size': n_per_group
                }
        
        # Generate visualizations
        if output_dir:
            import os
            os.makedirs(output_dir, exist_ok=True)
            
            # CIQ comparison plot
            ciq_plot_path = os.path.join(output_dir, 'ciq_comparison.png')
            self.visualization.plot_ciq_comparison(data, ciq_plot_path)
            results['visualizations_created'].append(ciq_plot_path)
            
            # Learning curves plot
            learning_plot_path = os.path.join(output_dir, 'learning_curves.png')
            self.visualization.plot_learning_curves(data, learning_plot_path)
            results['visualizations_created'].append(learning_plot_path)
            
            # Effect sizes plot
            effect_plot_path = os.path.join(output_dir, 'effect_sizes.png')
            self.visualization.plot_effect_sizes(
                results['hypothesis_tests']['ciq_superiority'], 
                effect_plot_path
            )
            results['visualizations_created'].append(effect_plot_path)
        
        return results
    
    def generate_report(self, results: Dict[str, Any]) -> str:
        """
        Generate a text report of the analysis results.
        
        Args:
            results: Analysis results from run_complete_analysis
            
        Returns:
            Formatted text report
        """
        report = []
        report.append("SYMBI Constitutional AI Replication Analysis Report")
        report.append("=" * 50)
        report.append("")
        
        # Descriptive statistics
        report.append("DESCRIPTIVE STATISTICS")
        report.append("-" * 25)
        
        desc_stats = results['descriptive_stats']
        
        report.append("Constitutional AI Group:")
        for metric, stats in desc_stats['constitutional'].items():
            report.append(f"  {metric.title()}: M={stats['mean']:.3f}, SD={stats['std']:.3f}, N={stats['n']}")
        
        report.append("")
        report.append("Directive AI Group:")
        for metric, stats in desc_stats['directive'].items():
            report.append(f"  {metric.title()}: M={stats['mean']:.3f}, SD={stats['std']:.3f}, N={stats['n']}")
        
        report.append("")
        
        # Hypothesis test results
        report.append("HYPOTHESIS TEST RESULTS")
        report.append("-" * 25)
        
        # CIQ superiority tests
        report.append("CIQ Superiority Tests:")
        for metric, result in results['hypothesis_tests']['ciq_superiority'].items():
            status = "SIGNIFICANT" if result.significant else "NOT SIGNIFICANT"
            report.append(f"  {metric.title()}: {status} (p={result.p_value:.4f}, d={result.effect_size:.3f})")
        
        report.append("")
        
        # Consistency test
        consistency_result = results['hypothesis_tests']['consistency_improvement']
        status = "SIGNIFICANT" if consistency_result.significant else "NOT SIGNIFICANT"
        report.append(f"Consistency Improvement: {status} (p={consistency_result.p_value:.4f})")
        
        report.append("")
        
        # Learning curve tests
        report.append("Learning Curve Analysis:")
        learning_results = results['hypothesis_tests']['learning_curves']
        for test_name, result in learning_results.items():
            status = "SIGNIFICANT" if result.significant else "NOT SIGNIFICANT"
            report.append(f"  {test_name}: {status} (p={result.p_value:.4f})")
        
        report.append("")
        
        # Power analysis
        if results['power_analysis']:
            report.append("POWER ANALYSIS")
            report.append("-" * 15)
            for metric, power_info in results['power_analysis'].items():
                report.append(f"  {metric.title()}: Power={power_info['observed_power']:.3f}")
        
        report.append("")
        
        # Conclusions
        report.append("CONCLUSIONS")
        report.append("-" * 11)
        
        # Count significant results
        sig_count = sum(1 for result in results['hypothesis_tests']['ciq_superiority'].values() 
                       if result.significant)
        total_tests = len(results['hypothesis_tests']['ciq_superiority'])
        
        if sig_count > total_tests / 2:
            report.append("✓ Constitutional AI shows superior performance on most CIQ metrics")
        else:
            report.append("✗ Constitutional AI does not show consistent superiority")
        
        if consistency_result.significant:
            report.append("✓ Constitutional AI demonstrates improved consistency")
        else:
            report.append("✗ No significant improvement in consistency detected")
        
        return "\n".join(report)