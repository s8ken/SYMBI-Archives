"""
Data Loading Utilities: Load and validate research data

This module provides utilities for loading, validating, and preprocessing
data for SYMBI constitutional AI research.
"""

import json
import csv
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime
import logging
from dataclasses import dataclass
import jsonschema
from urllib.parse import urlparse
import requests


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class DataValidationResult:
    """Result of data validation."""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    record_count: int
    schema_version: Optional[str] = None


@dataclass
class DatasetMetadata:
    """Metadata for a loaded dataset."""
    name: str
    source: str
    format: str
    record_count: int
    columns: List[str]
    date_range: Optional[Tuple[datetime, datetime]]
    schema_version: Optional[str]
    loaded_at: datetime
    validation_result: Optional[DataValidationResult] = None


class DataLoader:
    """Load and validate research data from various sources."""
    
    def __init__(self, schema_path: Optional[str] = None):
        """
        Initialize data loader.
        
        Args:
            schema_path: Path to JSON schema for validation
        """
        self.schema_path = schema_path
        self.schema = None
        if schema_path and Path(schema_path).exists():
            self.schema = self._load_schema(schema_path)
    
    def _load_schema(self, schema_path: str) -> Dict[str, Any]:
        """Load JSON schema for validation."""
        try:
            with open(schema_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load schema from {schema_path}: {e}")
            return {}
    
    def load_json(self, filepath: str, validate: bool = True) -> Tuple[Dict[str, Any], DatasetMetadata]:
        """
        Load data from JSON file.
        
        Args:
            filepath: Path to JSON file
            validate: Whether to validate against schema
            
        Returns:
            Tuple of (data, metadata)
        """
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            # Create metadata
            metadata = DatasetMetadata(
                name=Path(filepath).stem,
                source=filepath,
                format='json',
                record_count=self._count_records(data),
                columns=self._extract_columns(data),
                date_range=self._extract_date_range(data),
                schema_version=data.get('version'),
                loaded_at=datetime.now()
            )
            
            # Validate if requested and schema available
            if validate and self.schema:
                validation_result = self._validate_data(data)
                metadata.validation_result = validation_result
                
                if not validation_result.is_valid:
                    logger.warning(f"Data validation failed: {validation_result.errors}")
            
            logger.info(f"Loaded JSON data: {metadata.record_count} records from {filepath}")
            return data, metadata
            
        except Exception as e:
            logger.error(f"Error loading JSON from {filepath}: {e}")
            raise
    
    def load_csv(self, filepath: str, **kwargs) -> Tuple[pd.DataFrame, DatasetMetadata]:
        """
        Load data from CSV file.
        
        Args:
            filepath: Path to CSV file
            **kwargs: Additional arguments for pandas.read_csv
            
        Returns:
            Tuple of (dataframe, metadata)
        """
        try:
            df = pd.read_csv(filepath, **kwargs)
            
            # Create metadata
            metadata = DatasetMetadata(
                name=Path(filepath).stem,
                source=filepath,
                format='csv',
                record_count=len(df),
                columns=df.columns.tolist(),
                date_range=self._extract_date_range_df(df),
                schema_version=None,
                loaded_at=datetime.now()
            )
            
            logger.info(f"Loaded CSV data: {len(df)} records from {filepath}")
            return df, metadata
            
        except Exception as e:
            logger.error(f"Error loading CSV from {filepath}: {e}")
            raise
    
    def load_excel(self, filepath: str, sheet_name: Optional[str] = None, 
                   **kwargs) -> Tuple[pd.DataFrame, DatasetMetadata]:
        """
        Load data from Excel file.
        
        Args:
            filepath: Path to Excel file
            sheet_name: Name of sheet to load
            **kwargs: Additional arguments for pandas.read_excel
            
        Returns:
            Tuple of (dataframe, metadata)
        """
        try:
            df = pd.read_excel(filepath, sheet_name=sheet_name, **kwargs)
            
            # Create metadata
            metadata = DatasetMetadata(
                name=f"{Path(filepath).stem}_{sheet_name or 'default'}",
                source=filepath,
                format='excel',
                record_count=len(df),
                columns=df.columns.tolist(),
                date_range=self._extract_date_range_df(df),
                schema_version=None,
                loaded_at=datetime.now()
            )
            
            logger.info(f"Loaded Excel data: {len(df)} records from {filepath}")
            return df, metadata
            
        except Exception as e:
            logger.error(f"Error loading Excel from {filepath}: {e}")
            raise
    
    def load_from_url(self, url: str, format: str = 'json', 
                      **kwargs) -> Tuple[Union[Dict, pd.DataFrame], DatasetMetadata]:
        """
        Load data from URL.
        
        Args:
            url: URL to load data from
            format: Data format ('json', 'csv')
            **kwargs: Additional arguments for loading
            
        Returns:
            Tuple of (data, metadata)
        """
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            if format == 'json':
                data = response.json()
                metadata = DatasetMetadata(
                    name=urlparse(url).path.split('/')[-1],
                    source=url,
                    format='json',
                    record_count=self._count_records(data),
                    columns=self._extract_columns(data),
                    date_range=self._extract_date_range(data),
                    schema_version=data.get('version'),
                    loaded_at=datetime.now()
                )
                
            elif format == 'csv':
                from io import StringIO
                df = pd.read_csv(StringIO(response.text), **kwargs)
                data = df
                metadata = DatasetMetadata(
                    name=urlparse(url).path.split('/')[-1],
                    source=url,
                    format='csv',
                    record_count=len(df),
                    columns=df.columns.tolist(),
                    date_range=self._extract_date_range_df(df),
                    schema_version=None,
                    loaded_at=datetime.now()
                )
            else:
                raise ValueError(f"Unsupported format: {format}")
            
            logger.info(f"Loaded data from URL: {metadata.record_count} records from {url}")
            return data, metadata
            
        except Exception as e:
            logger.error(f"Error loading data from {url}: {e}")
            raise
    
    def load_symbi_dataset(self, dataset_path: str) -> Tuple[Dict[str, Any], DatasetMetadata]:
        """
        Load a SYMBI-formatted dataset with validation.
        
        Args:
            dataset_path: Path to SYMBI dataset
            
        Returns:
            Tuple of (dataset, metadata)
        """
        # Load the main dataset
        data, metadata = self.load_json(dataset_path, validate=True)
        
        # Additional SYMBI-specific validation
        validation_errors = []
        validation_warnings = []
        
        # Check for required SYMBI structure
        if 'experiment_metadata' not in data:
            validation_errors.append("Missing experiment_metadata")
        
        # Check for interaction data
        has_interactions = False
        for group in ['constitutional', 'directive']:
            if group in data and 'interactions' in data[group]:
                has_interactions = True
                interactions = data[group]['interactions']
                
                # Validate interaction structure
                for i, interaction in enumerate(interactions):
                    if 'ciq_metrics' not in interaction:
                        validation_errors.append(f"{group} interaction {i}: missing ciq_metrics")
                    if 'timestamp' not in interaction:
                        validation_errors.append(f"{group} interaction {i}: missing timestamp")
        
        if not has_interactions:
            validation_errors.append("No interaction data found")
        
        # Update validation result
        if metadata.validation_result:
            metadata.validation_result.errors.extend(validation_errors)
            metadata.validation_result.warnings.extend(validation_warnings)
            metadata.validation_result.is_valid = (
                metadata.validation_result.is_valid and len(validation_errors) == 0
            )
        else:
            metadata.validation_result = DataValidationResult(
                is_valid=len(validation_errors) == 0,
                errors=validation_errors,
                warnings=validation_warnings,
                record_count=metadata.record_count
            )
        
        return data, metadata
    
    def _validate_data(self, data: Dict[str, Any]) -> DataValidationResult:
        """Validate data against schema."""
        errors = []
        warnings = []
        
        try:
            jsonschema.validate(data, self.schema)
        except jsonschema.ValidationError as e:
            errors.append(f"Schema validation error: {e.message}")
        except Exception as e:
            errors.append(f"Validation error: {str(e)}")
        
        return DataValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            record_count=self._count_records(data)
        )
    
    def _count_records(self, data: Dict[str, Any]) -> int:
        """Count records in data structure."""
        count = 0
        
        # Handle different data structures
        if isinstance(data, dict):
            # Look for common patterns
            for key in ['interactions', 'receipts', 'data', 'records']:
                if key in data and isinstance(data[key], list):
                    count += len(data[key])
            
            # Look for nested structures
            for group in ['constitutional', 'directive']:
                if group in data and isinstance(data[group], dict):
                    for key in ['interactions', 'receipts']:
                        if key in data[group] and isinstance(data[group][key], list):
                            count += len(data[group][key])
        
        elif isinstance(data, list):
            count = len(data)
        
        return count
    
    def _extract_columns(self, data: Dict[str, Any]) -> List[str]:
        """Extract column names from data structure."""
        columns = []
        
        # Find first record to extract keys
        sample_record = None
        
        if isinstance(data, dict):
            # Look for interaction data
            for group in ['constitutional', 'directive']:
                if (group in data and 
                    isinstance(data[group], dict) and 
                    'interactions' in data[group] and 
                    len(data[group]['interactions']) > 0):
                    sample_record = data[group]['interactions'][0]
                    break
            
            # Look for other data structures
            if not sample_record:
                for key in ['interactions', 'receipts', 'data', 'records']:
                    if key in data and isinstance(data[key], list) and len(data[key]) > 0:
                        sample_record = data[key][0]
                        break
        
        elif isinstance(data, list) and len(data) > 0:
            sample_record = data[0]
        
        if sample_record and isinstance(sample_record, dict):
            columns = list(sample_record.keys())
        
        return columns
    
    def _extract_date_range(self, data: Dict[str, Any]) -> Optional[Tuple[datetime, datetime]]:
        """Extract date range from data."""
        timestamps = []
        
        # Collect timestamps from various locations
        def collect_timestamps(obj, key='timestamp'):
            if isinstance(obj, dict):
                if key in obj:
                    try:
                        if isinstance(obj[key], str):
                            timestamps.append(datetime.fromisoformat(obj[key].replace('Z', '+00:00')))
                        elif isinstance(obj[key], datetime):
                            timestamps.append(obj[key])
                    except:
                        pass
                
                for value in obj.values():
                    if isinstance(value, (dict, list)):
                        collect_timestamps(value, key)
            
            elif isinstance(obj, list):
                for item in obj:
                    if isinstance(item, (dict, list)):
                        collect_timestamps(item, key)
        
        collect_timestamps(data)
        
        if timestamps:
            return min(timestamps), max(timestamps)
        
        return None
    
    def _extract_date_range_df(self, df: pd.DataFrame) -> Optional[Tuple[datetime, datetime]]:
        """Extract date range from DataFrame."""
        date_columns = []
        
        # Find date columns
        for col in df.columns:
            if df[col].dtype == 'datetime64[ns]' or 'date' in col.lower() or 'time' in col.lower():
                try:
                    pd.to_datetime(df[col].dropna().iloc[0])
                    date_columns.append(col)
                except:
                    pass
        
        if date_columns:
            # Use first date column
            date_col = date_columns[0]
            dates = pd.to_datetime(df[date_col].dropna())
            if len(dates) > 0:
                return dates.min().to_pydatetime(), dates.max().to_pydatetime()
        
        return None


class DataPreprocessor:
    """Preprocess data for analysis."""
    
    @staticmethod
    def normalize_ciq_metrics(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize CIQ metrics to ensure consistency.
        
        Args:
            data: Dataset with CIQ metrics
            
        Returns:
            Normalized dataset
        """
        normalized_data = data.copy()
        
        def normalize_metrics(interactions):
            for interaction in interactions:
                if 'ciq_metrics' in interaction:
                    metrics = interaction['ciq_metrics']
                    
                    # Ensure all metrics are in [0, 1] range
                    for metric_name, value in metrics.items():
                        if isinstance(value, (int, float)):
                            metrics[metric_name] = max(0.0, min(1.0, float(value)))
        
        # Normalize for different data structures
        for group in ['constitutional', 'directive']:
            if (group in normalized_data and 
                'interactions' in normalized_data[group]):
                normalize_metrics(normalized_data[group]['interactions'])
        
        if 'interactions' in normalized_data:
            normalize_metrics(normalized_data['interactions'])
        
        return normalized_data
    
    @staticmethod
    def extract_ciq_dataframe(data: Dict[str, Any]) -> pd.DataFrame:
        """
        Extract CIQ metrics into a pandas DataFrame.
        
        Args:
            data: Dataset with CIQ metrics
            
        Returns:
            DataFrame with CIQ metrics
        """
        records = []
        
        def extract_from_interactions(interactions, group_name):
            for interaction in interactions:
                if 'ciq_metrics' in interaction:
                    record = {
                        'interaction_id': interaction.get('interaction_id'),
                        'session_id': interaction.get('session_id'),
                        'timestamp': interaction.get('timestamp'),
                        'group': group_name,
                        'mode': interaction.get('mode', group_name),
                        **interaction['ciq_metrics']
                    }
                    records.append(record)
        
        # Extract from different data structures
        for group in ['constitutional', 'directive']:
            if (group in data and 
                'interactions' in data[group]):
                extract_from_interactions(data[group]['interactions'], group)
        
        if 'interactions' in data:
            extract_from_interactions(data['interactions'], 'unknown')
        
        df = pd.DataFrame(records)
        
        # Convert timestamp to datetime
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        return df
    
    @staticmethod
    def calculate_summary_statistics(df: pd.DataFrame, 
                                   group_by: str = 'group') -> pd.DataFrame:
        """
        Calculate summary statistics for CIQ metrics.
        
        Args:
            df: DataFrame with CIQ metrics
            group_by: Column to group by
            
        Returns:
            DataFrame with summary statistics
        """
        ciq_columns = ['clarity', 'integrity', 'quality', 'breadth', 'safety', 'completion']
        available_columns = [col for col in ciq_columns if col in df.columns]
        
        if not available_columns:
            raise ValueError("No CIQ metric columns found in DataFrame")
        
        summary = df.groupby(group_by)[available_columns].agg([
            'count', 'mean', 'std', 'min', 'max', 'median'
        ]).round(4)
        
        return summary


# Utility functions
def load_sample_data(dataset_type: str = 'comparative', 
                    size: str = 'medium') -> Tuple[Dict[str, Any], DatasetMetadata]:
    """
    Load sample data using the sample data generator.
    
    Args:
        dataset_type: Type of dataset to load
        size: Size of dataset
        
    Returns:
        Tuple of (data, metadata)
    """
    from .sample_data import load_sample_dataset
    
    data = load_sample_dataset(dataset_type, size)
    
    metadata = DatasetMetadata(
        name=f"sample_{dataset_type}_{size}",
        source="generated",
        format="json",
        record_count=0,  # Will be calculated
        columns=[],
        date_range=None,
        schema_version="1.0",
        loaded_at=datetime.now()
    )
    
    # Calculate actual metadata
    loader = DataLoader()
    metadata.record_count = loader._count_records(data)
    metadata.columns = loader._extract_columns(data)
    metadata.date_range = loader._extract_date_range(data)
    
    return data, metadata


def quick_load_json(filepath: str) -> Dict[str, Any]:
    """Quick function to load JSON data without metadata."""
    loader = DataLoader()
    data, _ = loader.load_json(filepath, validate=False)
    return data


def quick_load_csv(filepath: str) -> pd.DataFrame:
    """Quick function to load CSV data without metadata."""
    loader = DataLoader()
    df, _ = loader.load_csv(filepath)
    return df


# Example usage
if __name__ == "__main__":
    # Initialize loader
    loader = DataLoader()
    
    # Load sample data
    data, metadata = load_sample_data('comparative', 'small')
    
    print("Loaded Sample Data:")
    print(f"Name: {metadata.name}")
    print(f"Records: {metadata.record_count}")
    print(f"Columns: {metadata.columns[:5]}...")  # First 5 columns
    print(f"Date range: {metadata.date_range}")
    
    # Extract CIQ DataFrame
    preprocessor = DataPreprocessor()
    ciq_df = preprocessor.extract_ciq_dataframe(data)
    
    print(f"\nCIQ DataFrame shape: {ciq_df.shape}")
    print(f"Groups: {ciq_df['group'].unique()}")
    
    # Calculate summary statistics
    summary = preprocessor.calculate_summary_statistics(ciq_df)
    print(f"\nSummary Statistics:")
    print(summary.head())