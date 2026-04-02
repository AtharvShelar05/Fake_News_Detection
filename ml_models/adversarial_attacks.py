"""
Adversarial Attack Strategies for Fake News Detection
Implements synonym substitution, character perturbation, and paraphrasing attacks
"""

import random
import numpy as np
import pandas as pd
from typing import List, Tuple


class AdversarialAttacks:
    """
    Generate adversarial examples to test model robustness
    """
    
    # Synonym mapping for common words
    SYNONYM_DICT = {
        'fake': ['false', 'fraudulent', 'bogus', 'fabricated', 'phony'],
        'news': ['story', 'report', 'article', 'information', 'claim'],
        'virus': ['pathogen', 'infection', 'microbe', 'bug', 'contagion'],
        'vaccine': ['inoculation', 'immunization', 'shot', 'jab', 'dose'],
        'government': ['state', 'administration', 'authority', 'regime', 'parliament'],
        'scientist': ['researcher', 'scholar', 'expert', 'investigator', 'analyst'],
        'discover': ['find', 'uncover', 'reveal', 'detect', 'identify'],
        'claim': ['assert', 'state', 'declare', 'allege', 'maintain'],
        'disease': ['illness', 'disorder', 'affliction', 'sickness', 'condition'],
        'health': ['wellness', 'wellbeing', 'fitness', 'vigor', 'condition'],
        'conspiracy': ['plot', 'scheme', 'intrigue', 'cabal', 'agenda'],
        'hoax': ['fraud', 'scam', 'trick', 'deception', 'swindle'],
        'breaking': ['urgent', 'critical', 'pressing', 'immediate', 'acute'],
        'shocking': ['startling', 'astounding', 'amazing', 'surprising', 'stunning'],
        'expose': ['reveal', 'uncover', 'unmask', 'bare', 'disclose'],
        'scandal': ['outrage', 'disgrace', 'shame', 'embarrassment', 'uproar'],
    }
    
    def __init__(self, random_state=42):
        """
        Initialize adversarial attack generator.
        
        Args:
            random_state (int): For reproducibility
        """
        self.random_state = random_state
        random.seed(random_state)
        np.random.seed(random_state)
    
    def synonym_substitution_attack(self, text: str, perturbation_rate: float = 0.3) -> str:
        """
        Replace words with synonyms to create adversarial text.
        
        Args:
            text (str): Original text
            perturbation_rate (float): Fraction of words to substitute (0-1)
            
        Returns:
            str: Adversarially modified text
        """
        words = text.split()
        num_to_perturb = max(1, int(len(words) * perturbation_rate))
        
        # Randomly select indices to perturb
        perturb_indices = random.sample(range(len(words)), min(num_to_perturb, len(words)))
        
        perturbed_words = words.copy()
        for idx in perturb_indices:
            word = words[idx].lower()
            # Check if word has synonyms defined
            if word in self.SYNONYM_DICT:
                synonym = random.choice(self.SYNONYM_DICT[word])
                perturbed_words[idx] = synonym
        
        return ' '.join(perturbed_words)
    
    def character_perturbation_attack(self, text: str, perturbation_rate: float = 0.1) -> str:
        """
        Insert or delete random characters to create adversarial text.
        
        Args:
            text (str): Original text
            perturbation_rate (float): Fraction of characters to modify
            
        Returns:
            str: Text with character-level perturbations
        """
        text_len = len(text)
        num_to_perturb = max(1, int(text_len * perturbation_rate))
        
        perturb_indices = random.sample(range(text_len), min(num_to_perturb, text_len))
        
        text_list = list(text)
        for idx in perturb_indices:
            operation = random.choice(['insert', 'delete', 'substitute'])
            
            if operation == 'insert' and idx < len(text_list):
                # Insert random character
                random_char = random.choice('abcdefghijklmnopqrstuvwxyz ')
                text_list.insert(idx, random_char)
            elif operation == 'delete' and len(text_list) > 1 and text_list[idx] != ' ':
                # Delete character
                text_list.pop(idx)
            elif operation == 'substitute':
                # Substitute with random character
                if text_list[idx] != ' ':
                    text_list[idx] = random.choice('abcdefghijklmnopqrstuvwxyz')
        
        return ''.join(text_list)
    
    def word_level_paraphrase_attack(self, text: str) -> str:
        """
        Simulate word-level paraphrasing by reordering and rewording.
        
        Args:
            text (str): Original text
            
        Returns:
            str: Paraphrased version of text
        """
        words = text.split()
        
        if len(words) < 3:
            return text
        
        # Split into content and stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of'}
        
        # Randomly reorder non-consecutive phrase chunks
        # Keep some structure but modify word order
        phrases = []
        current_phrase = []
        
        for word in words:
            current_phrase.append(word)
            if len(current_phrase) >= random.randint(2, 4) or word in stop_words:
                phrases.append(current_phrase)
                current_phrase = []
        
        if current_phrase:
            phrases.append(current_phrase)
        
        # Shuffle mid-level phrases while keeping some structure
        if len(phrases) > 1:
            # Keep first and last phrase, shuffle middle ones
            shuffled = [phrases[0]]
            if len(phrases) > 2:
                middle = phrases[1:-1]
                random.shuffle(middle)
                shuffled.extend(middle)
            shuffled.append(phrases[-1])
            phrases = shuffled
        
        return ' '.join([' '.join(phrase) for phrase in phrases])
    
    def generate_adversarial_dataset(self, texts: List[str], attack_type: str = 'all') -> List[Tuple[str, str]]:
        """
        Generate adversarial version of texts.
        
        Args:
            texts (List[str]): Original texts
            attack_type (str): 'synonym', 'character', 'paraphrase', or 'all'
            
        Returns:
            List[Tuple[str, str]]: List of (original, adversarial) text pairs
        """
        adversarial_pairs = []
        
        attack_methods = {
            'synonym': self.synonym_substitution_attack,
            'character': self.character_perturbation_attack,
            'paraphrase': self.word_level_paraphrase_attack,
        }
        
        if attack_type == 'all':
            methods = list(attack_methods.values())
        else:
            methods = [attack_methods[attack_type]]
        
        for text in texts:
            # Apply each selected attack method
            for method in methods:
                try:
                    adversarial_text = method(text)
                    adversarial_pairs.append((text, adversarial_text))
                except Exception as e:
                    print(f"Error applying {method.__name__} to text: {e}")
                    continue
        
        return adversarial_pairs
    
    def create_mixed_adversarial_dataset(self, texts: List[str], labels: np.ndarray) -> Tuple[List[str], np.ndarray]:
        """
        Create dataset with mix of original and adversarial samples.
        
        Args:
            texts (List[str]): Original texts
            labels (np.ndarray): Corresponding labels
            
        Returns:
            Tuple[List[str], np.ndarray]: Mixed dataset (texts, labels)
        """
        augmented_texts = list(texts)
        augmented_labels = list(labels)
        
        attack_types = ['synonym', 'character', 'paraphrase']
        
        for text, label in zip(texts, labels):
            for attack_type in attack_types:
                try:
                    if attack_type == 'synonym':
                        adversarial = self.synonym_substitution_attack(text)
                    elif attack_type == 'character':
                        adversarial = self.character_perturbation_attack(text)
                    else:  # paraphrase
                        adversarial = self.word_level_paraphrase_attack(text)
                    
                    augmented_texts.append(adversarial)
                    augmented_labels.append(label)
                except Exception as e:
                    print(f"Error in {attack_type} attack: {e}")
                    continue
        
        return augmented_texts, np.array(augmented_labels)
    
    def evaluate_attack_success(self, original_texts: List[str], 
                                adversarial_texts: List[str],
                                model_predict_func) -> dict:
        """
        Evaluate how well adversarial examples can fool the model.
        
        Args:
            original_texts (List[str]): Original texts
            adversarial_texts (List[str]): Adversarial texts
            model_predict_func: Function to get model predictions
            
        Returns:
            dict: Attack success metrics
        """
        original_preds = model_predict_func(original_texts)
        adversarial_preds = model_predict_func(adversarial_texts)
        
        # Count how many predictions changed
        changed = np.sum(original_preds != adversarial_preds)
        attack_success_rate = changed / len(original_preds) if len(original_preds) > 0 else 0
        
        return {
            'attack_success_rate': float(attack_success_rate),
            'predictions_changed': int(changed),
            'total_samples': len(original_preds)
        }


def main():
    """
    Example: Generate and display adversarial examples
    """
    # Sample texts
    sample_texts = [
        "breaking news scientists discover new cure disease",
        "shocking celebrities caught fake scandal spreading online",
        "government announces new policy updates citizens",
        "urgent viral claim vaccine side effects false"
    ]
    
    attacker = AdversarialAttacks(random_state=42)
    
    print("=== Adversarial Attack Examples ===\n")
    
    for text in sample_texts[:2]:  # Show 2 examples
        print(f"Original: {text}")
        print(f"Synonym Attack: {attacker.synonym_substitution_attack(text)}")
        print(f"Character Attack: {attacker.character_perturbation_attack(text)}")
        print(f"Paraphrase Attack: {attacker.word_level_paraphrase_attack(text)}")
        print("-" * 80)


if __name__ == "__main__":
    main()
