"""
Sample Data Generation: Create realistic test datasets

This module generates sample data for testing and demonstrating
SYMBI constitutional AI research methodologies.
"""

import random
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import uuid
import json
from dataclasses import dataclass, asdict
import hashlib


@dataclass
class SampleConfig:
    """Configuration for sample data generation."""
    n_interactions: int = 50
    n_sessions: int = 10
    constitutional_bias: float = 0.15  # How much better constitutional AI performs
    noise_level: float = 0.1  # Random variation
    learning_rate: float = 0.02  # How much improvement over time
    consistency_factor: float = 0.8  # How consistent constitutional AI is
    random_seed: Optional[int] = None


class SampleDataGenerator:
    """Generate realistic sample data for SYMBI research."""
    
    def __init__(self, config: Optional[SampleConfig] = None):
        """
        Initialize sample data generator.
        
        Args:
            config: Configuration for data generation
        """
        self.config = config or SampleConfig()
        if self.config.random_seed:
            random.seed(self.config.random_seed)
            np.random.seed(self.config.random_seed)
    
    def generate_constitutional_interaction(self, interaction_id: int, 
                                          session_progress: float) -> Dict[str, Any]:
        """
        Generate a single constitutional AI interaction.
        
        Args:
            interaction_id: Unique interaction identifier
            session_progress: Progress through session (0.0 to 1.0)
            
        Returns:
            Dictionary representing the interaction
        """
        # Base scores with constitutional bias
        base_clarity = 0.7 + self.config.constitutional_bias
        base_integrity = 0.75 + self.config.constitutional_bias
        base_quality = 0.72 + self.config.constitutional_bias
        
        # Add learning improvement
        learning_boost = session_progress * self.config.learning_rate
        
        # Add some noise
        noise = np.random.normal(0, self.config.noise_level, 3)
        
        # Calculate final scores (clamped to [0, 1])
        clarity = np.clip(base_clarity + learning_boost + noise[0], 0, 1)
        integrity = np.clip(base_integrity + learning_boost + noise[1], 0, 1)
        quality = np.clip(base_quality + learning_boost + noise[2], 0, 1)
        
        # Generate realistic interaction data
        interaction = {
            'interaction_id': f'const_{interaction_id:04d}',
            'timestamp': datetime.now() - timedelta(
                minutes=random.randint(1, 1440)  # Random time in last day
            ),
            'session_id': f'session_{random.randint(1, self.config.n_sessions):03d}',
            'mode': 'constitutional',
            'prompt_type': random.choice([
                'ethical_reasoning', 'complex_analysis', 'creative_task',
                'factual_query', 'problem_solving', 'explanation_request'
            ]),
            'input_tokens': random.randint(50, 500),
            'output_tokens': random.randint(100, 800),
            'processing_time_ms': random.randint(800, 3000),
            'ciq_metrics': {
                'clarity': float(clarity),
                'integrity': float(integrity),
                'quality': float(quality),
                'breadth': float(np.clip(np.random.normal(0.75, 0.1), 0, 1)),
                'safety': float(np.clip(np.random.normal(0.9, 0.05), 0, 1)),
                'completion': float(np.clip(np.random.normal(0.85, 0.1), 0, 1))
            },
            'constitutional_elements': {
                'principles_invoked': random.randint(2, 5),
                'ethical_considerations': random.choice([True, False]),
                'harm_mitigation': random.choice([True, False]),
                'transparency_level': random.uniform(0.7, 1.0)
            },
            'user_satisfaction': random.uniform(0.7, 1.0),
            'flags': self._generate_flags('constitutional')
        }
        
        return interaction
    
    def generate_directive_interaction(self, interaction_id: int, 
                                     session_progress: float) -> Dict[str, Any]:
        """
        Generate a single directive AI interaction.
        
        Args:
            interaction_id: Unique interaction identifier
            session_progress: Progress through session (0.0 to 1.0)
            
        Returns:
            Dictionary representing the interaction
        """
        # Base scores without constitutional bias
        base_clarity = 0.65
        base_integrity = 0.68
        base_quality = 0.70
        
        # Less consistent learning (more variable)
        learning_boost = session_progress * self.config.learning_rate * 0.7
        
        # More noise (less consistent)
        noise = np.random.normal(0, self.config.noise_level * 1.3, 3)
        
        # Calculate final scores
        clarity = np.clip(base_clarity + learning_boost + noise[0], 0, 1)
        integrity = np.clip(base_integrity + learning_boost + noise[1], 0, 1)
        quality = np.clip(base_quality + learning_boost + noise[2], 0, 1)
        
        # Generate realistic interaction data
        interaction = {
            'interaction_id': f'dir_{interaction_id:04d}',
            'timestamp': datetime.now() - timedelta(
                minutes=random.randint(1, 1440)
            ),
            'session_id': f'session_{random.randint(1, self.config.n_sessions):03d}',
            'mode': 'directive',
            'prompt_type': random.choice([
                'direct_instruction', 'factual_query', 'simple_task',
                'information_request', 'basic_analysis', 'straightforward_question'
            ]),
            'input_tokens': random.randint(30, 300),
            'output_tokens': random.randint(80, 600),
            'processing_time_ms': random.randint(500, 2000),
            'ciq_metrics': {
                'clarity': float(clarity),
                'integrity': float(integrity),
                'quality': float(quality),
                'breadth': float(np.clip(np.random.normal(0.65, 0.15), 0, 1)),
                'safety': float(np.clip(np.random.normal(0.8, 0.1), 0, 1)),
                'completion': float(np.clip(np.random.normal(0.75, 0.15), 0, 1))
            },
            'directive_elements': {
                'instruction_clarity': random.uniform(0.6, 0.9),
                'task_completion': random.choice([True, False]),
                'efficiency_score': random.uniform(0.7, 0.95)
            },
            'user_satisfaction': random.uniform(0.6, 0.9),
            'flags': self._generate_flags('directive')
        }
        
        return interaction
    
    def generate_trust_receipt(self, interaction: Dict[str, Any], 
                             previous_hash: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a trust receipt for an interaction.
        
        Args:
            interaction: Interaction data
            previous_hash: Hash of previous receipt in chain
            
        Returns:
            Trust receipt dictionary
        """
        receipt_data = {
            'version': '1.0',
            'session_id': interaction['session_id'],
            'interaction_id': interaction['interaction_id'],
            'mode': interaction['mode'],
            'timestamp': interaction['timestamp'].isoformat(),
            'inputs': {
                'prompt_type': interaction['prompt_type'],
                'input_tokens': interaction['input_tokens'],
                'processing_time_ms': interaction['processing_time_ms']
            },
            'constraints': {
                'max_tokens': 1000,
                'temperature': 0.7,
                'safety_level': 'high'
            },
            'outcome': {
                'output_tokens': interaction['output_tokens'],
                'completion_status': 'success',
                'user_satisfaction': interaction['user_satisfaction']
            },
            'flags': interaction['flags'],
            'ciq_metrics': interaction['ciq_metrics'],
            'previous_hash': previous_hash or '0' * 64,
            'metadata': {
                'generator': 'symbi_sample_data',
                'version': '1.0.0',
                'created_at': datetime.now().isoformat()
            }
        }
        
        # Calculate hash
        receipt_json = json.dumps(receipt_data, sort_keys=True, default=str)
        receipt_hash = hashlib.sha256(receipt_json.encode()).hexdigest()
        receipt_data['self_hash'] = receipt_hash
        
        # Generate signature (mock)
        signature_data = f"{receipt_hash}:symbi_key"
        receipt_data['signature'] = hashlib.sha256(signature_data.encode()).hexdigest()
        
        return receipt_data
    
    def _generate_flags(self, mode: str) -> List[str]:
        """Generate realistic flags for an interaction."""
        all_flags = [
            'high_quality', 'ethical_review', 'safety_check', 'user_feedback',
            'performance_optimized', 'context_aware', 'principle_based'
        ]
        
        if mode == 'constitutional':
            # Constitutional AI more likely to have certain flags
            flag_probabilities = [0.8, 0.9, 0.95, 0.7, 0.6, 0.8, 0.95]
        else:
            # Directive AI different flag probabilities
            flag_probabilities = [0.6, 0.3, 0.8, 0.5, 0.8, 0.6, 0.2]
        
        flags = []
        for flag, prob in zip(all_flags, flag_probabilities):
            if random.random() < prob:
                flags.append(flag)
        
        return flags


def generate_sample_constitutional_data(n_interactions: int = 50, 
                                      config: Optional[SampleConfig] = None) -> List[Dict[str, Any]]:
    """
    Generate sample constitutional AI interaction data.
    
    Args:
        n_interactions: Number of interactions to generate
        config: Configuration for data generation
        
    Returns:
        List of constitutional AI interactions
    """
    generator = SampleDataGenerator(config)
    interactions = []
    
    for i in range(n_interactions):
        session_progress = (i % 10) / 10.0  # Progress within session
        interaction = generator.generate_constitutional_interaction(i, session_progress)
        interactions.append(interaction)
    
    # Sort by timestamp
    interactions.sort(key=lambda x: x['timestamp'])
    
    return interactions


def generate_sample_directive_data(n_interactions: int = 50, 
                                 config: Optional[SampleConfig] = None) -> List[Dict[str, Any]]:
    """
    Generate sample directive AI interaction data.
    
    Args:
        n_interactions: Number of interactions to generate
        config: Configuration for data generation
        
    Returns:
        List of directive AI interactions
    """
    generator = SampleDataGenerator(config)
    interactions = []
    
    for i in range(n_interactions):
        session_progress = (i % 10) / 10.0
        interaction = generator.generate_directive_interaction(i, session_progress)
        interactions.append(interaction)
    
    # Sort by timestamp
    interactions.sort(key=lambda x: x['timestamp'])
    
    return interactions


def generate_sample_receipts(interactions: List[Dict[str, Any]], 
                           config: Optional[SampleConfig] = None) -> List[Dict[str, Any]]:
    """
    Generate trust receipts for a list of interactions.
    
    Args:
        interactions: List of interaction data
        config: Configuration for data generation
        
    Returns:
        List of trust receipts
    """
    generator = SampleDataGenerator(config)
    receipts = []
    previous_hash = None
    
    for interaction in interactions:
        receipt = generator.generate_trust_receipt(interaction, previous_hash)
        receipts.append(receipt)
        previous_hash = receipt['self_hash']
    
    return receipts


def generate_comparative_dataset(n_interactions_per_group: int = 50,
                               config: Optional[SampleConfig] = None) -> Dict[str, Any]:
    """
    Generate a complete comparative dataset for A/B testing.
    
    Args:
        n_interactions_per_group: Number of interactions per experimental group
        config: Configuration for data generation
        
    Returns:
        Dictionary containing both constitutional and directive data
    """
    # Ensure same random seed for fair comparison
    if config is None:
        config = SampleConfig(random_seed=42)
    
    # Generate constitutional data
    constitutional_data = generate_sample_constitutional_data(n_interactions_per_group, config)
    
    # Generate directive data with same seed for consistency
    directive_data = generate_sample_directive_data(n_interactions_per_group, config)
    
    # Generate receipts
    constitutional_receipts = generate_sample_receipts(constitutional_data, config)
    directive_receipts = generate_sample_receipts(directive_data, config)
    
    return {
        'constitutional': {
            'interactions': constitutional_data,
            'receipts': constitutional_receipts,
            'metadata': {
                'group': 'constitutional',
                'n_interactions': len(constitutional_data),
                'generation_config': asdict(config),
                'generated_at': datetime.now().isoformat()
            }
        },
        'directive': {
            'interactions': directive_data,
            'receipts': directive_receipts,
            'metadata': {
                'group': 'directive',
                'n_interactions': len(directive_data),
                'generation_config': asdict(config),
                'generated_at': datetime.now().isoformat()
            }
        },
        'experiment_metadata': {
            'total_interactions': n_interactions_per_group * 2,
            'groups': ['constitutional', 'directive'],
            'config': asdict(config),
            'generated_at': datetime.now().isoformat(),
            'description': 'Sample dataset for SYMBI constitutional AI research'
        }
    }


def load_sample_dataset(dataset_type: str = 'comparative', 
                       size: str = 'medium') -> Dict[str, Any]:
    """
    Load a pre-configured sample dataset.
    
    Args:
        dataset_type: Type of dataset ('comparative', 'constitutional_only', 'directive_only')
        size: Size of dataset ('small', 'medium', 'large')
        
    Returns:
        Sample dataset
    """
    size_configs = {
        'small': SampleConfig(n_interactions=25, n_sessions=5),
        'medium': SampleConfig(n_interactions=50, n_sessions=10),
        'large': SampleConfig(n_interactions=100, n_sessions=20)
    }
    
    config = size_configs.get(size, size_configs['medium'])
    
    if dataset_type == 'comparative':
        return generate_comparative_dataset(config.n_interactions, config)
    elif dataset_type == 'constitutional_only':
        interactions = generate_sample_constitutional_data(config.n_interactions, config)
        receipts = generate_sample_receipts(interactions, config)
        return {
            'constitutional': {
                'interactions': interactions,
                'receipts': receipts,
                'metadata': {
                    'group': 'constitutional',
                    'n_interactions': len(interactions),
                    'generated_at': datetime.now().isoformat()
                }
            }
        }
    elif dataset_type == 'directive_only':
        interactions = generate_sample_directive_data(config.n_interactions, config)
        receipts = generate_sample_receipts(interactions, config)
        return {
            'directive': {
                'interactions': interactions,
                'receipts': receipts,
                'metadata': {
                    'group': 'directive',
                    'n_interactions': len(interactions),
                    'generated_at': datetime.now().isoformat()
                }
            }
        }
    else:
        raise ValueError(f"Unknown dataset_type: {dataset_type}")


def save_sample_dataset(dataset: Dict[str, Any], filepath: str) -> None:
    """
    Save a sample dataset to a JSON file.
    
    Args:
        dataset: Dataset to save
        filepath: Path to save the dataset
    """
    with open(filepath, 'w') as f:
        json.dump(dataset, f, indent=2, default=str)


def load_dataset_from_file(filepath: str) -> Dict[str, Any]:
    """
    Load a dataset from a JSON file.
    
    Args:
        filepath: Path to the dataset file
        
    Returns:
        Loaded dataset
    """
    with open(filepath, 'r') as f:
        return json.load(f)


# Utility functions for quick access
def quick_constitutional_sample(n: int = 20) -> List[Dict[str, Any]]:
    """Quick function to generate constitutional AI sample data."""
    return generate_sample_constitutional_data(n)

def quick_directive_sample(n: int = 20) -> List[Dict[str, Any]]:
    """Quick function to generate directive AI sample data."""
    return generate_sample_directive_data(n)

def quick_comparative_sample(n: int = 20) -> Dict[str, Any]:
    """Quick function to generate comparative sample data."""
    return generate_comparative_dataset(n)


# Example usage and testing
if __name__ == "__main__":
    # Generate a small comparative dataset
    dataset = load_sample_dataset('comparative', 'small')
    
    print("Sample Dataset Generated:")
    print(f"Constitutional interactions: {len(dataset['constitutional']['interactions'])}")
    print(f"Directive interactions: {len(dataset['directive']['interactions'])}")
    print(f"Constitutional receipts: {len(dataset['constitutional']['receipts'])}")
    print(f"Directive receipts: {len(dataset['directive']['receipts'])}")
    
    # Show sample interaction
    sample_interaction = dataset['constitutional']['interactions'][0]
    print(f"\nSample Constitutional Interaction:")
    print(f"CIQ Metrics: {sample_interaction['ciq_metrics']}")
    print(f"Flags: {sample_interaction['flags']}")
    
    # Show sample receipt
    sample_receipt = dataset['constitutional']['receipts'][0]
    print(f"\nSample Trust Receipt:")
    print(f"Session ID: {sample_receipt['session_id']}")
    print(f"CIQ Metrics: {sample_receipt['ciq_metrics']}")
    print(f"Hash: {sample_receipt['self_hash'][:16]}...")