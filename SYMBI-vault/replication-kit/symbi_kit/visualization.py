"""
Visualization: Research data presentation and analysis

This module provides comprehensive visualization tools for SYMBI research
data, including CIQ metrics, trust receipts, and experimental results.
"""

import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass
import json
from datetime import datetime, timedelta
import networkx as nx
from matplotlib.patches import Rectangle
from matplotlib.collections import LineCollection
import warnings

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')

# Set style
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")


@dataclass
class VisualizationConfig:
    """Configuration for visualization settings."""
    figure_size: Tuple[int, int] = (12, 8)
    dpi: int = 300
    color_palette: str = "husl"
    style: str = "seaborn-v0_8"
    font_size: int = 12
    title_size: int = 16
    save_format: str = "png"
    
    def apply_matplotlib_config(self):
        """Apply configuration to matplotlib."""
        plt.style.use(self.style)
        plt.rcParams.update({
            'figure.figsize': self.figure_size,
            'figure.dpi': self.dpi,
            'font.size': self.font_size,
            'axes.titlesize': self.title_size,
            'axes.labelsize': self.font_size,
            'xtick.labelsize': self.font_size - 1,
            'ytick.labelsize': self.font_size - 1,
            'legend.fontsize': self.font_size - 1
        })
        sns.set_palette(self.color_palette)


class CIQVisualizer:
    """Visualizer for CIQ (Clarity, Integrity, Quality) metrics."""
    
    def __init__(self, config: Optional[VisualizationConfig] = None):
        """
        Initialize CIQ visualizer.
        
        Args:
            config: Visualization configuration
        """
        self.config = config or VisualizationConfig()
        self.config.apply_matplotlib_config()
    
    def plot_ciq_radar(self, ciq_data: Dict[str, float], 
                       title: str = "CIQ Metrics Radar Chart",
                       save_path: Optional[str] = None) -> None:
        """
        Create a radar chart for CIQ metrics.
        
        Args:
            ciq_data: Dictionary with CIQ metric values
            title: Chart title
            save_path: Optional path to save the chart
        """
        # Prepare data
        metrics = ['Clarity', 'Integrity', 'Quality']
        values = [
            ciq_data.get('clarity', 0.0),
            ciq_data.get('integrity', 0.0),
            ciq_data.get('quality', 0.0)
        ]
        
        # Close the radar chart
        values += values[:1]
        
        # Calculate angles for each metric
        angles = np.linspace(0, 2 * np.pi, len(metrics), endpoint=False).tolist()
        angles += angles[:1]
        
        # Create the plot
        fig, ax = plt.subplots(figsize=self.config.figure_size, subplot_kw=dict(projection='polar'))
        
        # Plot the radar chart
        ax.plot(angles, values, 'o-', linewidth=2, label='CIQ Scores')
        ax.fill(angles, values, alpha=0.25)
        
        # Customize the chart
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(metrics)
        ax.set_ylim(0, 1)
        ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
        ax.set_yticklabels(['0.2', '0.4', '0.6', '0.8', '1.0'])
        ax.grid(True)
        
        plt.title(title, size=self.config.title_size, pad=20)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=self.config.dpi, bbox_inches='tight')
        
        plt.show()
    
    def plot_ciq_comparison(self, constitutional_data: List[Dict[str, float]], 
                           directive_data: List[Dict[str, float]],
                           title: str = "Constitutional vs Directive AI: CIQ Comparison",
                           save_path: Optional[str] = None) -> None:
        """
        Create comparison plots for constitutional vs directive AI.
        
        Args:
            constitutional_data: List of CIQ metrics for constitutional AI
            directive_data: List of CIQ metrics for directive AI
            title: Chart title
            save_path: Optional path to save the chart
        """
        # Prepare data
        metrics = ['clarity', 'integrity', 'quality']
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle(title, fontsize=self.config.title_size)
        
        # Individual metric comparisons
        for i, metric in enumerate(metrics):
            ax = axes[i//2, i%2] if i < 3 else axes[1, 1]
            
            const_values = [d.get(metric, 0.0) for d in constitutional_data]
            dir_values = [d.get(metric, 0.0) for d in directive_data]
            
            # Box plot
            data_to_plot = [const_values, dir_values]
            labels = ['Constitutional', 'Directive']
            
            bp = ax.boxplot(data_to_plot, labels=labels, patch_artist=True)
            bp['boxes'][0].set_facecolor('lightblue')
            bp['boxes'][1].set_facecolor('lightcoral')
            
            ax.set_title(f'{metric.title()} Scores')
            ax.set_ylabel('Score')
            ax.grid(True, alpha=0.3)
            
            # Add mean lines
            ax.axhline(y=np.mean(const_values), color='blue', linestyle='--', alpha=0.7)
            ax.axhline(y=np.mean(dir_values), color='red', linestyle='--', alpha=0.7)
        
        # Composite score comparison
        if len(axes.flat) > 3:
            ax = axes[1, 1]
            
            const_composite = [
                (d.get('clarity', 0.0) + d.get('integrity', 0.0) + d.get('quality', 0.0)) / 3
                for d in constitutional_data
            ]
            dir_composite = [
                (d.get('clarity', 0.0) + d.get('integrity', 0.0) + d.get('quality', 0.0)) / 3
                for d in directive_data
            ]
            
            data_to_plot = [const_composite, dir_composite]
            labels = ['Constitutional', 'Directive']
            
            bp = ax.boxplot(data_to_plot, labels=labels, patch_artist=True)
            bp['boxes'][0].set_facecolor('lightgreen')
            bp['boxes'][1].set_facecolor('lightyellow')
            
            ax.set_title('Composite CIQ Scores')
            ax.set_ylabel('Score')
            ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=self.config.dpi, bbox_inches='tight')
        
        plt.show()
    
    def plot_ciq_timeline(self, ciq_timeline: List[Dict[str, Any]],
                         title: str = "CIQ Metrics Over Time",
                         save_path: Optional[str] = None) -> None:
        """
        Plot CIQ metrics evolution over time.
        
        Args:
            ciq_timeline: List of timestamped CIQ measurements
            title: Chart title
            save_path: Optional path to save the chart
        """
        if not ciq_timeline:
            print("No timeline data to plot")
            return
        
        # Extract data
        timestamps = []
        clarity_scores = []
        integrity_scores = []
        quality_scores = []
        
        for entry in ciq_timeline:
            timestamps.append(entry.get('timestamp', datetime.now()))
            ciq = entry.get('ciq_metrics', {})
            clarity_scores.append(ciq.get('clarity', 0.0))
            integrity_scores.append(ciq.get('integrity', 0.0))
            quality_scores.append(ciq.get('quality', 0.0))
        
        # Create the plot
        fig, ax = plt.subplots(figsize=self.config.figure_size)
        
        ax.plot(timestamps, clarity_scores, 'o-', label='Clarity', linewidth=2, markersize=6)
        ax.plot(timestamps, integrity_scores, 's-', label='Integrity', linewidth=2, markersize=6)
        ax.plot(timestamps, quality_scores, '^-', label='Quality', linewidth=2, markersize=6)
        
        # Calculate and plot composite score
        composite_scores = [(c + i + q) / 3 for c, i, q in zip(clarity_scores, integrity_scores, quality_scores)]
        ax.plot(timestamps, composite_scores, 'D-', label='Composite', linewidth=3, markersize=8, alpha=0.8)
        
        ax.set_xlabel('Time')
        ax.set_ylabel('CIQ Score')
        ax.set_title(title)
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Format x-axis
        plt.xticks(rotation=45)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=self.config.dpi, bbox_inches='tight')
        
        plt.show()
    
    def plot_ciq_heatmap(self, ciq_matrix: List[List[Dict[str, float]]],
                        labels: Optional[List[str]] = None,
                        title: str = "CIQ Metrics Heatmap",
                        save_path: Optional[str] = None) -> None:
        """
        Create a heatmap of CIQ metrics across different conditions.
        
        Args:
            ciq_matrix: 2D list of CIQ metric dictionaries
            labels: Optional labels for rows/columns
            title: Chart title
            save_path: Optional path to save the chart
        """
        if not ciq_matrix or not ciq_matrix[0]:
            print("No matrix data to plot")
            return
        
        # Extract composite scores
        composite_matrix = []
        for row in ciq_matrix:
            composite_row = []
            for ciq_dict in row:
                composite = (
                    ciq_dict.get('clarity', 0.0) + 
                    ciq_dict.get('integrity', 0.0) + 
                    ciq_dict.get('quality', 0.0)
                ) / 3
                composite_row.append(composite)
            composite_matrix.append(composite_row)
        
        # Create heatmap
        fig, ax = plt.subplots(figsize=self.config.figure_size)
        
        im = ax.imshow(composite_matrix, cmap='RdYlGn', aspect='auto', vmin=0, vmax=1)
        
        # Add colorbar
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('Composite CIQ Score')
        
        # Set labels
        if labels:
            ax.set_xticks(range(len(labels)))
            ax.set_xticklabels(labels, rotation=45)
            ax.set_yticks(range(len(labels)))
            ax.set_yticklabels(labels)
        
        # Add text annotations
        for i in range(len(composite_matrix)):
            for j in range(len(composite_matrix[0])):
                text = ax.text(j, i, f'{composite_matrix[i][j]:.2f}',
                             ha="center", va="center", color="black", fontweight='bold')
        
        ax.set_title(title)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=self.config.dpi, bbox_inches='tight')
        
        plt.show()


class TrustReceiptVisualizer:
    """Visualizer for trust receipts and blockchain-like structures."""
    
    def __init__(self, config: Optional[VisualizationConfig] = None):
        """
        Initialize trust receipt visualizer.
        
        Args:
            config: Visualization configuration
        """
        self.config = config or VisualizationConfig()
        self.config.apply_matplotlib_config()
    
    def plot_receipt_chain(self, receipts: List[Dict[str, Any]],
                          title: str = "Trust Receipt Chain",
                          save_path: Optional[str] = None) -> None:
        """
        Visualize a chain of trust receipts.
        
        Args:
            receipts: List of trust receipt dictionaries
            title: Chart title
            save_path: Optional path to save the chart
        """
        if not receipts:
            print("No receipts to visualize")
            return
        
        fig, ax = plt.subplots(figsize=(15, 8))
        
        # Calculate positions
        n_receipts = len(receipts)
        x_positions = np.linspace(0, 10, n_receipts)
        y_position = 0.5
        
        # Draw receipt boxes
        for i, (x_pos, receipt) in enumerate(zip(x_positions, receipts)):
            # Receipt box
            rect = Rectangle((x_pos - 0.4, y_position - 0.2), 0.8, 0.4, 
                           facecolor='lightblue', edgecolor='black', linewidth=2)
            ax.add_patch(rect)
            
            # Receipt info
            session_id = receipt.get('session_id', f'R{i+1}')[:8]
            ciq_score = receipt.get('ciq_metrics', {})
            composite = (
                ciq_score.get('clarity', 0.0) + 
                ciq_score.get('integrity', 0.0) + 
                ciq_score.get('quality', 0.0)
            ) / 3
            
            ax.text(x_pos, y_position + 0.05, session_id, ha='center', va='center', 
                   fontweight='bold', fontsize=10)
            ax.text(x_pos, y_position - 0.05, f'CIQ: {composite:.2f}', ha='center', va='center', 
                   fontsize=8)
            
            # Draw arrow to next receipt
            if i < n_receipts - 1:
                ax.arrow(x_pos + 0.4, y_position, 
                        x_positions[i+1] - x_pos - 0.8, 0,
                        head_width=0.05, head_length=0.1, fc='black', ec='black')
        
        ax.set_xlim(-0.5, 10.5)
        ax.set_ylim(0, 1)
        ax.set_title(title)
        ax.axis('off')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=self.config.dpi, bbox_inches='tight')
        
        plt.show()
    
    def plot_receipt_network(self, receipts: List[Dict[str, Any]],
                           title: str = "Trust Receipt Network",
                           save_path: Optional[str] = None) -> None:
        """
        Visualize trust receipts as a network graph.
        
        Args:
            receipts: List of trust receipt dictionaries
            title: Chart title
            save_path: Optional path to save the chart
        """
        if not receipts:
            print("No receipts to visualize")
            return
        
        # Create network graph
        G = nx.DiGraph()
        
        # Add nodes and edges
        for i, receipt in enumerate(receipts):
            session_id = receipt.get('session_id', f'R{i+1}')
            ciq_metrics = receipt.get('ciq_metrics', {})
            composite = (
                ciq_metrics.get('clarity', 0.0) + 
                ciq_metrics.get('integrity', 0.0) + 
                ciq_metrics.get('quality', 0.0)
            ) / 3
            
            G.add_node(session_id, ciq_score=composite)
            
            # Add edge to previous receipt
            if i > 0:
                prev_session = receipts[i-1].get('session_id', f'R{i}')
                G.add_edge(prev_session, session_id)
        
        # Create layout
        pos = nx.spring_layout(G, k=2, iterations=50)
        
        # Plot
        fig, ax = plt.subplots(figsize=self.config.figure_size)
        
        # Draw nodes
        node_colors = [G.nodes[node]['ciq_score'] for node in G.nodes()]
        nodes = nx.draw_networkx_nodes(G, pos, node_color=node_colors, 
                                     cmap='RdYlGn', vmin=0, vmax=1, 
                                     node_size=1000, ax=ax)
        
        # Draw edges
        nx.draw_networkx_edges(G, pos, edge_color='gray', arrows=True, 
                             arrowsize=20, ax=ax)
        
        # Draw labels
        nx.draw_networkx_labels(G, pos, font_size=8, font_weight='bold', ax=ax)
        
        # Add colorbar
        plt.colorbar(nodes, ax=ax, label='CIQ Score')
        
        ax.set_title(title)
        ax.axis('off')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=self.config.dpi, bbox_inches='tight')
        
        plt.show()
    
    def plot_receipt_metrics_distribution(self, receipts: List[Dict[str, Any]],
                                        title: str = "Trust Receipt Metrics Distribution",
                                        save_path: Optional[str] = None) -> None:
        """
        Plot distribution of metrics across trust receipts.
        
        Args:
            receipts: List of trust receipt dictionaries
            title: Chart title
            save_path: Optional path to save the chart
        """
        if not receipts:
            print("No receipts to analyze")
            return
        
        # Extract metrics
        clarity_scores = []
        integrity_scores = []
        quality_scores = []
        
        for receipt in receipts:
            ciq = receipt.get('ciq_metrics', {})
            clarity_scores.append(ciq.get('clarity', 0.0))
            integrity_scores.append(ciq.get('integrity', 0.0))
            quality_scores.append(ciq.get('quality', 0.0))
        
        # Create subplots
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        fig.suptitle(title, fontsize=self.config.title_size)
        
        # Clarity distribution
        axes[0, 0].hist(clarity_scores, bins=20, alpha=0.7, color='blue', edgecolor='black')
        axes[0, 0].set_title('Clarity Scores Distribution')
        axes[0, 0].set_xlabel('Score')
        axes[0, 0].set_ylabel('Frequency')
        axes[0, 0].grid(True, alpha=0.3)
        
        # Integrity distribution
        axes[0, 1].hist(integrity_scores, bins=20, alpha=0.7, color='green', edgecolor='black')
        axes[0, 1].set_title('Integrity Scores Distribution')
        axes[0, 1].set_xlabel('Score')
        axes[0, 1].set_ylabel('Frequency')
        axes[0, 1].grid(True, alpha=0.3)
        
        # Quality distribution
        axes[1, 0].hist(quality_scores, bins=20, alpha=0.7, color='red', edgecolor='black')
        axes[1, 0].set_title('Quality Scores Distribution')
        axes[1, 0].set_xlabel('Score')
        axes[1, 0].set_ylabel('Frequency')
        axes[1, 0].grid(True, alpha=0.3)
        
        # Composite distribution
        composite_scores = [(c + i + q) / 3 for c, i, q in zip(clarity_scores, integrity_scores, quality_scores)]
        axes[1, 1].hist(composite_scores, bins=20, alpha=0.7, color='purple', edgecolor='black')
        axes[1, 1].set_title('Composite CIQ Distribution')
        axes[1, 1].set_xlabel('Score')
        axes[1, 1].set_ylabel('Frequency')
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=self.config.dpi, bbox_inches='tight')
        
        plt.show()


class ExperimentalVisualizer:
    """Visualizer for experimental results and A/B testing."""
    
    def __init__(self, config: Optional[VisualizationConfig] = None):
        """
        Initialize experimental visualizer.
        
        Args:
            config: Visualization configuration
        """
        self.config = config or VisualizationConfig()
        self.config.apply_matplotlib_config()
    
    def plot_ab_test_results(self, constitutional_results: List[Dict[str, Any]],
                           directive_results: List[Dict[str, Any]],
                           title: str = "A/B Test Results: Constitutional vs Directive AI",
                           save_path: Optional[str] = None) -> None:
        """
        Visualize A/B test results.
        
        Args:
            constitutional_results: Results from constitutional AI tests
            directive_results: Results from directive AI tests
            title: Chart title
            save_path: Optional path to save the chart
        """
        # Extract CIQ metrics
        const_ciq = self._extract_ciq_from_results(constitutional_results)
        dir_ciq = self._extract_ciq_from_results(directive_results)
        
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        fig.suptitle(title, fontsize=self.config.title_size)
        
        metrics = ['clarity', 'integrity', 'quality']
        
        # Individual metric comparisons
        for i, metric in enumerate(metrics):
            # Box plot comparison
            ax1 = axes[0, i]
            data_to_plot = [const_ciq[metric], dir_ciq[metric]]
            labels = ['Constitutional', 'Directive']
            
            bp = ax1.boxplot(data_to_plot, labels=labels, patch_artist=True)
            bp['boxes'][0].set_facecolor('lightblue')
            bp['boxes'][1].set_facecolor('lightcoral')
            
            ax1.set_title(f'{metric.title()} Comparison')
            ax1.set_ylabel('Score')
            ax1.grid(True, alpha=0.3)
            
            # Violin plot
            ax2 = axes[1, i]
            parts = ax2.violinplot([const_ciq[metric], dir_ciq[metric]], positions=[1, 2])
            
            for pc, color in zip(parts['bodies'], ['lightblue', 'lightcoral']):
                pc.set_facecolor(color)
                pc.set_alpha(0.7)
            
            ax2.set_xticks([1, 2])
            ax2.set_xticklabels(['Constitutional', 'Directive'])
            ax2.set_title(f'{metric.title()} Distribution')
            ax2.set_ylabel('Score')
            ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=self.config.dpi, bbox_inches='tight')
        
        plt.show()
    
    def plot_learning_curves(self, constitutional_timeline: List[Dict[str, Any]],
                           directive_timeline: List[Dict[str, Any]],
                           title: str = "Learning Curves Comparison",
                           save_path: Optional[str] = None) -> None:
        """
        Plot learning curves for both experimental conditions.
        
        Args:
            constitutional_timeline: Timeline data for constitutional AI
            directive_timeline: Timeline data for directive AI
            title: Chart title
            save_path: Optional path to save the chart
        """
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle(title, fontsize=self.config.title_size)
        
        # Extract scores over time
        const_scores = self._extract_temporal_ciq(constitutional_timeline)
        dir_scores = self._extract_temporal_ciq(directive_timeline)
        
        # Individual learning curves
        axes[0, 0].plot(const_scores['clarity'], 'o-', label='Clarity', linewidth=2)
        axes[0, 0].plot(const_scores['integrity'], 's-', label='Integrity', linewidth=2)
        axes[0, 0].plot(const_scores['quality'], '^-', label='Quality', linewidth=2)
        axes[0, 0].set_title('Constitutional AI Learning')
        axes[0, 0].set_xlabel('Interaction')
        axes[0, 0].set_ylabel('CIQ Score')
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)
        
        axes[0, 1].plot(dir_scores['clarity'], 'o-', label='Clarity', linewidth=2)
        axes[0, 1].plot(dir_scores['integrity'], 's-', label='Integrity', linewidth=2)
        axes[0, 1].plot(dir_scores['quality'], '^-', label='Quality', linewidth=2)
        axes[0, 1].set_title('Directive AI Learning')
        axes[0, 1].set_xlabel('Interaction')
        axes[0, 1].set_ylabel('CIQ Score')
        axes[0, 1].legend()
        axes[0, 1].grid(True, alpha=0.3)
        
        # Composite comparison
        const_composite = [(c + i + q) / 3 for c, i, q in zip(
            const_scores['clarity'], const_scores['integrity'], const_scores['quality']
        )]
        dir_composite = [(c + i + q) / 3 for c, i, q in zip(
            dir_scores['clarity'], dir_scores['integrity'], dir_scores['quality']
        )]
        
        axes[1, 0].plot(const_composite, 'o-', label='Constitutional', linewidth=3, color='blue')
        axes[1, 0].plot(dir_composite, 's-', label='Directive', linewidth=3, color='red')
        axes[1, 0].set_title('Composite CIQ Comparison')
        axes[1, 0].set_xlabel('Interaction')
        axes[1, 0].set_ylabel('Composite Score')
        axes[1, 0].legend()
        axes[1, 0].grid(True, alpha=0.3)
        
        # Learning rate comparison (slopes)
        const_slope = np.polyfit(range(len(const_composite)), const_composite, 1)[0]
        dir_slope = np.polyfit(range(len(dir_composite)), dir_composite, 1)[0]
        
        axes[1, 1].bar(['Constitutional', 'Directive'], [const_slope, dir_slope], 
                      color=['blue', 'red'], alpha=0.7)
        axes[1, 1].set_title('Learning Rate Comparison')
        axes[1, 1].set_ylabel('Learning Rate (slope)')
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=self.config.dpi, bbox_inches='tight')
        
        plt.show()
    
    def plot_statistical_results(self, test_results: Dict[str, Any],
                               title: str = "Statistical Test Results",
                               save_path: Optional[str] = None) -> None:
        """
        Visualize statistical test results.
        
        Args:
            test_results: Dictionary of statistical test results
            title: Chart title
            save_path: Optional path to save the chart
        """
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle(title, fontsize=self.config.title_size)
        
        # P-values
        if 'ciq_superiority' in test_results:
            metrics = []
            p_values = []
            significant = []
            
            for metric, result in test_results['ciq_superiority'].items():
                metrics.append(metric.title())
                p_values.append(result.p_value)
                significant.append(result.significant)
            
            colors = ['green' if sig else 'red' for sig in significant]
            bars = axes[0, 0].bar(metrics, p_values, color=colors, alpha=0.7)
            axes[0, 0].axhline(y=0.05, color='black', linestyle='--', label='α = 0.05')
            axes[0, 0].set_title('P-values by Metric')
            axes[0, 0].set_ylabel('P-value')
            axes[0, 0].legend()
            axes[0, 0].grid(True, alpha=0.3)
            
            # Add significance markers
            for bar, sig in zip(bars, significant):
                if sig:
                    axes[0, 0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                                   '*', ha='center', va='bottom', fontsize=16, fontweight='bold')
        
        # Effect sizes
        if 'ciq_superiority' in test_results:
            effect_sizes = []
            for metric, result in test_results['ciq_superiority'].items():
                if result.effect_size is not None:
                    effect_sizes.append(result.effect_size)
                else:
                    effect_sizes.append(0)
            
            bars = axes[0, 1].bar(metrics, effect_sizes, color='skyblue', alpha=0.7)
            axes[0, 1].axhline(y=0.2, color='orange', linestyle='--', label='Small effect')
            axes[0, 1].axhline(y=0.5, color='red', linestyle='--', label='Medium effect')
            axes[0, 1].axhline(y=0.8, color='green', linestyle='--', label='Large effect')
            axes[0, 1].set_title('Effect Sizes (Cohen\'s d)')
            axes[0, 1].set_ylabel('Effect Size')
            axes[0, 1].legend()
            axes[0, 1].grid(True, alpha=0.3)
        
        # Confidence intervals (if available)
        if 'ciq_superiority' in test_results:
            ci_lower = []
            ci_upper = []
            
            for metric, result in test_results['ciq_superiority'].items():
                if result.confidence_interval:
                    ci_lower.append(result.confidence_interval[0])
                    ci_upper.append(result.confidence_interval[1])
                else:
                    ci_lower.append(0)
                    ci_upper.append(0)
            
            x_pos = range(len(metrics))
            axes[1, 0].errorbar(x_pos, [0] * len(metrics), 
                              yerr=[ci_lower, ci_upper], fmt='o', capsize=5)
            axes[1, 0].axhline(y=0, color='black', linestyle='-', alpha=0.5)
            axes[1, 0].set_xticks(x_pos)
            axes[1, 0].set_xticklabels(metrics, rotation=45)
            axes[1, 0].set_title('95% Confidence Intervals')
            axes[1, 0].set_ylabel('Mean Difference')
            axes[1, 0].grid(True, alpha=0.3)
        
        # Summary statistics
        if 'ciq_superiority' in test_results:
            sig_count = sum(1 for result in test_results['ciq_superiority'].values() 
                           if result.significant)
            total_tests = len(test_results['ciq_superiority'])
            
            labels = ['Significant', 'Not Significant']
            sizes = [sig_count, total_tests - sig_count]
            colors = ['green', 'red']
            
            axes[1, 1].pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
            axes[1, 1].set_title('Test Results Summary')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=self.config.dpi, bbox_inches='tight')
        
        plt.show()
    
    def _extract_ciq_from_results(self, results: List[Dict[str, Any]]) -> Dict[str, List[float]]:
        """Extract CIQ metrics from experimental results."""
        ciq_data = {
            'clarity': [],
            'integrity': [],
            'quality': []
        }
        
        for result in results:
            ciq = result.get('ciq_metrics', {})
            ciq_data['clarity'].append(ciq.get('clarity', 0.0))
            ciq_data['integrity'].append(ciq.get('integrity', 0.0))
            ciq_data['quality'].append(ciq.get('quality', 0.0))
        
        return ciq_data
    
    def _extract_temporal_ciq(self, timeline: List[Dict[str, Any]]) -> Dict[str, List[float]]:
        """Extract temporal CIQ data."""
        return self._extract_ciq_from_results(timeline)


class InteractiveVisualizer:
    """Interactive visualizations using Plotly."""
    
    def __init__(self):
        """Initialize interactive visualizer."""
        pass
    
    def create_interactive_ciq_dashboard(self, data: Dict[str, Any]) -> go.Figure:
        """
        Create an interactive CIQ metrics dashboard.
        
        Args:
            data: Dictionary containing CIQ data
            
        Returns:
            Plotly figure object
        """
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('CIQ Metrics Over Time', 'Metric Distribution', 
                          'Correlation Matrix', 'Performance Summary'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"type": "table"}]]
        )
        
        # Add traces (simplified example)
        if 'timeline' in data:
            timeline = data['timeline']
            clarity_scores = [entry.get('ciq_metrics', {}).get('clarity', 0) for entry in timeline]
            integrity_scores = [entry.get('ciq_metrics', {}).get('integrity', 0) for entry in timeline]
            quality_scores = [entry.get('ciq_metrics', {}).get('quality', 0) for entry in timeline]
            
            fig.add_trace(
                go.Scatter(y=clarity_scores, name='Clarity', mode='lines+markers'),
                row=1, col=1
            )
            fig.add_trace(
                go.Scatter(y=integrity_scores, name='Integrity', mode='lines+markers'),
                row=1, col=1
            )
            fig.add_trace(
                go.Scatter(y=quality_scores, name='Quality', mode='lines+markers'),
                row=1, col=1
            )
        
        # Update layout
        fig.update_layout(
            title="SYMBI CIQ Metrics Interactive Dashboard",
            showlegend=True,
            height=800
        )
        
        return fig
    
    def create_receipt_network_interactive(self, receipts: List[Dict[str, Any]]) -> go.Figure:
        """
        Create an interactive trust receipt network.
        
        Args:
            receipts: List of trust receipt dictionaries
            
        Returns:
            Plotly figure object
        """
        # Create network graph (simplified)
        G = nx.DiGraph()
        
        for i, receipt in enumerate(receipts):
            session_id = receipt.get('session_id', f'R{i+1}')
            ciq_metrics = receipt.get('ciq_metrics', {})
            composite = (
                ciq_metrics.get('clarity', 0.0) + 
                ciq_metrics.get('integrity', 0.0) + 
                ciq_metrics.get('quality', 0.0)
            ) / 3
            
            G.add_node(session_id, ciq_score=composite)
            
            if i > 0:
                prev_session = receipts[i-1].get('session_id', f'R{i}')
                G.add_edge(prev_session, session_id)
        
        # Get positions
        pos = nx.spring_layout(G)
        
        # Extract coordinates
        node_x = [pos[node][0] for node in G.nodes()]
        node_y = [pos[node][1] for node in G.nodes()]
        node_text = [f"{node}<br>CIQ: {G.nodes[node]['ciq_score']:.2f}" for node in G.nodes()]
        node_colors = [G.nodes[node]['ciq_score'] for node in G.nodes()]
        
        # Create edge traces
        edge_x = []
        edge_y = []
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
        
        # Create figure
        fig = go.Figure()
        
        # Add edges
        fig.add_trace(go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=2, color='gray'),
            hoverinfo='none',
            mode='lines',
            name='Connections'
        ))
        
        # Add nodes
        fig.add_trace(go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            hoverinfo='text',
            hovertext=node_text,
            text=[node for node in G.nodes()],
            textposition="middle center",
            marker=dict(
                size=30,
                color=node_colors,
                colorscale='RdYlGn',
                colorbar=dict(title="CIQ Score"),
                line=dict(width=2, color='black')
            ),
            name='Trust Receipts'
        ))
        
        fig.update_layout(
            title="Interactive Trust Receipt Network",
            showlegend=False,
            hovermode='closest',
            margin=dict(b=20,l=5,r=5,t=40),
            annotations=[
                dict(
                    text="Hover over nodes for details",
                    showarrow=False,
                    xref="paper", yref="paper",
                    x=0.005, y=-0.002,
                    xanchor='left', yanchor='bottom',
                    font=dict(color="gray", size=12)
                )
            ],
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
        )
        
        return fig


class ReportGenerator:
    """Generate comprehensive visualization reports."""
    
    def __init__(self, config: Optional[VisualizationConfig] = None):
        """
        Initialize report generator.
        
        Args:
            config: Visualization configuration
        """
        self.config = config or VisualizationConfig()
        self.ciq_viz = CIQVisualizer(config)
        self.receipt_viz = TrustReceiptVisualizer(config)
        self.exp_viz = ExperimentalVisualizer(config)
        self.interactive_viz = InteractiveVisualizer()
    
    def generate_complete_report(self, data: Dict[str, Any], 
                               output_dir: str) -> Dict[str, str]:
        """
        Generate a complete visualization report.
        
        Args:
            data: Complete experimental data
            output_dir: Directory to save visualizations
            
        Returns:
            Dictionary mapping visualization types to file paths
        """
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        generated_files = {}
        
        # CIQ visualizations
        if 'constitutional_data' in data and 'directive_data' in data:
            ciq_comparison_path = os.path.join(output_dir, 'ciq_comparison.png')
            self.ciq_viz.plot_ciq_comparison(
                data['constitutional_data'], 
                data['directive_data'],
                save_path=ciq_comparison_path
            )
            generated_files['ciq_comparison'] = ciq_comparison_path
        
        # Trust receipt visualizations
        if 'receipts' in data:
            receipt_chain_path = os.path.join(output_dir, 'receipt_chain.png')
            self.receipt_viz.plot_receipt_chain(
                data['receipts'],
                save_path=receipt_chain_path
            )
            generated_files['receipt_chain'] = receipt_chain_path
            
            receipt_metrics_path = os.path.join(output_dir, 'receipt_metrics.png')
            self.receipt_viz.plot_receipt_metrics_distribution(
                data['receipts'],
                save_path=receipt_metrics_path
            )
            generated_files['receipt_metrics'] = receipt_metrics_path
        
        # Experimental results
        if 'ab_test_results' in data:
            ab_results = data['ab_test_results']
            if 'constitutional' in ab_results and 'directive' in ab_results:
                ab_test_path = os.path.join(output_dir, 'ab_test_results.png')
                self.exp_viz.plot_ab_test_results(
                    ab_results['constitutional'],
                    ab_results['directive'],
                    save_path=ab_test_path
                )
                generated_files['ab_test_results'] = ab_test_path
        
        # Learning curves
        if 'constitutional_timeline' in data and 'directive_timeline' in data:
            learning_curves_path = os.path.join(output_dir, 'learning_curves.png')
            self.exp_viz.plot_learning_curves(
                data['constitutional_timeline'],
                data['directive_timeline'],
                save_path=learning_curves_path
            )
            generated_files['learning_curves'] = learning_curves_path
        
        # Statistical results
        if 'statistical_results' in data:
            stats_path = os.path.join(output_dir, 'statistical_results.png')
            self.exp_viz.plot_statistical_results(
                data['statistical_results'],
                save_path=stats_path
            )
            generated_files['statistical_results'] = stats_path
        
        return generated_files
    
    def create_html_report(self, data: Dict[str, Any], 
                          generated_files: Dict[str, str],
                          output_path: str) -> None:
        """
        Create an HTML report with all visualizations.
        
        Args:
            data: Experimental data
            generated_files: Dictionary of generated visualization files
            output_path: Path to save HTML report
        """
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>SYMBI Visualization Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .header {{ text-align: center; margin-bottom: 40px; }}
                .section {{ margin-bottom: 40px; }}
                .visualization {{ text-align: center; margin: 20px 0; }}
                img {{ max-width: 100%; height: auto; border: 1px solid #ddd; }}
                .summary {{ background-color: #f5f5f5; padding: 20px; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>SYMBI Constitutional AI Visualization Report</h1>
                <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            
            <div class="section">
                <h2>Executive Summary</h2>
                <div class="summary">
                    <p>This report presents comprehensive visualizations of SYMBI constitutional AI 
                    research data, including CIQ metrics analysis, trust receipt chains, 
                    experimental results, and statistical comparisons.</p>
                </div>
            </div>
        """
        
        # Add visualizations
        for viz_type, file_path in generated_files.items():
            html_content += f"""
            <div class="section">
                <h2>{viz_type.replace('_', ' ').title()}</h2>
                <div class="visualization">
                    <img src="{os.path.basename(file_path)}" alt="{viz_type}">
                </div>
            </div>
            """
        
        html_content += """
        </body>
        </html>
        """
        
        with open(output_path, 'w') as f:
            f.write(html_content)


# Utility functions for easy access
def create_ciq_visualizer(config: Optional[VisualizationConfig] = None) -> CIQVisualizer:
    """Create a CIQ visualizer instance."""
    return CIQVisualizer(config)

def create_receipt_visualizer(config: Optional[VisualizationConfig] = None) -> TrustReceiptVisualizer:
    """Create a trust receipt visualizer instance."""
    return TrustReceiptVisualizer(config)

def create_experimental_visualizer(config: Optional[VisualizationConfig] = None) -> ExperimentalVisualizer:
    """Create an experimental visualizer instance."""
    return ExperimentalVisualizer(config)

def create_interactive_visualizer() -> InteractiveVisualizer:
    """Create an interactive visualizer instance."""
    return InteractiveVisualizer()

def generate_quick_report(data: Dict[str, Any], output_dir: str) -> Dict[str, str]:
    """
    Quick function to generate a complete visualization report.
    
    Args:
        data: Experimental data
        output_dir: Output directory
        
    Returns:
        Dictionary of generated files
    """
    report_gen = ReportGenerator()
    return report_gen.generate_complete_report(data, output_dir)