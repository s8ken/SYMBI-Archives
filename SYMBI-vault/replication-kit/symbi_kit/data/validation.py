"""
Data Validation: Ensure data quality and integrity

This module provides comprehensive validation for SYMBI research data,
including schema validation, statistical checks, and data quality assessment.
"""

import json
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import jsonschema
from pathlib import Path
import hashlib
import re
import logging


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ValidationRule:
    """A single validation rule."""
    name: str
    description: str
    severity: str  # 'error', 'warning', 'info'
    check_function: callable
    parameters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ValidationIssue:
    """A validation issue found in data."""
    rule_name: str
    severity: str
    message: str
    location: str
    value: Any = None
    expected: Any = None
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ValidationReport:
    """Complete validation report."""
    dataset_name: str
    validation_timestamp: datetime
    total_records: int
    issues: List[ValidationIssue]
    passed_rules: List[str]
    failed_rules: List[str]
    warnings: List[str]
    summary: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_valid(self) -> bool:
        """Check if validation passed (no errors)."""
        return len([issue for issue in self.issues if issue.severity == 'error']) == 0
    
    @property
    def error_count(self) -> int:
        """Count of error-level issues."""
        return len([issue for issue in self.issues if issue.severity == 'error'])
    
    @property
    def warning_count(self) -> int:
        """Count of warning-level issues."""
        return len([issue for issue in self.issues if issue.severity == 'warning'])


class DataValidator:
    """Comprehensive data validator for SYMBI research data."""
    
    def __init__(self, schema_path: Optional[str] = None):
        """
        Initialize data validator.
        
        Args:
            schema_path: Path to JSON schema file
        """
        self.schema_path = schema_path
        self.schema = None
        self.rules = []
        
        if schema_path and Path(schema_path).exists():
            self.schema = self._load_schema(schema_path)
        
        self._setup_default_rules()
    
    def _load_schema(self, schema_path: str) -> Dict[str, Any]:
        """Load JSON schema for validation."""
        try:
            with open(schema_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load schema from {schema_path}: {e}")
            return {}
    
    def _setup_default_rules(self):
        """Setup default validation rules."""
        
        # Schema validation rule
        if self.schema:
            self.add_rule(ValidationRule(
                name="schema_compliance",
                description="Data must comply with JSON schema",
                severity="error",
                check_function=self._check_schema_compliance
            ))
        
        # CIQ metrics validation
        self.add_rule(ValidationRule(
            name="ciq_metrics_range",
            description="CIQ metrics must be in range [0, 1]",
            severity="error",
            check_function=self._check_ciq_metrics_range
        ))
        
        self.add_rule(ValidationRule(
            name="ciq_metrics_completeness",
            description="All required CIQ metrics must be present",
            severity="error",
            check_function=self._check_ciq_metrics_completeness,
            parameters={"required_metrics": ["clarity", "integrity", "quality"]}
        ))
        
        # Timestamp validation
        self.add_rule(ValidationRule(
            name="timestamp_format",
            description="Timestamps must be valid ISO format",
            severity="error",
            check_function=self._check_timestamp_format
        ))
        
        self.add_rule(ValidationRule(
            name="timestamp_chronology",
            description="Timestamps should be in chronological order within sessions",
            severity="warning",
            check_function=self._check_timestamp_chronology
        ))
        
        # Trust receipt validation
        self.add_rule(ValidationRule(
            name="receipt_hash_integrity",
            description="Trust receipt hashes must be valid",
            severity="error",
            check_function=self._check_receipt_hash_integrity
        ))
        
        self.add_rule(ValidationRule(
            name="receipt_chain_integrity",
            description="Trust receipt chains must be valid",
            severity="error",
            check_function=self._check_receipt_chain_integrity
        ))
        
        # Data consistency validation
        self.add_rule(ValidationRule(
            name="interaction_receipt_consistency",
            description="Interactions and receipts must be consistent",
            severity="error",
            check_function=self._check_interaction_receipt_consistency
        ))
        
        # Statistical validation
        self.add_rule(ValidationRule(
            name="statistical_outliers",
            description="Check for statistical outliers in CIQ metrics",
            severity="warning",
            check_function=self._check_statistical_outliers,
            parameters={"z_threshold": 3.0}
        ))
        
        # Data quality validation
        self.add_rule(ValidationRule(
            name="missing_values",
            description="Check for missing critical values",
            severity="warning",
            check_function=self._check_missing_values
        ))
        
        self.add_rule(ValidationRule(
            name="duplicate_records",
            description="Check for duplicate interaction records",
            severity="warning",
            check_function=self._check_duplicate_records
        ))
    
    def add_rule(self, rule: ValidationRule):
        """Add a validation rule."""
        self.rules.append(rule)
    
    def validate(self, data: Dict[str, Any], dataset_name: str = "unknown") -> ValidationReport:
        """
        Validate data against all rules.
        
        Args:
            data: Data to validate
            dataset_name: Name of the dataset
            
        Returns:
            Validation report
        """
        issues = []
        passed_rules = []
        failed_rules = []
        warnings = []
        
        # Count total records
        total_records = self._count_records(data)
        
        # Run each validation rule
        for rule in self.rules:
            try:
                rule_issues = rule.check_function(data, rule.parameters)
                
                if rule_issues:
                    failed_rules.append(rule.name)
                    issues.extend(rule_issues)
                    
                    if rule.severity == 'warning':
                        warnings.append(f"{rule.name}: {rule.description}")
                else:
                    passed_rules.append(rule.name)
                    
            except Exception as e:
                error_issue = ValidationIssue(
                    rule_name=rule.name,
                    severity="error",
                    message=f"Validation rule failed to execute: {str(e)}",
                    location="validation_system"
                )
                issues.append(error_issue)
                failed_rules.append(rule.name)
        
        # Create summary
        summary = {
            "total_rules": len(self.rules),
            "passed_rules": len(passed_rules),
            "failed_rules": len(failed_rules),
            "total_issues": len(issues),
            "error_issues": len([i for i in issues if i.severity == 'error']),
            "warning_issues": len([i for i in issues if i.severity == 'warning']),
            "info_issues": len([i for i in issues if i.severity == 'info'])
        }
        
        return ValidationReport(
            dataset_name=dataset_name,
            validation_timestamp=datetime.now(),
            total_records=total_records,
            issues=issues,
            passed_rules=passed_rules,
            failed_rules=failed_rules,
            warnings=warnings,
            summary=summary
        )
    
    def _count_records(self, data: Dict[str, Any]) -> int:
        """Count total records in dataset."""
        count = 0
        
        # Count interactions
        for group in ['constitutional', 'directive']:
            if (group in data and 
                isinstance(data[group], dict) and 
                'interactions' in data[group]):
                count += len(data[group]['interactions'])
        
        # Count receipts
        for group in ['constitutional', 'directive']:
            if (group in data and 
                isinstance(data[group], dict) and 
                'receipts' in data[group]):
                count += len(data[group]['receipts'])
        
        return count
    
    # Validation rule implementations
    def _check_schema_compliance(self, data: Dict[str, Any], 
                               parameters: Dict[str, Any]) -> List[ValidationIssue]:
        """Check JSON schema compliance."""
        issues = []
        
        try:
            jsonschema.validate(data, self.schema)
        except jsonschema.ValidationError as e:
            issues.append(ValidationIssue(
                rule_name="schema_compliance",
                severity="error",
                message=f"Schema validation failed: {e.message}",
                location=f"$.{'.'.join(str(p) for p in e.absolute_path)}",
                value=e.instance
            ))
        except Exception as e:
            issues.append(ValidationIssue(
                rule_name="schema_compliance",
                severity="error",
                message=f"Schema validation error: {str(e)}",
                location="root"
            ))
        
        return issues
    
    def _check_ciq_metrics_range(self, data: Dict[str, Any], 
                               parameters: Dict[str, Any]) -> List[ValidationIssue]:
        """Check CIQ metrics are in valid range [0, 1]."""
        issues = []
        
        def check_metrics(interactions, group_name):
            for i, interaction in enumerate(interactions):
                if 'ciq_metrics' in interaction:
                    metrics = interaction['ciq_metrics']
                    for metric_name, value in metrics.items():
                        if isinstance(value, (int, float)):
                            if value < 0 or value > 1:
                                issues.append(ValidationIssue(
                                    rule_name="ciq_metrics_range",
                                    severity="error",
                                    message=f"CIQ metric '{metric_name}' out of range [0, 1]",
                                    location=f"{group_name}.interactions[{i}].ciq_metrics.{metric_name}",
                                    value=value,
                                    expected="[0, 1]"
                                ))
        
        # Check all groups
        for group in ['constitutional', 'directive']:
            if (group in data and 
                'interactions' in data[group]):
                check_metrics(data[group]['interactions'], group)
        
        return issues
    
    def _check_ciq_metrics_completeness(self, data: Dict[str, Any], 
                                      parameters: Dict[str, Any]) -> List[ValidationIssue]:
        """Check all required CIQ metrics are present."""
        issues = []
        required_metrics = parameters.get('required_metrics', ['clarity', 'integrity', 'quality'])
        
        def check_completeness(interactions, group_name):
            for i, interaction in enumerate(interactions):
                if 'ciq_metrics' in interaction:
                    metrics = interaction['ciq_metrics']
                    for required_metric in required_metrics:
                        if required_metric not in metrics:
                            issues.append(ValidationIssue(
                                rule_name="ciq_metrics_completeness",
                                severity="error",
                                message=f"Missing required CIQ metric: {required_metric}",
                                location=f"{group_name}.interactions[{i}].ciq_metrics",
                                expected=required_metrics
                            ))
                else:
                    issues.append(ValidationIssue(
                        rule_name="ciq_metrics_completeness",
                        severity="error",
                        message="Missing ciq_metrics object",
                        location=f"{group_name}.interactions[{i}]"
                    ))
        
        # Check all groups
        for group in ['constitutional', 'directive']:
            if (group in data and 
                'interactions' in data[group]):
                check_completeness(data[group]['interactions'], group)
        
        return issues
    
    def _check_timestamp_format(self, data: Dict[str, Any], 
                              parameters: Dict[str, Any]) -> List[ValidationIssue]:
        """Check timestamp format validity."""
        issues = []
        
        def check_timestamps(interactions, group_name):
            for i, interaction in enumerate(interactions):
                if 'timestamp' in interaction:
                    timestamp = interaction['timestamp']
                    try:
                        if isinstance(timestamp, str):
                            datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        elif not isinstance(timestamp, datetime):
                            raise ValueError("Invalid timestamp type")
                    except Exception as e:
                        issues.append(ValidationIssue(
                            rule_name="timestamp_format",
                            severity="error",
                            message=f"Invalid timestamp format: {str(e)}",
                            location=f"{group_name}.interactions[{i}].timestamp",
                            value=timestamp
                        ))
        
        # Check all groups
        for group in ['constitutional', 'directive']:
            if (group in data and 
                'interactions' in data[group]):
                check_timestamps(data[group]['interactions'], group)
        
        return issues
    
    def _check_timestamp_chronology(self, data: Dict[str, Any], 
                                  parameters: Dict[str, Any]) -> List[ValidationIssue]:
        """Check timestamp chronological order within sessions."""
        issues = []
        
        def check_chronology(interactions, group_name):
            # Group by session
            sessions = {}
            for interaction in interactions:
                session_id = interaction.get('session_id')
                if session_id:
                    if session_id not in sessions:
                        sessions[session_id] = []
                    sessions[session_id].append(interaction)
            
            # Check chronology within each session
            for session_id, session_interactions in sessions.items():
                timestamps = []
                for interaction in session_interactions:
                    if 'timestamp' in interaction:
                        try:
                            if isinstance(interaction['timestamp'], str):
                                ts = datetime.fromisoformat(interaction['timestamp'].replace('Z', '+00:00'))
                            else:
                                ts = interaction['timestamp']
                            timestamps.append((ts, interaction.get('interaction_id')))
                        except:
                            continue
                
                # Check if sorted
                sorted_timestamps = sorted(timestamps, key=lambda x: x[0])
                if timestamps != sorted_timestamps:
                    issues.append(ValidationIssue(
                        rule_name="timestamp_chronology",
                        severity="warning",
                        message=f"Timestamps not in chronological order in session {session_id}",
                        location=f"{group_name}.session.{session_id}"
                    ))
        
        # Check all groups
        for group in ['constitutional', 'directive']:
            if (group in data and 
                'interactions' in data[group]):
                check_chronology(data[group]['interactions'], group)
        
        return issues
    
    def _check_receipt_hash_integrity(self, data: Dict[str, Any], 
                                    parameters: Dict[str, Any]) -> List[ValidationIssue]:
        """Check trust receipt hash integrity."""
        issues = []
        
        def check_hashes(receipts, group_name):
            for i, receipt in enumerate(receipts):
                if 'self_hash' in receipt:
                    # Recreate hash and compare
                    receipt_copy = receipt.copy()
                    stored_hash = receipt_copy.pop('self_hash')
                    receipt_copy.pop('signature', None)  # Remove signature for hash calculation
                    
                    # Calculate expected hash
                    receipt_json = json.dumps(receipt_copy, sort_keys=True, default=str)
                    expected_hash = hashlib.sha256(receipt_json.encode()).hexdigest()
                    
                    if stored_hash != expected_hash:
                        issues.append(ValidationIssue(
                            rule_name="receipt_hash_integrity",
                            severity="error",
                            message="Trust receipt hash mismatch",
                            location=f"{group_name}.receipts[{i}].self_hash",
                            value=stored_hash,
                            expected=expected_hash
                        ))
        
        # Check all groups
        for group in ['constitutional', 'directive']:
            if (group in data and 
                'receipts' in data[group]):
                check_hashes(data[group]['receipts'], group)
        
        return issues
    
    def _check_receipt_chain_integrity(self, data: Dict[str, Any], 
                                     parameters: Dict[str, Any]) -> List[ValidationIssue]:
        """Check trust receipt chain integrity."""
        issues = []
        
        def check_chain(receipts, group_name):
            if len(receipts) < 2:
                return
            
            for i in range(1, len(receipts)):
                current_receipt = receipts[i]
                previous_receipt = receipts[i-1]
                
                if 'previous_hash' in current_receipt and 'self_hash' in previous_receipt:
                    if current_receipt['previous_hash'] != previous_receipt['self_hash']:
                        issues.append(ValidationIssue(
                            rule_name="receipt_chain_integrity",
                            severity="error",
                            message="Trust receipt chain broken",
                            location=f"{group_name}.receipts[{i}].previous_hash",
                            value=current_receipt['previous_hash'],
                            expected=previous_receipt['self_hash']
                        ))
        
        # Check all groups
        for group in ['constitutional', 'directive']:
            if (group in data and 
                'receipts' in data[group]):
                check_chain(data[group]['receipts'], group)
        
        return issues
    
    def _check_interaction_receipt_consistency(self, data: Dict[str, Any], 
                                             parameters: Dict[str, Any]) -> List[ValidationIssue]:
        """Check consistency between interactions and receipts."""
        issues = []
        
        for group in ['constitutional', 'directive']:
            if (group in data and 
                'interactions' in data[group] and 
                'receipts' in data[group]):
                
                interactions = data[group]['interactions']
                receipts = data[group]['receipts']
                
                # Create lookup maps
                interaction_ids = {i.get('interaction_id') for i in interactions}
                receipt_ids = {r.get('interaction_id') for r in receipts}
                
                # Check for missing receipts
                missing_receipts = interaction_ids - receipt_ids
                for missing_id in missing_receipts:
                    if missing_id:  # Skip None values
                        issues.append(ValidationIssue(
                            rule_name="interaction_receipt_consistency",
                            severity="error",
                            message=f"Missing receipt for interaction {missing_id}",
                            location=f"{group}.receipts"
                        ))
                
                # Check for orphaned receipts
                orphaned_receipts = receipt_ids - interaction_ids
                for orphaned_id in orphaned_receipts:
                    if orphaned_id:  # Skip None values
                        issues.append(ValidationIssue(
                            rule_name="interaction_receipt_consistency",
                            severity="warning",
                            message=f"Orphaned receipt for interaction {orphaned_id}",
                            location=f"{group}.receipts"
                        ))
        
        return issues
    
    def _check_statistical_outliers(self, data: Dict[str, Any], 
                                  parameters: Dict[str, Any]) -> List[ValidationIssue]:
        """Check for statistical outliers in CIQ metrics."""
        issues = []
        z_threshold = parameters.get('z_threshold', 3.0)
        
        # Collect all CIQ metrics
        all_metrics = {}
        
        for group in ['constitutional', 'directive']:
            if (group in data and 
                'interactions' in data[group]):
                
                for interaction in data[group]['interactions']:
                    if 'ciq_metrics' in interaction:
                        for metric_name, value in interaction['ciq_metrics'].items():
                            if isinstance(value, (int, float)):
                                if metric_name not in all_metrics:
                                    all_metrics[metric_name] = []
                                all_metrics[metric_name].append(value)
        
        # Check for outliers
        for metric_name, values in all_metrics.items():
            if len(values) > 3:  # Need at least 3 values for meaningful statistics
                values_array = np.array(values)
                mean_val = np.mean(values_array)
                std_val = np.std(values_array)
                
                if std_val > 0:  # Avoid division by zero
                    z_scores = np.abs((values_array - mean_val) / std_val)
                    outlier_indices = np.where(z_scores > z_threshold)[0]
                    
                    for idx in outlier_indices:
                        issues.append(ValidationIssue(
                            rule_name="statistical_outliers",
                            severity="warning",
                            message=f"Statistical outlier detected in {metric_name}",
                            location=f"metrics.{metric_name}",
                            value=values[idx],
                            expected=f"within {z_threshold} standard deviations"
                        ))
        
        return issues
    
    def _check_missing_values(self, data: Dict[str, Any], 
                            parameters: Dict[str, Any]) -> List[ValidationIssue]:
        """Check for missing critical values."""
        issues = []
        
        critical_fields = [
            'interaction_id', 'session_id', 'timestamp', 'ciq_metrics'
        ]
        
        def check_missing(interactions, group_name):
            for i, interaction in enumerate(interactions):
                for field in critical_fields:
                    if field not in interaction or interaction[field] is None:
                        issues.append(ValidationIssue(
                            rule_name="missing_values",
                            severity="warning",
                            message=f"Missing critical field: {field}",
                            location=f"{group_name}.interactions[{i}]"
                        ))
        
        # Check all groups
        for group in ['constitutional', 'directive']:
            if (group in data and 
                'interactions' in data[group]):
                check_missing(data[group]['interactions'], group)
        
        return issues
    
    def _check_duplicate_records(self, data: Dict[str, Any], 
                               parameters: Dict[str, Any]) -> List[ValidationIssue]:
        """Check for duplicate interaction records."""
        issues = []
        
        def check_duplicates(interactions, group_name):
            seen_ids = set()
            for i, interaction in enumerate(interactions):
                interaction_id = interaction.get('interaction_id')
                if interaction_id:
                    if interaction_id in seen_ids:
                        issues.append(ValidationIssue(
                            rule_name="duplicate_records",
                            severity="warning",
                            message=f"Duplicate interaction ID: {interaction_id}",
                            location=f"{group_name}.interactions[{i}]",
                            value=interaction_id
                        ))
                    else:
                        seen_ids.add(interaction_id)
        
        # Check all groups
        for group in ['constitutional', 'directive']:
            if (group in data and 
                'interactions' in data[group]):
                check_duplicates(data[group]['interactions'], group)
        
        return issues


class ValidationReporter:
    """Generate validation reports in various formats."""
    
    @staticmethod
    def print_report(report: ValidationReport, detailed: bool = False):
        """Print validation report to console."""
        print(f"\n{'='*60}")
        print(f"VALIDATION REPORT: {report.dataset_name}")
        print(f"{'='*60}")
        print(f"Validation Time: {report.validation_timestamp}")
        print(f"Total Records: {report.total_records}")
        print(f"Overall Status: {'✓ PASSED' if report.is_valid else '✗ FAILED'}")
        
        print(f"\nSUMMARY:")
        print(f"  Total Rules: {report.summary['total_rules']}")
        print(f"  Passed: {report.summary['passed_rules']}")
        print(f"  Failed: {report.summary['failed_rules']}")
        print(f"  Errors: {report.summary['error_issues']}")
        print(f"  Warnings: {report.summary['warning_issues']}")
        
        if detailed and report.issues:
            print(f"\nISSUES:")
            for issue in report.issues:
                severity_symbol = "✗" if issue.severity == "error" else "⚠" if issue.severity == "warning" else "ℹ"
                print(f"  {severity_symbol} [{issue.severity.upper()}] {issue.rule_name}")
                print(f"    {issue.message}")
                print(f"    Location: {issue.location}")
                if issue.value is not None:
                    print(f"    Value: {issue.value}")
                if issue.expected is not None:
                    print(f"    Expected: {issue.expected}")
                print()
    
    @staticmethod
    def to_json(report: ValidationReport) -> str:
        """Convert validation report to JSON."""
        report_dict = {
            'dataset_name': report.dataset_name,
            'validation_timestamp': report.validation_timestamp.isoformat(),
            'total_records': report.total_records,
            'is_valid': report.is_valid,
            'summary': report.summary,
            'issues': [
                {
                    'rule_name': issue.rule_name,
                    'severity': issue.severity,
                    'message': issue.message,
                    'location': issue.location,
                    'value': issue.value,
                    'expected': issue.expected,
                    'timestamp': issue.timestamp.isoformat()
                }
                for issue in report.issues
            ],
            'passed_rules': report.passed_rules,
            'failed_rules': report.failed_rules,
            'warnings': report.warnings
        }
        
        return json.dumps(report_dict, indent=2)
    
    @staticmethod
    def to_html(report: ValidationReport) -> str:
        """Convert validation report to HTML."""
        status_color = "green" if report.is_valid else "red"
        status_text = "PASSED" if report.is_valid else "FAILED"
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Validation Report: {report.dataset_name}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
                .status {{ color: {status_color}; font-weight: bold; }}
                .summary {{ margin: 20px 0; }}
                .issues {{ margin: 20px 0; }}
                .error {{ color: red; }}
                .warning {{ color: orange; }}
                .info {{ color: blue; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Validation Report: {report.dataset_name}</h1>
                <p>Validation Time: {report.validation_timestamp}</p>
                <p>Total Records: {report.total_records}</p>
                <p class="status">Status: {status_text}</p>
            </div>
            
            <div class="summary">
                <h2>Summary</h2>
                <table>
                    <tr><th>Metric</th><th>Count</th></tr>
                    <tr><td>Total Rules</td><td>{report.summary['total_rules']}</td></tr>
                    <tr><td>Passed Rules</td><td>{report.summary['passed_rules']}</td></tr>
                    <tr><td>Failed Rules</td><td>{report.summary['failed_rules']}</td></tr>
                    <tr><td>Errors</td><td>{report.summary['error_issues']}</td></tr>
                    <tr><td>Warnings</td><td>{report.summary['warning_issues']}</td></tr>
                </table>
            </div>
        """
        
        if report.issues:
            html += """
            <div class="issues">
                <h2>Issues</h2>
                <table>
                    <tr><th>Severity</th><th>Rule</th><th>Message</th><th>Location</th></tr>
            """
            
            for issue in report.issues:
                severity_class = issue.severity
                html += f"""
                    <tr class="{severity_class}">
                        <td>{issue.severity.upper()}</td>
                        <td>{issue.rule_name}</td>
                        <td>{issue.message}</td>
                        <td>{issue.location}</td>
                    </tr>
                """
            
            html += """
                </table>
            </div>
            """
        
        html += """
        </body>
        </html>
        """
        
        return html


# Utility functions
def validate_symbi_dataset(data: Dict[str, Any], 
                          schema_path: Optional[str] = None,
                          dataset_name: str = "unknown") -> ValidationReport:
    """
    Quick function to validate a SYMBI dataset.
    
    Args:
        data: Dataset to validate
        schema_path: Path to JSON schema
        dataset_name: Name of the dataset
        
    Returns:
        Validation report
    """
    validator = DataValidator(schema_path)
    return validator.validate(data, dataset_name)


def quick_validate(data: Dict[str, Any]) -> bool:
    """
    Quick validation check - returns True if valid, False otherwise.
    
    Args:
        data: Dataset to validate
        
    Returns:
        True if valid, False otherwise
    """
    validator = DataValidator()
    report = validator.validate(data)
    return report.is_valid


# Example usage
if __name__ == "__main__":
    # Load sample data for testing
    from .sample_data import load_sample_dataset
    
    # Generate sample data
    sample_data = load_sample_dataset('comparative', 'small')
    
    # Validate the data
    validator = DataValidator()
    report = validator.validate(sample_data, "sample_comparative_small")
    
    # Print report
    ValidationReporter.print_report(report, detailed=True)
    
    print(f"\nValidation {'PASSED' if report.is_valid else 'FAILED'}")
    print(f"Errors: {report.error_count}, Warnings: {report.warning_count}")