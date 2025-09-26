"""
Trust Receipts: Cryptographic verification and integrity tracking

This module provides tools for creating, validating, and analyzing
SYMBI trust receipts that ensure interaction integrity.
"""

import json
import hashlib
import hmac
import time
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
import base64
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend


class ReceiptMode(Enum):
    """Modes of SYMBI operation."""
    CONSTITUTIONAL = "constitutional"
    DIRECTIVE = "directive"
    HYBRID = "hybrid"


class ReceiptFlag(Enum):
    """Flags for receipt validation and analysis."""
    VALIDATED = "validated"
    ANOMALY_DETECTED = "anomaly_detected"
    CHAIN_BROKEN = "chain_broken"
    SIGNATURE_INVALID = "signature_invalid"
    SCHEMA_VIOLATION = "schema_violation"


@dataclass
class CIQMetrics:
    """CIQ metrics embedded in trust receipts."""
    clarity: float
    integrity: float
    quality: float
    breadth: float
    safety: float
    completion: float
    
    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, float]) -> 'CIQMetrics':
        """Create from dictionary."""
        return cls(**data)


@dataclass
class TrustReceipt:
    """
    A SYMBI Trust Receipt representing a verified interaction.
    
    This cryptographically signed record ensures the integrity
    and traceability of constitutional AI interactions.
    """
    version: str
    session_id: str
    mode: ReceiptMode
    inputs: Dict[str, Any]
    constraints: Dict[str, Any]
    outcome: Dict[str, Any]
    flags: List[ReceiptFlag]
    ciq_metrics: CIQMetrics
    previous_hash: Optional[str]
    self_hash: str
    signature: str
    timestamp: str
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert receipt to dictionary format."""
        return {
            'version': self.version,
            'session_id': self.session_id,
            'mode': self.mode.value,
            'inputs': self.inputs,
            'constraints': self.constraints,
            'outcome': self.outcome,
            'flags': [flag.value for flag in self.flags],
            'ciq_metrics': self.ciq_metrics.to_dict(),
            'previous_hash': self.previous_hash,
            'self_hash': self.self_hash,
            'signature': self.signature,
            'timestamp': self.timestamp,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TrustReceipt':
        """Create receipt from dictionary."""
        return cls(
            version=data['version'],
            session_id=data['session_id'],
            mode=ReceiptMode(data['mode']),
            inputs=data['inputs'],
            constraints=data['constraints'],
            outcome=data['outcome'],
            flags=[ReceiptFlag(flag) for flag in data['flags']],
            ciq_metrics=CIQMetrics.from_dict(data['ciq_metrics']),
            previous_hash=data.get('previous_hash'),
            self_hash=data['self_hash'],
            signature=data['signature'],
            timestamp=data['timestamp'],
            metadata=data['metadata']
        )
    
    def to_json(self) -> str:
        """Convert receipt to JSON string."""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'TrustReceipt':
        """Create receipt from JSON string."""
        return cls.from_dict(json.loads(json_str))


class ReceiptGenerator:
    """Generates cryptographically signed trust receipts."""
    
    def __init__(self, private_key: Optional[bytes] = None):
        """
        Initialize receipt generator.
        
        Args:
            private_key: RSA private key for signing. If None, generates new key.
        """
        if private_key:
            self.private_key = serialization.load_pem_private_key(
                private_key, password=None, backend=default_backend()
            )
        else:
            self.private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
                backend=default_backend()
            )
        
        self.public_key = self.private_key.public_key()
    
    def get_public_key_pem(self) -> bytes:
        """Get public key in PEM format."""
        return self.public_key.serialize(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
    
    def get_private_key_pem(self) -> bytes:
        """Get private key in PEM format."""
        return self.private_key.serialize(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
    
    def generate_receipt(self, 
                        session_id: str,
                        mode: ReceiptMode,
                        inputs: Dict[str, Any],
                        constraints: Dict[str, Any],
                        outcome: Dict[str, Any],
                        ciq_metrics: CIQMetrics,
                        previous_hash: Optional[str] = None,
                        metadata: Optional[Dict[str, Any]] = None) -> TrustReceipt:
        """
        Generate a new trust receipt.
        
        Args:
            session_id: Unique session identifier
            mode: SYMBI operation mode
            inputs: Input data and prompts
            constraints: Constitutional constraints applied
            outcome: Interaction outcome and response
            ciq_metrics: Calculated CIQ metrics
            previous_hash: Hash of previous receipt in chain
            metadata: Additional metadata
            
        Returns:
            Signed TrustReceipt
        """
        if metadata is None:
            metadata = {}
        
        # Create timestamp
        timestamp = datetime.now(timezone.utc).isoformat()
        
        # Create receipt data for hashing (without signature)
        receipt_data = {
            'version': '1.0',
            'session_id': session_id,
            'mode': mode.value,
            'inputs': inputs,
            'constraints': constraints,
            'outcome': outcome,
            'ciq_metrics': ciq_metrics.to_dict(),
            'previous_hash': previous_hash,
            'timestamp': timestamp,
            'metadata': metadata
        }
        
        # Calculate hash
        receipt_hash = self._calculate_hash(receipt_data)
        
        # Sign the hash
        signature = self._sign_data(receipt_hash)
        
        # Create final receipt
        receipt = TrustReceipt(
            version='1.0',
            session_id=session_id,
            mode=mode,
            inputs=inputs,
            constraints=constraints,
            outcome=outcome,
            flags=[],  # Will be populated during validation
            ciq_metrics=ciq_metrics,
            previous_hash=previous_hash,
            self_hash=receipt_hash,
            signature=signature,
            timestamp=timestamp,
            metadata=metadata
        )
        
        return receipt
    
    def _calculate_hash(self, data: Dict[str, Any]) -> str:
        """Calculate SHA-256 hash of receipt data."""
        # Create canonical JSON representation
        canonical_json = json.dumps(data, sort_keys=True, separators=(',', ':'))
        
        # Calculate hash
        hash_obj = hashlib.sha256(canonical_json.encode('utf-8'))
        return hash_obj.hexdigest()
    
    def _sign_data(self, data: str) -> str:
        """Sign data with private key."""
        signature = self.private_key.sign(
            data.encode('utf-8'),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return base64.b64encode(signature).decode('utf-8')


class ReceiptValidator:
    """Validates trust receipts and receipt chains."""
    
    def __init__(self, public_key: bytes):
        """
        Initialize validator with public key.
        
        Args:
            public_key: RSA public key in PEM format
        """
        self.public_key = serialization.load_pem_public_key(
            public_key, backend=default_backend()
        )
    
    def validate_receipt(self, receipt: TrustReceipt) -> Tuple[bool, List[str]]:
        """
        Validate a single trust receipt.
        
        Args:
            receipt: Receipt to validate
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Validate signature
        if not self._verify_signature(receipt):
            errors.append("Invalid signature")
        
        # Validate hash
        if not self._verify_hash(receipt):
            errors.append("Invalid hash")
        
        # Validate schema
        schema_errors = self._validate_schema(receipt)
        errors.extend(schema_errors)
        
        # Validate CIQ metrics
        ciq_errors = self._validate_ciq_metrics(receipt.ciq_metrics)
        errors.extend(ciq_errors)
        
        return len(errors) == 0, errors
    
    def validate_chain(self, receipts: List[TrustReceipt]) -> Tuple[bool, List[str]]:
        """
        Validate a chain of trust receipts.
        
        Args:
            receipts: List of receipts in chronological order
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        if not receipts:
            return True, []
        
        # Validate each receipt individually
        for i, receipt in enumerate(receipts):
            is_valid, receipt_errors = self.validate_receipt(receipt)
            if not is_valid:
                errors.extend([f"Receipt {i}: {error}" for error in receipt_errors])
        
        # Validate chain integrity
        for i in range(1, len(receipts)):
            current = receipts[i]
            previous = receipts[i-1]
            
            if current.previous_hash != previous.self_hash:
                errors.append(f"Chain break between receipts {i-1} and {i}")
            
            if current.session_id != previous.session_id:
                errors.append(f"Session ID mismatch between receipts {i-1} and {i}")
        
        return len(errors) == 0, errors
    
    def _verify_signature(self, receipt: TrustReceipt) -> bool:
        """Verify receipt signature."""
        try:
            signature_bytes = base64.b64decode(receipt.signature)
            self.public_key.verify(
                signature_bytes,
                receipt.self_hash.encode('utf-8'),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except Exception:
            return False
    
    def _verify_hash(self, receipt: TrustReceipt) -> bool:
        """Verify receipt hash."""
        # Reconstruct data for hashing
        receipt_data = {
            'version': receipt.version,
            'session_id': receipt.session_id,
            'mode': receipt.mode.value,
            'inputs': receipt.inputs,
            'constraints': receipt.constraints,
            'outcome': receipt.outcome,
            'ciq_metrics': receipt.ciq_metrics.to_dict(),
            'previous_hash': receipt.previous_hash,
            'timestamp': receipt.timestamp,
            'metadata': receipt.metadata
        }
        
        # Calculate expected hash
        canonical_json = json.dumps(receipt_data, sort_keys=True, separators=(',', ':'))
        expected_hash = hashlib.sha256(canonical_json.encode('utf-8')).hexdigest()
        
        return expected_hash == receipt.self_hash
    
    def _validate_schema(self, receipt: TrustReceipt) -> List[str]:
        """Validate receipt schema."""
        errors = []
        
        # Check required fields
        if not receipt.version:
            errors.append("Missing version")
        
        if not receipt.session_id:
            errors.append("Missing session_id")
        
        if not receipt.self_hash:
            errors.append("Missing self_hash")
        
        if not receipt.signature:
            errors.append("Missing signature")
        
        if not receipt.timestamp:
            errors.append("Missing timestamp")
        
        # Validate timestamp format
        try:
            datetime.fromisoformat(receipt.timestamp.replace('Z', '+00:00'))
        except ValueError:
            errors.append("Invalid timestamp format")
        
        return errors
    
    def _validate_ciq_metrics(self, metrics: CIQMetrics) -> List[str]:
        """Validate CIQ metrics."""
        errors = []
        
        # Check that all metrics are in valid range [0, 1]
        for field_name, value in asdict(metrics).items():
            if not isinstance(value, (int, float)):
                errors.append(f"CIQ metric {field_name} must be numeric")
            elif not (0 <= value <= 1):
                errors.append(f"CIQ metric {field_name} must be between 0 and 1")
        
        return errors


class ReceiptChain:
    """Manages a chain of trust receipts for a session."""
    
    def __init__(self, session_id: str, generator: ReceiptGenerator):
        """
        Initialize receipt chain.
        
        Args:
            session_id: Unique session identifier
            generator: Receipt generator for creating new receipts
        """
        self.session_id = session_id
        self.generator = generator
        self.receipts: List[TrustReceipt] = []
    
    def add_interaction(self,
                       mode: ReceiptMode,
                       inputs: Dict[str, Any],
                       constraints: Dict[str, Any],
                       outcome: Dict[str, Any],
                       ciq_metrics: CIQMetrics,
                       metadata: Optional[Dict[str, Any]] = None) -> TrustReceipt:
        """
        Add a new interaction to the chain.
        
        Args:
            mode: SYMBI operation mode
            inputs: Input data and prompts
            constraints: Constitutional constraints
            outcome: Interaction outcome
            ciq_metrics: CIQ metrics
            metadata: Additional metadata
            
        Returns:
            Generated TrustReceipt
        """
        previous_hash = None
        if self.receipts:
            previous_hash = self.receipts[-1].self_hash
        
        receipt = self.generator.generate_receipt(
            session_id=self.session_id,
            mode=mode,
            inputs=inputs,
            constraints=constraints,
            outcome=outcome,
            ciq_metrics=ciq_metrics,
            previous_hash=previous_hash,
            metadata=metadata
        )
        
        self.receipts.append(receipt)
        return receipt
    
    def get_chain_summary(self) -> Dict[str, Any]:
        """Get summary of the receipt chain."""
        if not self.receipts:
            return {
                'session_id': self.session_id,
                'length': 0,
                'avg_ciq': None,
                'modes_used': [],
                'first_timestamp': None,
                'last_timestamp': None
            }
        
        # Calculate average CIQ metrics
        total_clarity = sum(r.ciq_metrics.clarity for r in self.receipts)
        total_integrity = sum(r.ciq_metrics.integrity for r in self.receipts)
        total_quality = sum(r.ciq_metrics.quality for r in self.receipts)
        
        avg_ciq = {
            'clarity': total_clarity / len(self.receipts),
            'integrity': total_integrity / len(self.receipts),
            'quality': total_quality / len(self.receipts)
        }
        
        # Get unique modes
        modes_used = list(set(r.mode.value for r in self.receipts))
        
        return {
            'session_id': self.session_id,
            'length': len(self.receipts),
            'avg_ciq': avg_ciq,
            'modes_used': modes_used,
            'first_timestamp': self.receipts[0].timestamp,
            'last_timestamp': self.receipts[-1].timestamp
        }
    
    def export_chain(self) -> List[Dict[str, Any]]:
        """Export chain as list of dictionaries."""
        return [receipt.to_dict() for receipt in self.receipts]
    
    def import_chain(self, chain_data: List[Dict[str, Any]]) -> None:
        """Import chain from list of dictionaries."""
        self.receipts = [TrustReceipt.from_dict(data) for data in chain_data]


class ReceiptAnalyzer:
    """Analyzes trust receipts for patterns and insights."""
    
    def __init__(self):
        """Initialize analyzer."""
        pass
    
    def analyze_session(self, chain: ReceiptChain) -> Dict[str, Any]:
        """
        Analyze a complete session chain.
        
        Args:
            chain: Receipt chain to analyze
            
        Returns:
            Analysis results
        """
        if not chain.receipts:
            return {'error': 'No receipts to analyze'}
        
        receipts = chain.receipts
        
        analysis = {
            'session_summary': chain.get_chain_summary(),
            'ciq_trends': self._analyze_ciq_trends(receipts),
            'mode_analysis': self._analyze_modes(receipts),
            'interaction_patterns': self._analyze_interaction_patterns(receipts),
            'quality_insights': self._generate_quality_insights(receipts)
        }
        
        return analysis
    
    def compare_sessions(self, chains: List[ReceiptChain]) -> Dict[str, Any]:
        """
        Compare multiple session chains.
        
        Args:
            chains: List of receipt chains to compare
            
        Returns:
            Comparative analysis
        """
        if not chains:
            return {'error': 'No chains to compare'}
        
        # Aggregate metrics across all chains
        all_receipts = []
        for chain in chains:
            all_receipts.extend(chain.receipts)
        
        if not all_receipts:
            return {'error': 'No receipts in any chain'}
        
        comparison = {
            'session_count': len(chains),
            'total_interactions': len(all_receipts),
            'avg_ciq_across_sessions': self._calculate_average_ciq(all_receipts),
            'mode_distribution': self._analyze_mode_distribution(all_receipts),
            'session_comparisons': [
                {
                    'session_id': chain.session_id,
                    'summary': chain.get_chain_summary()
                }
                for chain in chains
            ],
            'best_performing_session': self._find_best_session(chains),
            'recommendations': self._generate_session_recommendations(chains)
        }
        
        return comparison
    
    def _analyze_ciq_trends(self, receipts: List[TrustReceipt]) -> Dict[str, Any]:
        """Analyze CIQ metric trends over time."""
        if len(receipts) < 2:
            return {'trend': 'insufficient_data'}
        
        clarity_scores = [r.ciq_metrics.clarity for r in receipts]
        integrity_scores = [r.ciq_metrics.integrity for r in receipts]
        quality_scores = [r.ciq_metrics.quality for r in receipts]
        
        trends = {
            'clarity_trend': self._calculate_trend(clarity_scores),
            'integrity_trend': self._calculate_trend(integrity_scores),
            'quality_trend': self._calculate_trend(quality_scores),
            'overall_improvement': self._calculate_overall_improvement(receipts)
        }
        
        return trends
    
    def _analyze_modes(self, receipts: List[TrustReceipt]) -> Dict[str, Any]:
        """Analyze mode usage patterns."""
        mode_counts = {}
        mode_ciq = {}
        
        for receipt in receipts:
            mode = receipt.mode.value
            mode_counts[mode] = mode_counts.get(mode, 0) + 1
            
            if mode not in mode_ciq:
                mode_ciq[mode] = {'clarity': [], 'integrity': [], 'quality': []}
            
            mode_ciq[mode]['clarity'].append(receipt.ciq_metrics.clarity)
            mode_ciq[mode]['integrity'].append(receipt.ciq_metrics.integrity)
            mode_ciq[mode]['quality'].append(receipt.ciq_metrics.quality)
        
        # Calculate average CIQ by mode
        mode_averages = {}
        for mode, metrics in mode_ciq.items():
            mode_averages[mode] = {
                'clarity': sum(metrics['clarity']) / len(metrics['clarity']),
                'integrity': sum(metrics['integrity']) / len(metrics['integrity']),
                'quality': sum(metrics['quality']) / len(metrics['quality'])
            }
        
        return {
            'mode_counts': mode_counts,
            'mode_averages': mode_averages,
            'most_used_mode': max(mode_counts, key=mode_counts.get),
            'best_performing_mode': self._find_best_mode(mode_averages)
        }
    
    def _analyze_interaction_patterns(self, receipts: List[TrustReceipt]) -> Dict[str, Any]:
        """Analyze interaction patterns."""
        patterns = {
            'avg_interaction_length': self._calculate_avg_interaction_length(receipts),
            'complexity_distribution': self._analyze_complexity_distribution(receipts),
            'constraint_usage': self._analyze_constraint_usage(receipts)
        }
        
        return patterns
    
    def _generate_quality_insights(self, receipts: List[TrustReceipt]) -> List[str]:
        """Generate quality insights from receipt analysis."""
        insights = []
        
        if not receipts:
            return insights
        
        # Calculate overall averages
        avg_clarity = sum(r.ciq_metrics.clarity for r in receipts) / len(receipts)
        avg_integrity = sum(r.ciq_metrics.integrity for r in receipts) / len(receipts)
        avg_quality = sum(r.ciq_metrics.quality for r in receipts) / len(receipts)
        
        # Generate insights based on scores
        if avg_clarity > 0.8:
            insights.append("Excellent communication clarity maintained throughout session")
        elif avg_clarity < 0.5:
            insights.append("Communication clarity needs improvement")
        
        if avg_integrity > 0.8:
            insights.append("Strong constitutional adherence demonstrated")
        elif avg_integrity < 0.5:
            insights.append("Constitutional integrity requires attention")
        
        if avg_quality > 0.8:
            insights.append("High-quality outcomes consistently achieved")
        elif avg_quality < 0.5:
            insights.append("Outcome quality below expectations")
        
        # Analyze trends
        if len(receipts) > 3:
            first_half = receipts[:len(receipts)//2]
            second_half = receipts[len(receipts)//2:]
            
            first_avg = sum(
                (r.ciq_metrics.clarity + r.ciq_metrics.integrity + r.ciq_metrics.quality) / 3
                for r in first_half
            ) / len(first_half)
            
            second_avg = sum(
                (r.ciq_metrics.clarity + r.ciq_metrics.integrity + r.ciq_metrics.quality) / 3
                for r in second_half
            ) / len(second_half)
            
            if second_avg > first_avg + 0.1:
                insights.append("Performance improved significantly over time")
            elif second_avg < first_avg - 0.1:
                insights.append("Performance declined over time")
        
        return insights
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction for a series of values."""
        if len(values) < 2:
            return 'stable'
        
        # Simple linear trend calculation
        x = list(range(len(values)))
        n = len(values)
        
        sum_x = sum(x)
        sum_y = sum(values)
        sum_xy = sum(x[i] * values[i] for i in range(n))
        sum_x2 = sum(x[i] ** 2 for i in range(n))
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
        
        if slope > 0.05:
            return 'improving'
        elif slope < -0.05:
            return 'declining'
        else:
            return 'stable'
    
    def _calculate_overall_improvement(self, receipts: List[TrustReceipt]) -> float:
        """Calculate overall improvement from first to last interaction."""
        if len(receipts) < 2:
            return 0.0
        
        first = receipts[0]
        last = receipts[-1]
        
        first_avg = (first.ciq_metrics.clarity + first.ciq_metrics.integrity + 
                    first.ciq_metrics.quality) / 3
        last_avg = (last.ciq_metrics.clarity + last.ciq_metrics.integrity + 
                   last.ciq_metrics.quality) / 3
        
        return last_avg - first_avg
    
    def _calculate_average_ciq(self, receipts: List[TrustReceipt]) -> Dict[str, float]:
        """Calculate average CIQ metrics across receipts."""
        if not receipts:
            return {'clarity': 0, 'integrity': 0, 'quality': 0}
        
        return {
            'clarity': sum(r.ciq_metrics.clarity for r in receipts) / len(receipts),
            'integrity': sum(r.ciq_metrics.integrity for r in receipts) / len(receipts),
            'quality': sum(r.ciq_metrics.quality for r in receipts) / len(receipts)
        }
    
    def _analyze_mode_distribution(self, receipts: List[TrustReceipt]) -> Dict[str, float]:
        """Analyze distribution of modes across all receipts."""
        mode_counts = {}
        for receipt in receipts:
            mode = receipt.mode.value
            mode_counts[mode] = mode_counts.get(mode, 0) + 1
        
        total = len(receipts)
        return {mode: count / total for mode, count in mode_counts.items()}
    
    def _find_best_session(self, chains: List[ReceiptChain]) -> Dict[str, Any]:
        """Find the best performing session."""
        best_session = None
        best_score = -1
        
        for chain in chains:
            if not chain.receipts:
                continue
            
            avg_ciq = sum(
                (r.ciq_metrics.clarity + r.ciq_metrics.integrity + r.ciq_metrics.quality) / 3
                for r in chain.receipts
            ) / len(chain.receipts)
            
            if avg_ciq > best_score:
                best_score = avg_ciq
                best_session = chain.session_id
        
        return {
            'session_id': best_session,
            'avg_ciq_score': best_score
        }
    
    def _generate_session_recommendations(self, chains: List[ReceiptChain]) -> List[str]:
        """Generate recommendations based on session analysis."""
        recommendations = []
        
        # Analyze all receipts
        all_receipts = []
        for chain in chains:
            all_receipts.extend(chain.receipts)
        
        if not all_receipts:
            return recommendations
        
        # Mode analysis
        mode_performance = {}
        for receipt in all_receipts:
            mode = receipt.mode.value
            if mode not in mode_performance:
                mode_performance[mode] = []
            
            avg_ciq = (receipt.ciq_metrics.clarity + receipt.ciq_metrics.integrity + 
                      receipt.ciq_metrics.quality) / 3
            mode_performance[mode].append(avg_ciq)
        
        # Find best performing mode
        mode_averages = {
            mode: sum(scores) / len(scores)
            for mode, scores in mode_performance.items()
        }
        
        if mode_averages:
            best_mode = max(mode_averages, key=mode_averages.get)
            recommendations.append(f"Consider using {best_mode} mode more frequently")
        
        # Overall performance recommendations
        overall_avg = sum(
            (r.ciq_metrics.clarity + r.ciq_metrics.integrity + r.ciq_metrics.quality) / 3
            for r in all_receipts
        ) / len(all_receipts)
        
        if overall_avg < 0.6:
            recommendations.append("Focus on improving constitutional adherence and clarity")
        elif overall_avg > 0.8:
            recommendations.append("Maintain current high standards of collaboration")
        
        return recommendations
    
    def _find_best_mode(self, mode_averages: Dict[str, Dict[str, float]]) -> str:
        """Find the best performing mode based on average CIQ."""
        best_mode = None
        best_score = -1
        
        for mode, metrics in mode_averages.items():
            avg_score = (metrics['clarity'] + metrics['integrity'] + metrics['quality']) / 3
            if avg_score > best_score:
                best_score = avg_score
                best_mode = mode
        
        return best_mode
    
    def _calculate_avg_interaction_length(self, receipts: List[TrustReceipt]) -> float:
        """Calculate average interaction length (simplified)."""
        if not receipts:
            return 0.0
        
        total_length = 0
        for receipt in receipts:
            # Estimate length from input and outcome text
            input_text = str(receipt.inputs.get('prompt', ''))
            outcome_text = str(receipt.outcome.get('response', ''))
            total_length += len(input_text) + len(outcome_text)
        
        return total_length / len(receipts)
    
    def _analyze_complexity_distribution(self, receipts: List[TrustReceipt]) -> Dict[str, int]:
        """Analyze complexity distribution of interactions."""
        complexity_counts = {'low': 0, 'medium': 0, 'high': 0}
        
        for receipt in receipts:
            # Simple complexity heuristic based on constraint count and text length
            constraint_count = len(receipt.constraints)
            input_length = len(str(receipt.inputs.get('prompt', '')))
            
            if constraint_count <= 2 and input_length < 200:
                complexity_counts['low'] += 1
            elif constraint_count <= 5 and input_length < 500:
                complexity_counts['medium'] += 1
            else:
                complexity_counts['high'] += 1
        
        return complexity_counts
    
    def _analyze_constraint_usage(self, receipts: List[TrustReceipt]) -> Dict[str, Any]:
        """Analyze how constraints are used across interactions."""
        all_constraints = []
        for receipt in receipts:
            all_constraints.extend(receipt.constraints.keys())
        
        # Count constraint frequency
        constraint_counts = {}
        for constraint in all_constraints:
            constraint_counts[constraint] = constraint_counts.get(constraint, 0) + 1
        
        return {
            'total_unique_constraints': len(set(all_constraints)),
            'avg_constraints_per_interaction': len(all_constraints) / len(receipts) if receipts else 0,
            'most_common_constraints': sorted(
                constraint_counts.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:5]
        }