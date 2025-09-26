# SYMBI Replication Kit

A comprehensive toolkit for replicating and validating SYMBI constitutional AI research, enabling researchers to conduct rigorous A/B testing and analysis of human-AI collaboration patterns.

## Overview

The SYMBI Replication Kit provides researchers with the tools needed to:

- **Replicate SYMBI Research**: Reproduce key findings from SYMBI constitutional AI studies
- **Conduct A/B Testing**: Compare constitutional vs. directive AI prompting approaches
- **Analyze CIQ Metrics**: Measure Clarity, Integrity, and Quality in AI interactions
- **Validate Trust Receipts**: Verify cryptographic integrity of interaction records
- **Generate Research Reports**: Create publication-ready analysis and visualizations

## Quick Start

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd SYMBI-vault/replication-kit

# Install dependencies
pip install -r requirements.txt

# Install the package in development mode
pip install -e .
```

### Basic Usage

```python
from symbi_kit import ABTestFramework, load_sample_dataset

# Load sample data
data = load_sample_dataset('comparative', 'medium')

# Run A/B test analysis
framework = ABTestFramework()
results = framework.run_analysis(data)

# Print results
framework.print_results(results)
```

## Core Components

### 1. A/B Testing Framework (`ab_testing.py`)

Compare constitutional AI against traditional directive approaches:

```python
from symbi_kit.ab_testing import ABTestFramework, TestConfiguration

# Configure test
config = TestConfiguration(
    name="Constitutional vs Directive",
    hypothesis="Constitutional AI produces higher CIQ scores",
    alpha=0.05,
    power=0.8
)

# Run analysis
framework = ABTestFramework(config)
results = framework.run_analysis(your_data)
```

### 2. CIQ Metrics Analysis (`ciq_metrics.py`)

Measure and analyze Clarity, Integrity, and Quality:

```python
from symbi_kit.ciq_metrics import CIQCalculator

calculator = CIQCalculator()

# Calculate CIQ for an interaction
ciq_result = calculator.calculate_ciq(interaction_data)
print(f"Overall CIQ Score: {ciq_result.overall_score}")
```

### 3. Trust Receipt Validation (`trust_receipts.py`)

Verify cryptographic integrity of interaction records:

```python
from symbi_kit.trust_receipts import ReceiptValidator

validator = ReceiptValidator()

# Validate a single receipt
is_valid = validator.validate_receipt(receipt)

# Validate entire chain
chain_valid = validator.validate_chain(receipt_chain)
```

### 4. Statistical Analysis (`statistical_analysis.py`)

Comprehensive statistical testing and analysis:

```python
from symbi_kit.statistical_analysis import ReplicationAnalysis

analyzer = ReplicationAnalysis()
report = analyzer.run_complete_analysis(
    constitutional_data=const_data,
    directive_data=dir_data
)
```

### 5. Data Visualization (`visualization.py`)

Create publication-ready charts and reports:

```python
from symbi_kit.visualization import ReportGenerator

generator = ReportGenerator()
html_report = generator.generate_complete_report(
    analysis_results=results,
    output_path="research_report.html"
)
```

## Data Formats

### Interaction Data Structure

```json
{
  "interaction_id": "const_0001",
  "session_id": "session_001",
  "timestamp": "2024-01-15T10:30:00Z",
  "mode": "constitutional",
  "ciq_metrics": {
    "clarity": 0.85,
    "integrity": 0.92,
    "quality": 0.88,
    "breadth": 0.75,
    "safety": 0.95,
    "completion": 0.90
  },
  "flags": ["high_quality", "ethical_review"],
  "user_satisfaction": 0.87
}
```

### Trust Receipt Structure

```json
{
  "version": "1.0",
  "session_id": "session_001",
  "interaction_id": "const_0001",
  "mode": "constitutional",
  "timestamp": "2024-01-15T10:30:00Z",
  "ciq_metrics": { ... },
  "previous_hash": "abc123...",
  "self_hash": "def456...",
  "signature": "ghi789..."
}
```

## Sample Data Generation

Generate realistic test datasets for development and testing:

```python
from symbi_kit.data import generate_comparative_dataset

# Generate sample data
dataset = generate_comparative_dataset(
    n_interactions_per_group=100,
    constitutional_bias=0.15  # Constitutional AI performs 15% better
)

# Save for later use
save_sample_dataset(dataset, "my_test_data.json")
```

## Research Workflows

### 1. Basic Replication Study

```python
# Load your data
data = load_dataset_from_file("your_data.json")

# Validate data quality
from symbi_kit.data.validation import validate_symbi_dataset
validation_report = validate_symbi_dataset(data)

if validation_report.is_valid:
    # Run A/B test
    framework = ABTestFramework()
    results = framework.run_analysis(data)
    
    # Generate report
    generator = ReportGenerator()
    generator.generate_complete_report(results, "replication_report.html")
```

### 2. Custom Analysis Pipeline

```python
from symbi_kit import (
    DataLoader, DataPreprocessor, CIQCalculator, 
    StatisticalAnalysis, VisualizationTools
)

# Load and preprocess data
loader = DataLoader()
data, metadata = loader.load_symbi_dataset("dataset.json")

preprocessor = DataPreprocessor()
normalized_data = preprocessor.normalize_ciq_metrics(data)

# Extract CIQ metrics
ciq_df = preprocessor.extract_ciq_dataframe(normalized_data)

# Run statistical analysis
analyzer = StatisticalAnalysis()
hypothesis_results = analyzer.test_ciq_superiority(
    constitutional_group=ciq_df[ciq_df['group'] == 'constitutional'],
    directive_group=ciq_df[ciq_df['group'] == 'directive']
)

# Create visualizations
viz = VisualizationTools()
viz.plot_ciq_comparison(ciq_df, save_path="ciq_comparison.png")
```

## Command Line Tools

The kit includes several CLI tools for common tasks:

### A/B Test Analysis

```bash
# Run A/B test on dataset
symbi-ab-test --data dataset.json --output results.json

# With custom configuration
symbi-ab-test --data dataset.json --config test_config.json --output results.json
```

### Data Validation

```bash
# Validate dataset
symbi-validate --data dataset.json --schema schema.json

# Quick validation
symbi-validate --data dataset.json --quick
```

### Receipt Verification

```bash
# Verify trust receipt chain
symbi-verify-receipts --data dataset.json --output verification_report.json
```

## Configuration

### Test Configuration

Create a `test_config.json` file:

```json
{
  "name": "My Replication Study",
  "hypothesis": "Constitutional AI improves CIQ metrics",
  "alpha": 0.05,
  "power": 0.8,
  "effect_size": 0.3,
  "metrics_to_test": ["clarity", "integrity", "quality"],
  "statistical_tests": ["t_test", "mann_whitney", "bootstrap"]
}
```

### Visualization Configuration

Create a `viz_config.json` file:

```json
{
  "theme": "publication",
  "color_scheme": "symbi",
  "figure_size": [12, 8],
  "dpi": 300,
  "font_size": 12,
  "save_formats": ["png", "pdf", "svg"]
}
```

## Advanced Features

### Custom Metrics

Define your own CIQ metrics:

```python
from symbi_kit.ciq_metrics import BaseMetric

class CustomMetric(BaseMetric):
    def calculate(self, interaction_data):
        # Your custom calculation logic
        return score, explanation, confidence

# Register and use
calculator = CIQCalculator()
calculator.add_custom_metric("my_metric", CustomMetric())
```

### Custom Validation Rules

Add domain-specific validation:

```python
from symbi_kit.data.validation import DataValidator, ValidationRule

def check_custom_rule(data, parameters):
    # Your validation logic
    return issues

validator = DataValidator()
validator.add_rule(ValidationRule(
    name="custom_check",
    description="Custom validation rule",
    severity="warning",
    check_function=check_custom_rule
))
```

### Interactive Analysis

Use Jupyter notebooks for interactive analysis:

```python
# In Jupyter notebook
from symbi_kit.visualization import InteractiveVisualizer

viz = InteractiveVisualizer()

# Create interactive dashboard
dashboard = viz.create_ciq_dashboard(data)
dashboard.show()
```

## Data Privacy and Ethics

The SYMBI Replication Kit is designed with privacy and ethics in mind:

- **No Personal Data**: Sample data generators create synthetic, non-personal data
- **Cryptographic Verification**: Trust receipts ensure data integrity without exposing content
- **Configurable Anonymization**: Tools for removing or hashing sensitive identifiers
- **Ethical Guidelines**: Built-in checks for responsible AI research practices

## Contributing

We welcome contributions to the SYMBI Replication Kit:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/new-analysis`
3. **Add tests**: Ensure your code is well-tested
4. **Submit a pull request**: Include clear description of changes

### Development Setup

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/

# Run linting
flake8 symbi_kit/
black symbi_kit/

# Generate documentation
cd docs/
make html
```

## Testing

The kit includes comprehensive tests:

```bash
# Run all tests
pytest

# Run specific test categories
pytest tests/test_ab_testing.py
pytest tests/test_ciq_metrics.py
pytest tests/test_trust_receipts.py

# Run with coverage
pytest --cov=symbi_kit --cov-report=html
```

## Documentation

Full documentation is available:

- **API Reference**: Detailed function and class documentation
- **Tutorials**: Step-by-step guides for common workflows
- **Examples**: Complete example analyses and use cases
- **Research Papers**: Links to relevant SYMBI research publications

## Troubleshooting

### Common Issues

**ImportError: No module named 'symbi_kit'**
```bash
# Ensure package is installed
pip install -e .
```

**Validation Errors**
```python
# Check data format
from symbi_kit.data.validation import ValidationReporter
ValidationReporter.print_report(validation_report, detailed=True)
```

**Statistical Test Failures**
```python
# Check sample sizes and data distribution
from symbi_kit.statistical_analysis import PowerAnalysis
power_analysis = PowerAnalysis()
power_analysis.calculate_required_sample_size(effect_size=0.3, power=0.8)
```

### Getting Help

- **GitHub Issues**: Report bugs and request features
- **Discussions**: Ask questions and share insights
- **Documentation**: Check the full documentation
- **Examples**: Review example notebooks and scripts

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Citation

If you use the SYMBI Replication Kit in your research, please cite:

```bibtex
@software{symbi_replication_kit,
  title={SYMBI Replication Kit: Tools for Constitutional AI Research},
  author={SYMBI Research Team},
  year={2024},
  url={https://github.com/symbi/replication-kit},
  version={1.0.0}
}
```

## Acknowledgments

- SYMBI Research Team for the foundational constitutional AI research
- Contributors to the open-source scientific Python ecosystem
- Researchers and practitioners providing feedback and validation

## Roadmap

### Version 1.1 (Planned)
- [ ] Real-time analysis dashboard
- [ ] Integration with popular ML frameworks
- [ ] Advanced statistical methods
- [ ] Multi-language support

### Version 1.2 (Future)
- [ ] Distributed analysis capabilities
- [ ] Cloud deployment options
- [ ] Advanced visualization templates
- [ ] Integration with research databases

---

**Ready to replicate SYMBI research?** Start with the [Quick Start](#quick-start) guide and explore the [examples](examples/) directory for complete workflows.

For questions, issues, or contributions, please visit our [GitHub repository](https://github.com/symbi/replication-kit).