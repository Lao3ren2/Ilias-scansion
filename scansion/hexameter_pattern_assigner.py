"""
Hexameter Pattern Assignment System
Assigns valid hexameter length patterns to verses using a probabilistic model.
"""

import csv
import math
import random
import argparse
from typing import List, Dict, Any, Tuple
from itertools import product


ALPHA = 2 #ALPHA = 2 is a beta(2,2) prior for the parameters, ALHPA=1 is uniform/no prior

INPUT_PATH = "../syllabification/digbib_ilias_syllabified.csv"

class HexameterPatternGenerator:
    """Generates all valid hexameter patterns for given syllable counts."""
    
    # Valid foot patterns (T=stressed, L=unstressed long, S=unstressed short)
    STRESSED_LONG = "TL"  # stressed-long
    STRESSED_SHORT_SHORT = "TSS"  # stressed-short-short
    LAST_STRESSED_LONG = "TL"  # stressed-long (catalectic)
    LAST_STRESSED_SHORT = "TS"  # stressed-short (catalectic)
    
    def __init__(self):
        self.patterns_by_count: Dict[int, List[str]] = {}
        self._generate_all_patterns()
    
    def _generate_all_patterns(self):
        """Generate all valid hexameter patterns and index by syllable count."""
        # First 5 feet: each can be stressed-long (2 syllables) or stressed-short-short (3 syllables)
        foot_options = [self.STRESSED_LONG, self.STRESSED_SHORT_SHORT]
        first_five = list(product(foot_options, repeat=5))
        
        # Last foot: stressed-long (2 syllables) or stressed-short (1 syllable, catalectic)
        last_options = [self.LAST_STRESSED_LONG, self.LAST_STRESSED_SHORT]
        
        for first_five_pattern in first_five:
            for last_foot in last_options:
                # Combine first 5 feet + last foot
                full_pattern = "".join(first_five_pattern) + last_foot
                syllable_count = len(full_pattern)
                
                if syllable_count not in self.patterns_by_count:
                    self.patterns_by_count[syllable_count] = []
                self.patterns_by_count[syllable_count].append(full_pattern)
    
    def get_patterns_for_count(self, syllable_count: int) -> List[str]:
        """Get all valid patterns for a given syllable count."""
        return self.patterns_by_count.get(syllable_count, [])
    
    def get_all_patterns(self) -> Dict[int, List[str]]:
        """Get all patterns indexed by syllable count."""
        return self.patterns_by_count



class SyllableModel:
    """Model for syllable stress and length probabilities."""
    
    def __init__(self, syllables: List[str], random_init: bool = False, 
                 use_third_last_position: bool = False):
        """
        Initialize model with syllable types.
        
        Args:
            syllables: List of unique syllable strings
            random_init: If True, initialize p_s randomly in [0.1, 0.9]
            use_third_last_position: If True, use a single parameter for third-to-last position
        """
        self.syllables = syllables
        self.use_third_last_position = use_third_last_position
        
        if random_init:
            # Initialize randomly in [0.1, 0.9] to avoid extreme values
            self.p_stressed = {s: random.uniform(0.1, 0.9) for s in syllables}
            self.p_long = {s: random.uniform(0.1, 0.9) for s in syllables}
        else:
            # Initialize all p_s = 0.5
            self.p_stressed = {s: 0.5 for s in syllables}
            self.p_long = {s: 0.5 for s in syllables}
        
        # Initialize third-to-last position parameter
        if use_third_last_position:
            if random_init:
                self.t_third_last_stressed = random.uniform(0.1, 0.9)
                self.t_third_last_long = random.uniform(0.1, 0.9)
            else:
                self.t_third_last_stressed = 0.5
                self.t_third_last_long = 0.5
        else:
            self.t_third_last_stressed = None
            self.t_third_last_long = None
    
    def get_p_stressed(self, syllable: str) -> float:
        """Get probability of being stressed for a syllable."""
        return self.p_stressed.get(syllable, 0.5)
    
    def set_p_stressed(self, syllable: str, value: float):
        """Set probability of being stressed for a syllable."""
        self.p_stressed[syllable] = value
    
    def get_all_p_stressed(self) -> Dict[str, float]:
        """Get all syllable stress probabilities."""
        return self.p_stressed.copy()
    
    def set_all_p_stressed(self, p_dict: Dict[str, float]):
        """Set all syllable stress probabilities."""
        self.p_stressed = p_dict.copy()
    
    def get_p_long(self, syllable: str) -> float:
        """Get probability of being long for a syllable."""
        return self.p_long.get(syllable, 0.5)
    
    def set_p_long(self, syllable: str, value: float):
        """Set probability of being long for a syllable."""
        self.p_long[syllable] = value
    
    def get_all_p_long(self) -> Dict[str, float]:
        """Get all syllable length probabilities."""
        return self.p_long.copy()
    
    def set_all_p_long(self, p_dict: Dict[str, float]):
        """Set all syllable length probabilities."""
        self.p_long = p_dict.copy()
    
    def get_third_last_position_stressed(self) -> float:
        """Get third-to-last position parameter for stress."""
        if self.use_third_last_position:
            return self.t_third_last_stressed
        return 0.5
    
    def set_third_last_position_stressed(self, value: float):
        """Set third-to-last position parameter for stress."""
        if self.use_third_last_position:
            self.t_third_last_stressed = value
    
    def get_third_last_position_long(self) -> float:
        """Get third-to-last position parameter for length."""
        if self.use_third_last_position:
            return self.t_third_last_long
        return 0.5
    
    def set_third_last_position_long(self, value: float):
        """Set third-to-last position parameter for length."""
        if self.use_third_last_position:
            self.t_third_last_long = value
    
    def get_combined_p_stressed(self, syllable: str, verse_length: int, position: int) -> float:
        """
        Get combined probability of being stressed using syllable and optional third-to-last position parameter.
        
        If use_third_last_position is enabled and this is the third-to-last syllable,
        uses log-odds combination: logit(P) = logit(p_stressed) + logit(t_stressed)
        where t_stressed is the third-to-last position parameter for stress.
        Then converts back to probability.
        
        Args:
            syllable: The syllable string
            verse_length: Total number of syllables in the verse
            position: Position of the syllable in the verse (1-indexed from left)
            
        Returns:
            Combined probability of being stressed
        """
        p_s = self.get_p_stressed(syllable)
        
        if not self.use_third_last_position:
            return p_s
        
        # Check if this is the third-to-last position
        is_third_last = (position == verse_length - 2)
        
        if not is_third_last:
            return p_s
        
        # Combine using log-odds addition
        def logit(p):
            if p <= 0 or p >= 1:
                p = max(0.001, min(0.999, p))
            return math.log(p / (1 - p))
        
        def sigmoid(x):
            return 1 / (1 + math.exp(-x))
        
        combined_logit = logit(p_s) + logit(self.t_third_last_stressed)
        combined_p = sigmoid(combined_logit)
        
        # Clip to reasonable range
        return max(0.001, min(0.999, combined_p))
    
    def get_combined_p_long(self, syllable: str, verse_length: int, position: int) -> float:
        """
        Get combined probability of being long using syllable and optional third-to-last position parameter.
        
        If use_third_last_position is enabled and this is the third-to-last syllable,
        uses log-odds combination: logit(P) = logit(p_long) + logit(t_long)
        where t_long is the third-to-last position parameter for length.
        Then converts back to probability.
        
        Args:
            syllable: The syllable string
            verse_length: Total number of syllables in the verse
            position: Position of the syllable in the verse (1-indexed from left)
            
        Returns:
            Combined probability of being long 
        """
        p_s = self.get_p_long(syllable)
        
        if not self.use_third_last_position:
            return p_s
        
        # Check if this is the third-to-last position
        is_third_last = (position == verse_length - 2)
        
        if not is_third_last:
            return p_s
        
        # Combine using log-odds addition
        def logit(p):
            if p <= 0 or p >= 1:
                p = max(0.001, min(0.999, p))
            return math.log(p / (1 - p))
        
        def sigmoid(x):
            return 1 / (1 + math.exp(-x))
        
        combined_logit = logit(p_s) + logit(self.t_third_last_long)
        combined_p = sigmoid(combined_logit)
        
        # Clip to reasonable range
        return max(0.001, min(0.999, combined_p))


class EMScansion:
    """EM algorithm for hexameter scansion."""
    
    def __init__(self, model: SyllableModel):
        """
        Initialize EM algorithm.
        
        Args:
            model: SyllableModel with syllable probabilities
        """
        self.model = model
        self.pattern_generator = HexameterPatternGenerator()
    
    def load_verses(self, csv_path: str) -> List[Dict[str, Any]]:
        """Load verses from CSV file."""
        verses = []
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                verses.append(row)
        return verses
    
    
    def compute_pattern_probability(self, pattern: str, syllables: List[str]) -> float:
        """
        Compute unnormalized probability of a pattern given syllables.
        
        For three-way distinction (T=stressed, L= unstressed long, S=unstressed short):
        P(sigma | v, theta) ∝ product over i of:
        - If sigma_i = T: p_stressed * p_long
        - If sigma_i = L: (1 - p_stressed) * p_long
        - If sigma_i = S: (1 - p_stressed) * (1 - p_long)
        
        If position parameters are enabled, uses combined probability from syllable and position.
        
        Args:
            pattern: String like "TLTLTLTLTLTS"
            syllables: List of syllable strings
            
        Returns:
            Unnormalized log probability (use log for numerical stability)
        """
        if len(pattern) != len(syllables):
            return -float('inf')
        
        log_prob = 0.0
        verse_length = len(syllables)
        
        for position, (pattern_char, syllable) in enumerate(zip(pattern, syllables), start=1):
            p_stressed = self.model.get_combined_p_stressed(syllable, verse_length, position)
            p_long = self.model.get_combined_p_long(syllable, verse_length, position)
            
            if pattern_char == 'T':
                log_prob += math.log(p_stressed) + math.log(p_long)
            elif pattern_char == 'L':
                log_prob += math.log(1.0 - p_stressed) + math.log(p_long)
            else:  # 'S'
                log_prob += math.log(1.0 - p_stressed) + math.log(1.0 - p_long)
        
        return log_prob
    
    def e_step(self, verses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        E-step: Compute posterior probabilities for each scansion for each verse.
        
        Args:
            verses: List of verse dictionaries
            
        Returns:
            List of verse data with pattern probabilities
        """
        verse_data = []
        skipped = 0
        
        for verse in verses:
            # Parse syllabified text
            syllabified = verse['verse_syllabified']
            syllables = syllabified.split('|')
            syllable_count = len(syllables)
            
            # Get valid patterns for this syllable count
            valid_patterns = self.pattern_generator.get_patterns_for_count(syllable_count)
            
            if not valid_patterns:
                # No valid patterns found, skip this verse
                skipped += 1
                continue
            
            # Compute log probabilities for each pattern
            log_probs = []
            for pattern in valid_patterns:
                log_prob = self.compute_pattern_probability(pattern, syllables)
                log_probs.append(log_prob)
            
            # Normalize using log-sum-exp for numerical stability
            max_log = max(log_probs)
            exp_log_probs = [math.exp(lp - max_log) for lp in log_probs]
            total = sum(exp_log_probs)
            # Compute normalized probabilities
            pattern_probs = {}
            for pattern, exp_lp in zip(valid_patterns, exp_log_probs):
                pattern_probs[pattern] = exp_lp / total
            
            verse_data.append({
                'verse': verse,
                'syllables': syllables,
                'patterns': valid_patterns,
                'pattern_probs': pattern_probs
            })
        
        if skipped > 0:
            print(f"  Skipped {skipped} verses with no valid patterns")
        
        return verse_data
    
    def m_step(self, verse_data: List[Dict[str, Any]]) -> Tuple[Dict[str, float], Dict[str, float], float, float]:
        """
        M-step: Update parameters (using Beta(2,2) prior if ALPHA=2)
        If ALPHA=2
        For syllables: 
        - p_stressed_new = (1 + E[stressed counts of s]) / (2 + E[total counts of s])
        - p_long_new = (1 + E[long counts of s]) / (2 + E[total counts of s])
        For third-to-last position:
        - t_stressed_new = (1 + E[stressed counts at third-to-last]) / (2 + E[total counts at third-to-last])
        - t_long_new = (1 + E[long counts at third-to-last]) / (2 + E[total counts at third-to-last])
        
        Args:
            verse_data: Output from E-step
            
        Returns:
            Tuple of (new p_stressed values, new p_long values, new t_stressed value, new t_long value)
        """
        # Initialize counts for syllables
        expected_stressed_counts = {s: 0.0 for s in self.model.syllables}
        expected_long_counts = {s: 0.0 for s in self.model.syllables}
        expected_total_counts = {s: 0.0 for s in self.model.syllables}
        expected_not_stressed_counts = {s: 0.0 for s in self.model.syllables}
        
        # Initialize counts for third-to-last position
        expected_stressed_third_last = 0.0
        expected_long_third_last = 0.0
        expected_total_third_last = 0.0
        expected_not_stressed_third_last = 0.0
        
        for data in verse_data:
            syllables = data['syllables']
            patterns = data['patterns']
            pattern_probs = data['pattern_probs']
            verse_length = len(syllables)
            
            for pattern, prob in pattern_probs.items():
                for position, (syllable, pattern_char) in enumerate(zip(syllables, pattern), start=1):
                    # Update syllable counts
                    if syllable in expected_stressed_counts:
                        expected_total_counts[syllable] += prob
                        if pattern_char == 'T':
                            expected_stressed_counts[syllable] += prob
                            expected_long_counts[syllable] += prob
                        elif pattern_char == 'L':
                            expected_long_counts[syllable] += prob
                        else:  # 'S'
                            pass
                    
                    # Update third-to-last position counts if enabled
                    if self.model.use_third_last_position:
                        # Check if this is the third-to-last position
                        is_third_last = (position == verse_length - 2)
                        if is_third_last:
                            expected_total_third_last += prob
                            if pattern_char == 'T':
                                expected_stressed_third_last += prob
                                expected_long_third_last += prob
                            elif pattern_char == 'L':
                                expected_long_third_last += prob
                            else:  # 'S'
                                pass
        
        # Update syllable parameters with Beta(2,2) prior
        new_p_stressed = {}
        new_p_long = {}
        for syllable in self.model.syllables:
            stressed_count = expected_stressed_counts[syllable]
            total_count = expected_total_counts[syllable]
            long_count = expected_long_counts[syllable]
            
            if total_count > 0:
                # Beta(2,2) prior for stressed: add 1 to numerator, 2 to denominator
                new_p_stressed_val = ((ALPHA - 1) + stressed_count) / ((2* (ALPHA - 1)) + total_count)
            
            new_p_stressed[syllable] = new_p_stressed_val
            
            if total_count > 0:
                # Beta(2,2) prior for long: add 1 to numerator, 2 to denominator
                new_p_long_val = ((ALPHA-1) + long_count) / ((2*(ALPHA-1)) + total_count)
            
            new_p_long[syllable] = new_p_long_val
        
        # Update third-to-last position parameters with Beta(2,2) prior
        new_t_stressed = 0.5
        new_t_long = 0.5
        if self.model.use_third_last_position:
            if expected_total_third_last > 0:
                # Beta(2,2) prior for stressed: add 1 to numerator, 2 to denominator
                new_t_stressed = (1.0 + expected_stressed_third_last) / (2.0 + expected_total_third_last)
            
            
            if expected_total_third_last > 0:
                # Beta(2,2) prior for long: add 1 to numerator, 2 to denominator
                new_t_long = (1.0 + expected_long_third_last) / (2.0 + expected_total_third_last)
            
        
        return new_p_stressed, new_p_long, new_t_stressed, new_t_long
    
    def em_optimize(self, verses: List[Dict[str, Any]], max_iterations: int = 100,
                    epsilon: float = 1e-4) -> Tuple[Dict[str, float], Dict[str, float], float, float, float]:
        """
        Run EM algorithm to optimize parameters.
        
        Args:
            verses: List of verse dictionaries
            max_iterations: Maximum number of EM iterations
            epsilon: Convergence tolerance
            
        Returns:
            Tuple of (final p_stressed values, final p_long values, final t_stressed value, final t_long value, final entropy)
        """
        print(f"\nRunning EM optimization (max {max_iterations} iterations)...")
        
        prev_p_stressed = self.model.get_all_p_stressed()
        prev_p_long = self.model.get_all_p_long()
        prev_t_stressed = self.model.get_third_last_position_stressed() if self.model.use_third_last_position else 0.5
        prev_t_long = self.model.get_third_last_position_long() if self.model.use_third_last_position else 0.5
        final_entropy = 0.0
        
        for iteration in range(max_iterations):
            # E-step
            verse_data = self.e_step(verses)
            
            # Compute entropy
            entropy = self.compute_entropy(verse_data)
            
            # M-step
            new_p_stressed, new_p_long, new_t_stressed, new_t_long = self.m_step(verse_data)
            self.model.set_all_p_stressed(new_p_stressed)
            self.model.set_all_p_long(new_p_long)
            if self.model.use_third_last_position:
                self.model.set_third_last_position_stressed(new_t_stressed)
                self.model.set_third_last_position_long(new_t_long)
            
            # Check convergence
            max_change = 0.0
            for syllable in self.model.syllables:
                change_stressed = abs(new_p_stressed[syllable] - prev_p_stressed[syllable])
                change_long = abs(new_p_long[syllable] - prev_p_long[syllable])
                max_change = max(max_change, change_stressed, change_long)
            
            if self.model.use_third_last_position:
                change_t_stressed = abs(new_t_stressed - prev_t_stressed)
                change_t_long = abs(new_t_long - prev_t_long)
                max_change = max(max_change, change_t_stressed, change_t_long)
            
            if iteration % 10 == 0 or iteration == max_iterations - 1:
                print(f"  Iteration {iteration + 1}: max_change = {max_change:.6f}, "
                      f"entropy = {entropy:.4f}, verses used = {len(verse_data)}")
            
            if max_change < epsilon:
                print(f"  Converged after {iteration + 1} iterations")
                final_entropy = entropy
                break
            
            prev_p_stressed = new_p_stressed.copy()
            prev_p_long = new_p_long.copy()
            prev_t_stressed = new_t_stressed
            prev_t_long = new_t_long
            final_entropy = entropy
        
        print("EM optimization complete")
        return (self.model.get_all_p_stressed(), self.model.get_all_p_long(), 
                self.model.get_third_last_position_stressed(), 
                self.model.get_third_last_position_long(), final_entropy)
    
    def assign_best_patterns(self, verses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Assign most likely pattern to each verse.
        Args:
            verses: List of verse dictionaries
            
        Returns:
            List of verses with assigned patterns and confidence
        """
        results = []
        
        for verse in verses:
            # Parse syllabified text
            syllabified = verse['verse_syllabified']
            syllables = syllabified.split('|')
            syllable_count = len(syllables)
            
            # Get valid patterns for this syllable count
            valid_patterns = self.pattern_generator.get_patterns_for_count(syllable_count)
            
            if not valid_patterns:
                # No valid patterns found
                result = verse.copy()
                result['syllable_count'] = syllable_count
                result['assigned_pattern'] = ''
                result['confidence'] = 0.0
                results.append(result)
                continue
                        
            # Compute probabilities and find best
            best_pattern = None
            best_prob = -float('inf')
            best_idx = 0
            pattern_probs = {}
            
            for idx, pattern in enumerate(valid_patterns):
                log_prob = self.compute_pattern_probability(pattern, syllables)
                pattern_probs[pattern] = log_prob
                if log_prob > best_prob:
                    best_prob = log_prob
                    best_pattern = pattern
                    best_idx = idx
            
            # Normalize to get confidence
            max_log = max(pattern_probs.values())
            exp_probs = [math.exp(lp - max_log) for lp in pattern_probs.values()]
            total = sum(exp_probs)
            confidence = exp_probs[best_idx] / total
            
            formatted_pattern = ''.join(best_pattern)
            
            result = verse.copy()
            result['syllable_count'] = syllable_count
            result['assigned_pattern'] = formatted_pattern
            result['confidence'] = confidence
            results.append(result)
        
        return results
    
    def save_results(self, results: List[Dict[str, Any]], output_path: str):
        """Save results to CSV file."""
        fieldnames = ['line_number', 'book_number', 'original_text', 'verse_normalized', 'verse_syllabified', 'syllable_count',
                     'assigned_pattern', 'confidence']
        
        with open(output_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for result in results:
                row = {field: result.get(field, '') for field in fieldnames}
                writer.writerow(row)
        
        print(f"Saved {len(results)} verses to {output_path}")
    
    def save_syllable_probabilities(self, output_path: str):
        """Save syllable probabilities to CSV file."""
        with open(output_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['syllable', 'p_stressed', 'p_long'])
            writer.writeheader()
            p_stressed = self.model.get_all_p_stressed()
            p_long = self.model.get_all_p_long()
            for syllable in p_stressed.keys():
                writer.writerow({'syllable': syllable, 'p_stressed': p_stressed[syllable], 'p_long': p_long[syllable]})
        
        print(f"Saved syllable probabilities to {output_path}")
    
    def save_position_probabilities(self, output_path: str):
        """Save position probabilities to CSV file."""
        if not self.model.use_third_last_position:
            print("Position parameters not enabled, skipping save")
            return
        
        with open(output_path, 'w', encoding='utf-8', newline='') as f:
            fieldnames = ['position', 'p_stressed', 'p_long']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerow({'position': 'third_to_last', 
                           'p_stressed': self.model.get_third_last_position_stressed(),
                           'p_long': self.model.get_third_last_position_long()})
        
        print(f"Saved position probabilities to {output_path}")
    
    def compute_entropy(self, verse_data: List[Dict[str, Any]]) -> float:
        """
        Compute average entropy of scansion posterior across all verses.
        
        Lower entropy means more confident predictions (better fit).
        
        Args:
            verse_data: Output from E-step
            
        Returns:
            Average entropy across all verses
        """
        total_entropy = 0.0
        count = 0
        
        for data in verse_data:
            pattern_probs = data['pattern_probs']
            # Compute entropy: -sum(p * log(p))
            entropy = 0.0
            for prob in pattern_probs.values():
                if prob > 0:
                    entropy -= prob * math.log(prob)
            total_entropy += entropy
            count += 1
        
        if count > 0:
            return total_entropy / count
        return 0.0


def main():
    """Main execution function."""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='EM algorithm for hexameter scansion')
    parser.add_argument('--output', '-o', type=str, default='verses_with_patterns.csv',
                        help='Output CSV file for verse patterns (default: verses_with_patterns.csv)')
    parser.add_argument('--syllable-output', '-s', type=str, default='syllable_probabilities.csv',
                        help='Output CSV file for syllable probabilities (default: syllable_probabilities.csv)')
    parser.add_argument('--position-output', '-p', type=str, default='position_probabilities.csv',
                        help='Output CSV file for position probabilities (default: position_probabilities.csv)')
    parser.add_argument('--random-init', action='store_true',
                        help='Initialize syllable probabilities randomly instead of 0.5')
    parser.add_argument('--use-third-last-position', action='store_true',
                        help='Use a single parameter for the third-to-last position')
    parser.add_argument('--max-iterations', '-i', type=int, default=100,
                        help='Maximum number of EM iterations (default: 100)')
    parser.add_argument('--seed', type=int, default=None,
                        help='Random seed for reproducibility')
    
    args = parser.parse_args()
    
    # Set random seed if provided
    if args.seed is not None:
        random.seed(args.seed)
        print(f"Random seed set to {args.seed}")
    
    print(f"ALHPA={ALPHA}")

    # Load syllables
    print(f"Loading syllables from {INPUT_PATH}...")
    syllables = []
    with open(INPUT_PATH, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            syllabified = row['verse_syllabified']
            verse_syllables = syllabified.split('|')
            syllables.extend(verse_syllables)
    syllables = list(set(syllables))
    print(f"Loaded {len(syllables)} unique syllables")
    
    # Initialize model
    init_type = "random" if args.random_init else "0.5"
    print(f"Initializing syllable probabilities: {init_type}")
    if args.use_third_last_position:
        print("Using third-to-last position parameter")
    model = SyllableModel(syllables, random_init=args.random_init, 
                          use_third_last_position=args.use_third_last_position)
    
    # Initialize EM algorithm
    em = EMScansion(model)
    
    # Load verses
    print(f"Loading verses from {INPUT_PATH}.csv...")
    verses = em.load_verses(INPUT_PATH)
    print(f"Loaded {len(verses)} verses")
    
    # Print pattern statistics
    patterns_by_count = em.pattern_generator.get_all_patterns()
    print(f"\nValid patterns by syllable count:")
    for count in sorted(patterns_by_count.keys()):
        print(f"  {count} syllables: {len(patterns_by_count[count])} patterns")
    
    # Run EM optimization
    final_p_stressed, final_p_long, final_t_stressed, final_t_long, final_entropy = em.em_optimize(
        verses, max_iterations=args.max_iterations, epsilon=1e-4)
    
    # Print final entropy (measure of fit)
    print(f"\nFinal entropy (lower is better): {final_entropy:.4f}")
    
    # Save syllable probabilities
    em.save_syllable_probabilities(args.syllable_output)
    
    # Save position probabilities if enabled
    if args.use_third_last_position:
        em.save_position_probabilities(args.position_output)
    
    # Assign best patterns
    print("\nAssigning best patterns to verses...")
    results = em.assign_best_patterns(verses)
    
    # Save results
    em.save_results(results, args.output)
    
    # Print statistics
    print(f"\nAssignment Statistics:")
    assigned = sum(1 for r in results if r['assigned_pattern'])
    print(f"  Successfully assigned: {assigned}/{len(results)}")
    
    # Show sample syllable probabilities
    print(f"\nSample syllable probabilities (first 10):")
    for i, syllable in enumerate(list(final_p_stressed.keys())[:10]):
        print(f"  {syllable}: p_stressed={final_p_stressed[syllable]:.4f}, p_long={final_p_long[syllable]:.4f}")
    
    # Show sample position probabilities if enabled
    if args.use_third_last_position:
        print(f"\nThird-to-last position probabilities: t_stressed={final_t_stressed:.4f}, t_long={final_t_long:.4f}")
    
    # Show sample results
    print(f"\nSample results (first 5):")
    for i, result in enumerate(results[:5]):
        print(f"  Line {result['line_number']}: {result['assigned_pattern']} (confidence: {result['confidence']:.4f})")


if __name__ == "__main__":
    main()
