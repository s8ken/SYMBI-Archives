"""
CIQ Metrics: Clarity, Integrity, Quality Measurement

This module provides comprehensive tools for measuring the three core
dimensions of SYMBI constitutional AI interactions.
"""

import re
import json
import math
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from abc import ABC, abstractmethod
import numpy as np
from collections import Counter


@dataclass
class MetricResult:
    """Result of a single metric calculation."""
    score: float
    components: Dict[str, float]
    explanation: str
    confidence: float


class BaseMetric(ABC):
    """Abstract base class for CIQ metrics."""
    
    @abstractmethod
    def calculate(self, prompt: str, response: str, 
                 context: Dict[str, Any]) -> MetricResult:
        """Calculate the metric score."""
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """Get the metric name."""
        pass


class ClarityMetric(BaseMetric):
    """
    Clarity Metric: Measures how well the interaction communicates
    intent, understanding, and reasoning.
    """
    
    def get_name(self) -> str:
        return "clarity"
    
    def calculate(self, prompt: str, response: str,
                 context: Dict[str, Any]) -> MetricResult:
        """
        Calculate clarity score based on multiple dimensions.
        
        Components:
        - Communication effectiveness
        - Reasoning transparency  
        - Intent alignment
        - Comprehensibility
        """
        components = {}
        
        # Communication effectiveness (0-1)
        components['communication'] = self._assess_communication_effectiveness(
            prompt, response
        )
        
        # Reasoning transparency (0-1)
        components['reasoning'] = self._assess_reasoning_transparency(response)
        
        # Intent alignment (0-1)
        components['intent_alignment'] = self._assess_intent_alignment(
            prompt, response, context
        )
        
        # Comprehensibility (0-1)
        components['comprehensibility'] = self._assess_comprehensibility(response)
        
        # Weighted average
        weights = {
            'communication': 0.3,
            'reasoning': 0.3,
            'intent_alignment': 0.25,
            'comprehensibility': 0.15
        }
        
        score = sum(components[key] * weights[key] for key in weights)
        confidence = self._calculate_confidence(components)
        
        explanation = self._generate_explanation(components, score)
        
        return MetricResult(
            score=score,
            components=components,
            explanation=explanation,
            confidence=confidence
        )
    
    def _assess_communication_effectiveness(self, prompt: str, response: str) -> float:
        """Assess how effectively the response communicates."""
        score = 0.0
        
        # Check for direct acknowledgment of the prompt
        if self._contains_acknowledgment(prompt, response):
            score += 0.3
        
        # Check for structured communication
        if self._has_clear_structure(response):
            score += 0.3
        
        # Check for appropriate detail level
        detail_score = self._assess_detail_appropriateness(prompt, response)
        score += 0.4 * detail_score
        
        return min(score, 1.0)
    
    def _assess_reasoning_transparency(self, response: str) -> float:
        """Assess how transparently the reasoning is communicated."""
        score = 0.0
        
        # Look for explicit reasoning indicators
        reasoning_indicators = [
            r'because\s+', r'therefore\s+', r'thus\s+', r'consequently\s+',
            r'reasoning:', r'rationale:', r'logic:', r'approach:',
            r'step\s+\d+', r'first[ly]?\s*,', r'second[ly]?\s*,', r'third[ly]?\s*,'
        ]
        
        indicator_count = sum(
            1 for pattern in reasoning_indicators
            if re.search(pattern, response, re.IGNORECASE)
        )
        
        score += min(indicator_count * 0.15, 0.6)
        
        # Check for causal relationships
        if self._contains_causal_reasoning(response):
            score += 0.2
        
        # Check for consideration of alternatives
        if self._considers_alternatives(response):
            score += 0.2
        
        return min(score, 1.0)
    
    def _assess_intent_alignment(self, prompt: str, response: str,
                               context: Dict[str, Any]) -> float:
        """Assess how well the response aligns with prompt intent."""
        # Extract key terms from prompt
        prompt_terms = self._extract_key_terms(prompt)
        response_terms = self._extract_key_terms(response)
        
        # Calculate term overlap
        if not prompt_terms:
            return 0.5  # Neutral if no clear terms
        
        overlap = len(set(prompt_terms) & set(response_terms))
        term_alignment = overlap / len(prompt_terms)
        
        # Check for task completion indicators
        task_completion = self._assess_task_completion(prompt, response)
        
        # Combine scores
        return 0.6 * term_alignment + 0.4 * task_completion
    
    def _assess_comprehensibility(self, response: str) -> float:
        """Assess how comprehensible the response is."""
        score = 0.0
        
        # Sentence length analysis
        sentences = re.split(r'[.!?]+', response)
        avg_sentence_length = np.mean([len(s.split()) for s in sentences if s.strip()])
        
        # Optimal range: 15-25 words per sentence
        if 15 <= avg_sentence_length <= 25:
            score += 0.3
        elif 10 <= avg_sentence_length <= 30:
            score += 0.2
        else:
            score += 0.1
        
        # Vocabulary complexity
        words = response.lower().split()
        complex_words = sum(1 for word in words if len(word) > 7)
        complexity_ratio = complex_words / len(words) if words else 0
        
        # Moderate complexity is good (10-20%)
        if 0.1 <= complexity_ratio <= 0.2:
            score += 0.3
        elif 0.05 <= complexity_ratio <= 0.3:
            score += 0.2
        else:
            score += 0.1
        
        # Readability indicators
        if self._has_good_readability(response):
            score += 0.4
        
        return min(score, 1.0)
    
    def _contains_acknowledgment(self, prompt: str, response: str) -> bool:
        """Check if response acknowledges the prompt."""
        acknowledgment_patterns = [
            r'understand', r'acknowledge', r'recognize', r'see that',
            r'you\'re asking', r'you want', r'the question', r'the task'
        ]
        return any(re.search(pattern, response, re.IGNORECASE) 
                  for pattern in acknowledgment_patterns)
    
    def _has_clear_structure(self, response: str) -> bool:
        """Check if response has clear structure."""
        structure_indicators = [
            r'^\s*\d+\.', r'^\s*[a-z]\)', r'^\s*[-*]', r':\s*$',
            r'first[ly]?', r'second[ly]?', r'finally', r'in conclusion'
        ]
        return any(re.search(pattern, response, re.MULTILINE | re.IGNORECASE)
                  for pattern in structure_indicators)
    
    def _assess_detail_appropriateness(self, prompt: str, response: str) -> float:
        """Assess if response detail level matches prompt needs."""
        prompt_length = len(prompt.split())
        response_length = len(response.split())
        
        # Rough heuristic: response should be 1-3x prompt length
        ratio = response_length / prompt_length if prompt_length > 0 else 1
        
        if 1 <= ratio <= 3:
            return 1.0
        elif 0.5 <= ratio <= 5:
            return 0.7
        else:
            return 0.3
    
    def _contains_causal_reasoning(self, response: str) -> bool:
        """Check for causal reasoning patterns."""
        causal_patterns = [
            r'leads to', r'results in', r'causes?', r'due to',
            r'as a result', r'consequently', r'therefore'
        ]
        return any(re.search(pattern, response, re.IGNORECASE)
                  for pattern in causal_patterns)
    
    def _considers_alternatives(self, response: str) -> bool:
        """Check if response considers alternatives."""
        alternative_patterns = [
            r'alternatively', r'on the other hand', r'however',
            r'another approach', r'different way', r'could also'
        ]
        return any(re.search(pattern, response, re.IGNORECASE)
                  for pattern in alternative_patterns)
    
    def _extract_key_terms(self, text: str) -> List[str]:
        """Extract key terms from text."""
        # Simple keyword extraction (could be enhanced with NLP)
        words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
        # Filter out common words
        stopwords = {'that', 'this', 'with', 'from', 'they', 'been', 'have', 
                    'were', 'said', 'each', 'which', 'their', 'time', 'will'}
        return [word for word in words if word not in stopwords]
    
    def _assess_task_completion(self, prompt: str, response: str) -> float:
        """Assess if the response completes the requested task."""
        # Look for task completion indicators
        completion_indicators = [
            r'completed?', r'finished', r'done', r'accomplished',
            r'here is', r'here are', r'the answer', r'solution'
        ]
        
        indicator_count = sum(
            1 for pattern in completion_indicators
            if re.search(pattern, response, re.IGNORECASE)
        )
        
        return min(indicator_count * 0.3, 1.0)
    
    def _has_good_readability(self, response: str) -> bool:
        """Check for good readability indicators."""
        # Simple readability checks
        sentences = re.split(r'[.!?]+', response)
        
        # Check for varied sentence lengths
        lengths = [len(s.split()) for s in sentences if s.strip()]
        if len(lengths) > 1:
            length_variance = np.var(lengths)
            return length_variance > 10  # Some variety in sentence length
        
        return True
    
    def _calculate_confidence(self, components: Dict[str, float]) -> float:
        """Calculate confidence in the clarity assessment."""
        # Higher confidence when components are consistent
        values = list(components.values())
        variance = np.var(values)
        return max(0.5, 1.0 - variance)
    
    def _generate_explanation(self, components: Dict[str, float], 
                            score: float) -> str:
        """Generate human-readable explanation of clarity score."""
        explanations = []
        
        if components['communication'] > 0.7:
            explanations.append("Strong communication effectiveness")
        elif components['communication'] < 0.4:
            explanations.append("Weak communication effectiveness")
        
        if components['reasoning'] > 0.7:
            explanations.append("Clear reasoning transparency")
        elif components['reasoning'] < 0.4:
            explanations.append("Limited reasoning transparency")
        
        if components['intent_alignment'] > 0.7:
            explanations.append("Good intent alignment")
        elif components['intent_alignment'] < 0.4:
            explanations.append("Poor intent alignment")
        
        if score > 0.8:
            overall = "Excellent clarity"
        elif score > 0.6:
            overall = "Good clarity"
        elif score > 0.4:
            overall = "Moderate clarity"
        else:
            overall = "Poor clarity"
        
        return f"{overall}. " + "; ".join(explanations)


class IntegrityMetric(BaseMetric):
    """
    Integrity Metric: Measures consistency between stated principles,
    processes, and actual outcomes.
    """
    
    def get_name(self) -> str:
        return "integrity"
    
    def calculate(self, prompt: str, response: str,
                 context: Dict[str, Any]) -> MetricResult:
        """
        Calculate integrity score based on consistency dimensions.
        
        Components:
        - Principle adherence
        - Process consistency
        - Promise fulfillment
        - Transparency maintenance
        """
        components = {}
        
        # Principle adherence (0-1)
        components['principle_adherence'] = self._assess_principle_adherence(
            prompt, response, context
        )
        
        # Process consistency (0-1)
        components['process_consistency'] = self._assess_process_consistency(
            prompt, response
        )
        
        # Promise fulfillment (0-1)
        components['promise_fulfillment'] = self._assess_promise_fulfillment(
            prompt, response
        )
        
        # Transparency maintenance (0-1)
        components['transparency'] = self._assess_transparency(response)
        
        # Weighted average
        weights = {
            'principle_adherence': 0.35,
            'process_consistency': 0.25,
            'promise_fulfillment': 0.25,
            'transparency': 0.15
        }
        
        score = sum(components[key] * weights[key] for key in weights)
        confidence = self._calculate_confidence(components)
        
        explanation = self._generate_explanation(components, score)
        
        return MetricResult(
            score=score,
            components=components,
            explanation=explanation,
            confidence=confidence
        )
    
    def _assess_principle_adherence(self, prompt: str, response: str,
                                  context: Dict[str, Any]) -> float:
        """Assess adherence to stated constitutional principles."""
        # Extract principles from context or prompt
        principles = context.get('constitutional_principles', [])
        if not principles:
            # Look for principle statements in prompt
            principles = self._extract_principles_from_prompt(prompt)
        
        if not principles:
            return 0.5  # Neutral if no principles specified
        
        adherence_score = 0.0
        for principle in principles:
            if self._response_adheres_to_principle(response, principle):
                adherence_score += 1.0 / len(principles)
        
        return adherence_score
    
    def _assess_process_consistency(self, prompt: str, response: str) -> float:
        """Assess consistency in described processes."""
        # Look for process descriptions in prompt and response
        prompt_processes = self._extract_processes(prompt)
        response_processes = self._extract_processes(response)
        
        if not prompt_processes:
            return 0.8  # High score if no specific process required
        
        consistency_score = 0.0
        for process in prompt_processes:
            if any(self._processes_consistent(process, resp_proc) 
                  for resp_proc in response_processes):
                consistency_score += 1.0 / len(prompt_processes)
        
        return consistency_score
    
    def _assess_promise_fulfillment(self, prompt: str, response: str) -> float:
        """Assess whether response fulfills promises made in prompt."""
        # Extract commitments/promises from prompt
        promises = self._extract_promises(prompt)
        
        if not promises:
            return 0.8  # High score if no specific promises
        
        fulfillment_score = 0.0
        for promise in promises:
            if self._promise_fulfilled(promise, response):
                fulfillment_score += 1.0 / len(promises)
        
        return fulfillment_score
    
    def _assess_transparency(self, response: str) -> float:
        """Assess transparency in the response."""
        score = 0.0
        
        # Check for explicit reasoning
        if self._contains_explicit_reasoning(response):
            score += 0.4
        
        # Check for acknowledgment of limitations
        if self._acknowledges_limitations(response):
            score += 0.3
        
        # Check for process disclosure
        if self._discloses_process(response):
            score += 0.3
        
        return min(score, 1.0)
    
    def _extract_principles_from_prompt(self, prompt: str) -> List[str]:
        """Extract constitutional principles from prompt text."""
        principles = []
        
        # Look for principle sections
        principle_patterns = [
            r'principle[s]?:\s*(.+?)(?:\n\n|\n[A-Z]|$)',
            r'constitutional\s+(?:principle|framework)[s]?:\s*(.+?)(?:\n\n|\n[A-Z]|$)',
            r'guided by[:\s]+(.+?)(?:\n\n|\n[A-Z]|$)'
        ]
        
        for pattern in principle_patterns:
            matches = re.findall(pattern, prompt, re.IGNORECASE | re.DOTALL)
            for match in matches:
                # Split on bullet points or line breaks
                items = re.split(r'[-*•]\s*|\n\s*\d+\.\s*', match)
                principles.extend([item.strip() for item in items if item.strip()])
        
        return principles
    
    def _response_adheres_to_principle(self, response: str, principle: str) -> bool:
        """Check if response adheres to a specific principle."""
        # Extract key concepts from principle
        principle_words = set(re.findall(r'\b\w+\b', principle.lower()))
        response_words = set(re.findall(r'\b\w+\b', response.lower()))
        
        # Check for concept overlap
        overlap = len(principle_words & response_words)
        return overlap >= len(principle_words) * 0.3
    
    def _extract_processes(self, text: str) -> List[str]:
        """Extract process descriptions from text."""
        processes = []
        
        # Look for step-by-step processes
        step_patterns = [
            r'step\s+\d+[:\s]+(.+?)(?:\n|$)',
            r'\d+\.\s+(.+?)(?:\n|$)',
            r'first[ly]?[:\s]+(.+?)(?:\n|second|$)',
            r'process[:\s]+(.+?)(?:\n\n|\n[A-Z]|$)'
        ]
        
        for pattern in step_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
            processes.extend([match.strip() for match in matches])
        
        return processes
    
    def _processes_consistent(self, process1: str, process2: str) -> bool:
        """Check if two process descriptions are consistent."""
        # Simple word overlap check
        words1 = set(re.findall(r'\b\w+\b', process1.lower()))
        words2 = set(re.findall(r'\b\w+\b', process2.lower()))
        
        overlap = len(words1 & words2)
        union = len(words1 | words2)
        
        return overlap / union > 0.3 if union > 0 else False
    
    def _extract_promises(self, prompt: str) -> List[str]:
        """Extract promises or commitments from prompt."""
        promises = []
        
        # Look for commitment language
        promise_patterns = [
            r'will\s+(.+?)(?:\.|,|\n|$)',
            r'ensure[s]?\s+(.+?)(?:\.|,|\n|$)',
            r'guarantee[s]?\s+(.+?)(?:\.|,|\n|$)',
            r'commit[s]?\s+to\s+(.+?)(?:\.|,|\n|$)'
        ]
        
        for pattern in promise_patterns:
            matches = re.findall(pattern, prompt, re.IGNORECASE)
            promises.extend([match.strip() for match in matches])
        
        return promises
    
    def _promise_fulfilled(self, promise: str, response: str) -> bool:
        """Check if a promise is fulfilled in the response."""
        # Extract key action words from promise
        promise_words = set(re.findall(r'\b\w+\b', promise.lower()))
        response_words = set(re.findall(r'\b\w+\b', response.lower()))
        
        # Check for significant overlap
        overlap = len(promise_words & response_words)
        return overlap >= len(promise_words) * 0.4
    
    def _contains_explicit_reasoning(self, response: str) -> bool:
        """Check if response contains explicit reasoning."""
        reasoning_indicators = [
            r'because', r'therefore', r'thus', r'reasoning',
            r'rationale', r'logic', r'approach', r'method'
        ]
        return any(re.search(pattern, response, re.IGNORECASE)
                  for pattern in reasoning_indicators)
    
    def _acknowledges_limitations(self, response: str) -> bool:
        """Check if response acknowledges limitations."""
        limitation_indicators = [
            r'limitation', r'constraint', r'cannot', r'unable',
            r'uncertain', r'unclear', r'may not', r'might not'
        ]
        return any(re.search(pattern, response, re.IGNORECASE)
                  for pattern in limitation_indicators)
    
    def _discloses_process(self, response: str) -> bool:
        """Check if response discloses its process."""
        process_indicators = [
            r'approach', r'method', r'process', r'step',
            r'first', r'then', r'next', r'finally'
        ]
        return any(re.search(pattern, response, re.IGNORECASE)
                  for pattern in process_indicators)
    
    def _calculate_confidence(self, components: Dict[str, float]) -> float:
        """Calculate confidence in integrity assessment."""
        values = list(components.values())
        # Higher confidence when all components are either high or low
        variance = np.var(values)
        return max(0.6, 1.0 - variance * 2)
    
    def _generate_explanation(self, components: Dict[str, float],
                            score: float) -> str:
        """Generate explanation of integrity score."""
        explanations = []
        
        if components['principle_adherence'] > 0.7:
            explanations.append("Strong principle adherence")
        elif components['principle_adherence'] < 0.4:
            explanations.append("Weak principle adherence")
        
        if components['process_consistency'] > 0.7:
            explanations.append("Consistent processes")
        elif components['process_consistency'] < 0.4:
            explanations.append("Inconsistent processes")
        
        if components['transparency'] > 0.7:
            explanations.append("High transparency")
        elif components['transparency'] < 0.4:
            explanations.append("Low transparency")
        
        if score > 0.8:
            overall = "High integrity"
        elif score > 0.6:
            overall = "Good integrity"
        elif score > 0.4:
            overall = "Moderate integrity"
        else:
            overall = "Low integrity"
        
        return f"{overall}. " + "; ".join(explanations)


class QualityMetric(BaseMetric):
    """
    Quality Metric: Measures overall effectiveness, accuracy,
    and value of the interaction outcome.
    """
    
    def get_name(self) -> str:
        return "quality"
    
    def calculate(self, prompt: str, response: str,
                 context: Dict[str, Any]) -> MetricResult:
        """
        Calculate quality score based on effectiveness dimensions.
        
        Components:
        - Task completion
        - Accuracy assessment
        - Value generation
        - User satisfaction proxy
        """
        components = {}
        
        # Task completion (0-1)
        components['task_completion'] = self._assess_task_completion(
            prompt, response
        )
        
        # Accuracy assessment (0-1)
        components['accuracy'] = self._assess_accuracy(
            prompt, response, context
        )
        
        # Value generation (0-1)
        components['value_generation'] = self._assess_value_generation(
            prompt, response
        )
        
        # User satisfaction proxy (0-1)
        components['satisfaction_proxy'] = self._assess_satisfaction_proxy(
            response
        )
        
        # Weighted average
        weights = {
            'task_completion': 0.35,
            'accuracy': 0.3,
            'value_generation': 0.2,
            'satisfaction_proxy': 0.15
        }
        
        score = sum(components[key] * weights[key] for key in weights)
        confidence = self._calculate_confidence(components, context)
        
        explanation = self._generate_explanation(components, score)
        
        return MetricResult(
            score=score,
            components=components,
            explanation=explanation,
            confidence=confidence
        )
    
    def _assess_task_completion(self, prompt: str, response: str) -> float:
        """Assess how completely the task was accomplished."""
        # Extract task indicators from prompt
        task_indicators = self._extract_task_indicators(prompt)
        
        completion_score = 0.0
        
        # Check for direct task completion
        if self._contains_completion_indicators(response):
            completion_score += 0.4
        
        # Check for task-specific content
        if task_indicators:
            addressed_tasks = sum(
                1 for task in task_indicators
                if self._task_addressed_in_response(task, response)
            )
            completion_score += 0.6 * (addressed_tasks / len(task_indicators))
        else:
            completion_score += 0.6  # Assume completion if no specific tasks
        
        return min(completion_score, 1.0)
    
    def _assess_accuracy(self, prompt: str, response: str,
                       context: Dict[str, Any]) -> float:
        """Assess accuracy of the response."""
        # This is a simplified accuracy assessment
        # In practice, this might involve fact-checking, domain expertise, etc.
        
        accuracy_score = 0.0
        
        # Check for factual consistency indicators
        if self._contains_factual_language(response):
            accuracy_score += 0.3
        
        # Check for appropriate uncertainty expression
        if self._expresses_appropriate_uncertainty(response):
            accuracy_score += 0.3
        
        # Check for logical consistency
        if self._is_logically_consistent(response):
            accuracy_score += 0.4
        
        return min(accuracy_score, 1.0)
    
    def _assess_value_generation(self, prompt: str, response: str) -> float:
        """Assess the value generated by the response."""
        value_score = 0.0
        
        # Check for actionable insights
        if self._contains_actionable_insights(response):
            value_score += 0.3
        
        # Check for novel information or perspectives
        if self._contains_novel_content(response):
            value_score += 0.3
        
        # Check for practical utility
        if self._has_practical_utility(response):
            value_score += 0.4
        
        return min(value_score, 1.0)
    
    def _assess_satisfaction_proxy(self, response: str) -> float:
        """Assess likely user satisfaction based on response characteristics."""
        satisfaction_score = 0.0
        
        # Check response length appropriateness
        word_count = len(response.split())
        if 50 <= word_count <= 500:  # Reasonable length
            satisfaction_score += 0.3
        elif 20 <= word_count <= 1000:
            satisfaction_score += 0.2
        else:
            satisfaction_score += 0.1
        
        # Check for helpful tone
        if self._has_helpful_tone(response):
            satisfaction_score += 0.4
        
        # Check for completeness feeling
        if self._feels_complete(response):
            satisfaction_score += 0.3
        
        return min(satisfaction_score, 1.0)
    
    def _extract_task_indicators(self, prompt: str) -> List[str]:
        """Extract task indicators from the prompt."""
        task_patterns = [
            r'please\s+(.+?)(?:\.|,|\n|$)',
            r'can you\s+(.+?)(?:\.|,|\n|$)',
            r'I need\s+(.+?)(?:\.|,|\n|$)',
            r'help me\s+(.+?)(?:\.|,|\n|$)',
            r'explain\s+(.+?)(?:\.|,|\n|$)',
            r'analyze\s+(.+?)(?:\.|,|\n|$)'
        ]
        
        tasks = []
        for pattern in task_patterns:
            matches = re.findall(pattern, prompt, re.IGNORECASE)
            tasks.extend([match.strip() for match in matches])
        
        return tasks
    
    def _contains_completion_indicators(self, response: str) -> bool:
        """Check for task completion indicators."""
        completion_patterns = [
            r'completed?', r'finished', r'done', r'accomplished',
            r'here is', r'here are', r'the result', r'in summary'
        ]
        return any(re.search(pattern, response, re.IGNORECASE)
                  for pattern in completion_patterns)
    
    def _task_addressed_in_response(self, task: str, response: str) -> bool:
        """Check if a specific task is addressed in the response."""
        task_words = set(re.findall(r'\b\w+\b', task.lower()))
        response_words = set(re.findall(r'\b\w+\b', response.lower()))
        
        overlap = len(task_words & response_words)
        return overlap >= len(task_words) * 0.4
    
    def _contains_factual_language(self, response: str) -> bool:
        """Check for factual, evidence-based language."""
        factual_indicators = [
            r'research shows', r'studies indicate', r'evidence suggests',
            r'data shows', r'according to', r'based on', r'statistics'
        ]
        return any(re.search(pattern, response, re.IGNORECASE)
                  for pattern in factual_indicators)
    
    def _expresses_appropriate_uncertainty(self, response: str) -> bool:
        """Check for appropriate uncertainty expression."""
        uncertainty_indicators = [
            r'might', r'could', r'possibly', r'likely', r'probably',
            r'uncertain', r'unclear', r'depends on', r'varies'
        ]
        return any(re.search(pattern, response, re.IGNORECASE)
                  for pattern in uncertainty_indicators)
    
    def _is_logically_consistent(self, response: str) -> bool:
        """Check for logical consistency (simplified)."""
        # Look for contradictory statements
        contradiction_patterns = [
            (r'always', r'never'),
            (r'all', r'none'),
            (r'definitely', r'uncertain'),
            (r'impossible', r'possible')
        ]
        
        response_lower = response.lower()
        for pos_pattern, neg_pattern in contradiction_patterns:
            if (re.search(pos_pattern, response_lower) and 
                re.search(neg_pattern, response_lower)):
                return False
        
        return True
    
    def _contains_actionable_insights(self, response: str) -> bool:
        """Check for actionable insights."""
        actionable_indicators = [
            r'should', r'recommend', r'suggest', r'consider',
            r'try', r'implement', r'action', r'step', r'approach'
        ]
        return any(re.search(pattern, response, re.IGNORECASE)
                  for pattern in actionable_indicators)
    
    def _contains_novel_content(self, response: str) -> bool:
        """Check for novel or creative content."""
        novelty_indicators = [
            r'innovative', r'creative', r'novel', r'unique',
            r'alternative', r'different approach', r'new way'
        ]
        return any(re.search(pattern, response, re.IGNORECASE)
                  for pattern in novelty_indicators)
    
    def _has_practical_utility(self, response: str) -> bool:
        """Check for practical utility."""
        utility_indicators = [
            r'practical', r'useful', r'helpful', r'benefit',
            r'advantage', r'solution', r'tool', r'method'
        ]
        return any(re.search(pattern, response, re.IGNORECASE)
                  for pattern in utility_indicators)
    
    def _has_helpful_tone(self, response: str) -> bool:
        """Check for helpful, positive tone."""
        helpful_indicators = [
            r'happy to help', r'glad to', r'pleased to',
            r'certainly', r'of course', r'absolutely'
        ]
        return any(re.search(pattern, response, re.IGNORECASE)
                  for pattern in helpful_indicators)
    
    def _feels_complete(self, response: str) -> bool:
        """Check if response feels complete."""
        # Look for conclusion indicators
        conclusion_indicators = [
            r'in conclusion', r'to summarize', r'overall',
            r'in summary', r'finally', r'lastly'
        ]
        return any(re.search(pattern, response, re.IGNORECASE)
                  for pattern in conclusion_indicators)
    
    def _calculate_confidence(self, components: Dict[str, float],
                            context: Dict[str, Any]) -> float:
        """Calculate confidence in quality assessment."""
        # Base confidence on component consistency and available context
        values = list(components.values())
        variance = np.var(values)
        
        base_confidence = max(0.5, 1.0 - variance)
        
        # Adjust based on available context
        if context.get('ground_truth') or context.get('expert_evaluation'):
            base_confidence += 0.2
        
        return min(base_confidence, 1.0)
    
    def _generate_explanation(self, components: Dict[str, float],
                            score: float) -> str:
        """Generate explanation of quality score."""
        explanations = []
        
        if components['task_completion'] > 0.7:
            explanations.append("High task completion")
        elif components['task_completion'] < 0.4:
            explanations.append("Low task completion")
        
        if components['accuracy'] > 0.7:
            explanations.append("Good accuracy")
        elif components['accuracy'] < 0.4:
            explanations.append("Questionable accuracy")
        
        if components['value_generation'] > 0.7:
            explanations.append("High value generation")
        elif components['value_generation'] < 0.4:
            explanations.append("Limited value generation")
        
        if score > 0.8:
            overall = "Excellent quality"
        elif score > 0.6:
            overall = "Good quality"
        elif score > 0.4:
            overall = "Moderate quality"
        else:
            overall = "Poor quality"
        
        return f"{overall}. " + "; ".join(explanations)


class CIQCalculator:
    """Main calculator for all CIQ metrics."""
    
    def __init__(self):
        """Initialize CIQ calculator with all metric components."""
        self.clarity_metric = ClarityMetric()
        self.integrity_metric = IntegrityMetric()
        self.quality_metric = QualityMetric()
    
    def calculate_all_metrics(self, prompt: str, response: str,
                            context: Dict[str, Any]) -> Dict[str, float]:
        """
        Calculate all CIQ metrics for an interaction.
        
        Args:
            prompt: The input prompt or question
            response: The AI response to evaluate
            context: Additional context and metadata
            
        Returns:
            Dictionary with all CIQ scores and components
        """
        results = {}
        
        # Calculate individual metrics
        clarity_result = self.clarity_metric.calculate(prompt, response, context)
        integrity_result = self.integrity_metric.calculate(prompt, response, context)
        quality_result = self.quality_metric.calculate(prompt, response, context)
        
        # Store main scores
        results['clarity'] = clarity_result.score
        results['integrity'] = integrity_result.score
        results['quality'] = quality_result.score
        
        # Calculate composite CIQ score
        results['ciq_composite'] = (
            clarity_result.score + integrity_result.score + quality_result.score
        ) / 3
        
        # Store detailed components
        results['clarity_components'] = clarity_result.components
        results['integrity_components'] = integrity_result.components
        results['quality_components'] = quality_result.components
        
        # Store explanations
        results['clarity_explanation'] = clarity_result.explanation
        results['integrity_explanation'] = integrity_result.explanation
        results['quality_explanation'] = quality_result.explanation
        
        # Store confidence scores
        results['clarity_confidence'] = clarity_result.confidence
        results['integrity_confidence'] = integrity_result.confidence
        results['quality_confidence'] = quality_result.confidence
        
        return results
    
    def calculate_single_metric(self, metric_name: str, prompt: str,
                              response: str, context: Dict[str, Any]) -> MetricResult:
        """
        Calculate a single CIQ metric.
        
        Args:
            metric_name: 'clarity', 'integrity', or 'quality'
            prompt: The input prompt
            response: The AI response
            context: Additional context
            
        Returns:
            MetricResult for the specified metric
        """
        if metric_name == 'clarity':
            return self.clarity_metric.calculate(prompt, response, context)
        elif metric_name == 'integrity':
            return self.integrity_metric.calculate(prompt, response, context)
        elif metric_name == 'quality':
            return self.quality_metric.calculate(prompt, response, context)
        else:
            raise ValueError(f"Unknown metric: {metric_name}")
    
    def get_metric_summary(self, results: Dict[str, float]) -> Dict[str, Any]:
        """
        Generate a summary of CIQ metric results.
        
        Args:
            results: Results from calculate_all_metrics
            
        Returns:
            Summary dictionary with interpretations and recommendations
        """
        summary = {
            'overall_score': results['ciq_composite'],
            'individual_scores': {
                'clarity': results['clarity'],
                'integrity': results['integrity'],
                'quality': results['quality']
            },
            'interpretation': self._interpret_scores(results),
            'recommendations': self._generate_recommendations(results)
        }
        
        return summary
    
    def _interpret_scores(self, results: Dict[str, float]) -> str:
        """Interpret CIQ scores for human understanding."""
        composite = results['ciq_composite']
        
        if composite >= 0.8:
            return "Excellent constitutional AI collaboration"
        elif composite >= 0.6:
            return "Good constitutional AI collaboration"
        elif composite >= 0.4:
            return "Moderate constitutional AI collaboration"
        else:
            return "Poor constitutional AI collaboration"
    
    def _generate_recommendations(self, results: Dict[str, float]) -> List[str]:
        """Generate recommendations based on CIQ scores."""
        recommendations = []
        
        if results['clarity'] < 0.6:
            recommendations.append(
                "Improve communication clarity and reasoning transparency"
            )
        
        if results['integrity'] < 0.6:
            recommendations.append(
                "Strengthen adherence to constitutional principles and consistency"
            )
        
        if results['quality'] < 0.6:
            recommendations.append(
                "Enhance task completion and value generation"
            )
        
        if not recommendations:
            recommendations.append("Maintain current high standards of collaboration")
        
        return recommendations