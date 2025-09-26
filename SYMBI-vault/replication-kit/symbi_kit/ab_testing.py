"""
A/B Testing Framework for SYMBI Protocol Research

This module provides tools for conducting rigorous A/B tests comparing
SYMBI constitutional prompting against traditional directive prompting.
"""

import json
import time
import uuid
import hashlib
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import numpy as np
from .ciq_metrics import CIQCalculator
from .trust_receipts import TrustReceiptValidator


@dataclass
class TestConfiguration:
    """Configuration for A/B test execution."""
    test_name: str
    description: str
    sample_size: int
    randomization_seed: Optional[int] = None
    significance_level: float = 0.05
    power: float = 0.8
    minimum_effect_size: float = 0.2
    
    def __post_init__(self):
        if self.randomization_seed is None:
            self.randomization_seed = int(time.time())


@dataclass
class TestResult:
    """Individual test result from A/B testing."""
    participant_id: str
    condition: str  # 'symbi' or 'directive'
    prompt: str
    response: str
    timestamp: datetime
    ciq_scores: Dict[str, float]
    metadata: Dict[str, Any]
    trust_receipt: Optional[Dict] = None


class SymbiTest:
    """SYMBI constitutional prompting test condition."""
    
    def __init__(self, constitutional_framework: Dict[str, Any]):
        """
        Initialize SYMBI test with constitutional framework.
        
        Args:
            constitutional_framework: Dictionary containing constitutional principles,
                                    constraints, and interaction guidelines
        """
        self.framework = constitutional_framework
        self.ciq_calculator = CIQCalculator()
        
    def generate_prompt(self, base_task: str, context: Dict[str, Any]) -> str:
        """
        Generate SYMBI constitutional prompt from base task.
        
        Args:
            base_task: The core task or question to be addressed
            context: Additional context and constraints
            
        Returns:
            Constitutional prompt following SYMBI principles
        """
        constitutional_prefix = self._build_constitutional_prefix()
        relationship_context = self._build_relationship_context(context)
        
        prompt = f"""
{constitutional_prefix}

## Task Context
{relationship_context}

## Core Task
{base_task}

## Constitutional Constraints
{self._format_constraints()}

## Expected Collaboration
Please approach this task as a collaborative partner, ensuring:
1. Clarity in communication and reasoning
2. Integrity in process and outcomes  
3. Quality in both method and results

Provide your response with explicit reasoning for how you're addressing
the constitutional constraints while achieving the task objectives.
"""
        return prompt.strip()
    
    def _build_constitutional_prefix(self) -> str:
        """Build the constitutional framework prefix."""
        principles = self.framework.get('principles', [])
        return f"""
## Constitutional Framework
We are engaging in constitutional AI collaboration guided by these principles:
{chr(10).join(f"- {principle}" for principle in principles)}

This interaction will be recorded as a Trust Receipt for transparency and accountability.
"""
    
    def _build_relationship_context(self, context: Dict[str, Any]) -> str:
        """Build relationship and context information."""
        return f"""
Interaction Context: {context.get('scenario', 'General collaboration')}
Stakeholders: {', '.join(context.get('stakeholders', ['Human', 'AI']))}
Success Criteria: {context.get('success_criteria', 'Mutual benefit and understanding')}
"""
    
    def _format_constraints(self) -> str:
        """Format constitutional constraints for the prompt."""
        constraints = self.framework.get('constraints', [])
        return chr(10).join(f"- {constraint}" for constraint in constraints)
    
    def evaluate_response(self, prompt: str, response: str, 
                         context: Dict[str, Any]) -> TestResult:
        """
        Evaluate a response using SYMBI metrics.
        
        Args:
            prompt: The constitutional prompt used
            response: AI response to evaluate
            context: Test context and metadata
            
        Returns:
            TestResult with CIQ scores and trust receipt
        """
        # Calculate CIQ scores
        ciq_scores = self.ciq_calculator.calculate_all_metrics(
            prompt, response, context
        )
        
        # Generate trust receipt
        trust_receipt = self._generate_trust_receipt(
            prompt, response, ciq_scores, context
        )
        
        return TestResult(
            participant_id=context.get('participant_id', str(uuid.uuid4())),
            condition='symbi',
            prompt=prompt,
            response=response,
            timestamp=datetime.now(timezone.utc),
            ciq_scores=ciq_scores,
            metadata=context,
            trust_receipt=trust_receipt
        )
    
    def _generate_trust_receipt(self, prompt: str, response: str,
                              ciq_scores: Dict[str, float],
                              context: Dict[str, Any]) -> Dict:
        """Generate a trust receipt for the interaction."""
        session_id = context.get('session_id', str(uuid.uuid4()))
        
        receipt = {
            "version": "1.0",
            "session_id": session_id,
            "mode": "constitutional",
            "inputs": {
                "prompt": prompt,
                "context": context
            },
            "constraints": self.framework.get('constraints', []),
            "outcome": {
                "response": response,
                "reasoning": "Constitutional AI collaboration"
            },
            "flags": [],
            "ciq": ciq_scores,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metadata": {
                "framework_version": self.framework.get('version', '1.0'),
                "test_condition": "symbi"
            }
        }
        
        # Generate cryptographic hash
        receipt_str = json.dumps(receipt, sort_keys=True)
        receipt["self_hash"] = hashlib.sha256(receipt_str.encode()).hexdigest()
        
        return receipt


class DirectiveTest:
    """Traditional directive prompting test condition."""
    
    def __init__(self):
        """Initialize directive test condition."""
        self.ciq_calculator = CIQCalculator()
    
    def generate_prompt(self, base_task: str, context: Dict[str, Any]) -> str:
        """
        Generate traditional directive prompt from base task.
        
        Args:
            base_task: The core task or question to be addressed
            context: Additional context (minimal usage in directive approach)
            
        Returns:
            Direct, instruction-based prompt
        """
        return f"""
{base_task}

Please provide a clear, accurate, and helpful response.
"""
    
    def evaluate_response(self, prompt: str, response: str,
                         context: Dict[str, Any]) -> TestResult:
        """
        Evaluate a response using standard metrics.
        
        Args:
            prompt: The directive prompt used
            response: AI response to evaluate
            context: Test context and metadata
            
        Returns:
            TestResult with CIQ scores (baseline measurement)
        """
        # Calculate CIQ scores for comparison
        ciq_scores = self.ciq_calculator.calculate_all_metrics(
            prompt, response, context
        )
        
        return TestResult(
            participant_id=context.get('participant_id', str(uuid.uuid4())),
            condition='directive',
            prompt=prompt,
            response=response,
            timestamp=datetime.now(timezone.utc),
            ciq_scores=ciq_scores,
            metadata=context,
            trust_receipt=None  # No trust receipts for directive condition
        )


class ABTestFramework:
    """Framework for conducting SYMBI vs Directive A/B tests."""
    
    def __init__(self, config: TestConfiguration,
                 constitutional_framework: Dict[str, Any]):
        """
        Initialize A/B test framework.
        
        Args:
            config: Test configuration parameters
            constitutional_framework: SYMBI constitutional framework
        """
        self.config = config
        self.symbi_test = SymbiTest(constitutional_framework)
        self.directive_test = DirectiveTest()
        self.results: List[TestResult] = []
        
        # Set random seed for reproducibility
        np.random.seed(config.randomization_seed)
    
    def randomize_condition(self, participant_id: str) -> str:
        """
        Randomly assign participant to test condition.
        
        Args:
            participant_id: Unique identifier for participant
            
        Returns:
            'symbi' or 'directive' condition assignment
        """
        # Use participant ID for consistent assignment
        hash_obj = hashlib.md5(participant_id.encode())
        hash_int = int(hash_obj.hexdigest(), 16)
        return 'symbi' if hash_int % 2 == 0 else 'directive'
    
    def run_test(self, participant_id: str, base_task: str,
                 context: Dict[str, Any]) -> TestResult:
        """
        Run A/B test for a single participant.
        
        Args:
            participant_id: Unique identifier for participant
            base_task: The task to be completed
            context: Additional context and metadata
            
        Returns:
            TestResult from the assigned condition
        """
        condition = self.randomize_condition(participant_id)
        context['participant_id'] = participant_id
        context['test_name'] = self.config.test_name
        
        if condition == 'symbi':
            prompt = self.symbi_test.generate_prompt(base_task, context)
            # In real implementation, this would call the AI system
            response = self._simulate_ai_response(prompt, condition)
            result = self.symbi_test.evaluate_response(prompt, response, context)
        else:
            prompt = self.directive_test.generate_prompt(base_task, context)
            # In real implementation, this would call the AI system
            response = self._simulate_ai_response(prompt, condition)
            result = self.directive_test.evaluate_response(prompt, response, context)
        
        self.results.append(result)
        return result
    
    def _simulate_ai_response(self, prompt: str, condition: str) -> str:
        """
        Simulate AI response for testing purposes.
        In real implementation, this would call actual AI system.
        """
        if condition == 'symbi':
            return f"""
I'll approach this task following our constitutional framework.

**Reasoning Process:**
Based on the constitutional constraints provided, I need to ensure clarity,
integrity, and quality in my response while maintaining transparency about
my decision-making process.

**Response:**
[Simulated constitutional AI response with explicit reasoning and 
consideration of stakeholder needs]

**Constitutional Compliance:**
- Clarity: Provided explicit reasoning and structured response
- Integrity: Maintained consistency with stated principles
- Quality: Addressed task requirements comprehensively
"""
        else:
            return "[Simulated direct AI response to the task]"
    
    def get_results_summary(self) -> Dict[str, Any]:
        """
        Get summary statistics of A/B test results.
        
        Returns:
            Dictionary containing test summary and statistics
        """
        if not self.results:
            return {"error": "No test results available"}
        
        symbi_results = [r for r in self.results if r.condition == 'symbi']
        directive_results = [r for r in self.results if r.condition == 'directive']
        
        def calculate_condition_stats(results: List[TestResult]) -> Dict:
            if not results:
                return {}
            
            ciq_scores = [r.ciq_scores for r in results]
            clarity_scores = [scores.get('clarity', 0) for scores in ciq_scores]
            integrity_scores = [scores.get('integrity', 0) for scores in ciq_scores]
            quality_scores = [scores.get('quality', 0) for scores in ciq_scores]
            
            return {
                "n": len(results),
                "clarity": {
                    "mean": np.mean(clarity_scores),
                    "std": np.std(clarity_scores),
                    "median": np.median(clarity_scores)
                },
                "integrity": {
                    "mean": np.mean(integrity_scores),
                    "std": np.std(integrity_scores),
                    "median": np.median(integrity_scores)
                },
                "quality": {
                    "mean": np.mean(quality_scores),
                    "std": np.std(quality_scores),
                    "median": np.median(quality_scores)
                }
            }
        
        return {
            "test_config": asdict(self.config),
            "total_results": len(self.results),
            "symbi_condition": calculate_condition_stats(symbi_results),
            "directive_condition": calculate_condition_stats(directive_results),
            "completion_time": datetime.now(timezone.utc).isoformat()
        }
    
    def export_results(self, filepath: str) -> None:
        """
        Export test results to JSON file.
        
        Args:
            filepath: Path to save results file
        """
        export_data = {
            "test_configuration": asdict(self.config),
            "results": [asdict(result) for result in self.results],
            "summary": self.get_results_summary(),
            "export_timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, default=str)
    
    def load_results(self, filepath: str) -> None:
        """
        Load test results from JSON file.
        
        Args:
            filepath: Path to results file
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Reconstruct TestResult objects
        self.results = []
        for result_data in data.get('results', []):
            # Convert timestamp string back to datetime
            if isinstance(result_data['timestamp'], str):
                result_data['timestamp'] = datetime.fromisoformat(
                    result_data['timestamp'].replace('Z', '+00:00')
                )
            
            result = TestResult(**result_data)
            self.results.append(result)