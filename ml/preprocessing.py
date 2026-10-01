"""
ML-specific Text Preprocessing for Child Safety Classifier.

Provides text cleaning, normalization, and optional data augmentation
for the training pipeline.
"""

import re
import random
from typing import List, Tuple


def clean_for_ml(text: str) -> str:
    """
    Clean text for ML processing.
    - Lowercase
    - Remove special characters (keep emojis)
    - Light stemming/normalization
    """
    if not text or not isinstance(text, str):
        return ""
    
    text = text.lower().strip()
    
    # Normalize unicode quotes and apostrophes
    text = text.replace('\u2019', "'").replace('\u2018', "'")
    text = text.replace('\u201c', '"').replace('\u201d', '"')
    
    # Remove URLs
    text = re.sub(r'https?://\S+', ' URL ', text)
    text = re.sub(r'www\.\S+', ' URL ', text)
    
    # Keep emojis but remove other special chars
    # First, mark emojis
    emoji_pattern = re.compile(
        "[\U0001F600-\U0001F64F"
        "\U0001F300-\U0001F5FF"
        "\U0001F680-\U0001F6FF"
        "\U0001F1E0-\U0001F1FF"
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "\u2640-\u2642"
        "\u2600-\u2B55]+",
        flags=re.UNICODE
    )
    
    # Extract emojis
    emojis = emoji_pattern.findall(text)
    
    # Remove special chars but keep alphanumeric, spaces, and basic punctuation
    text = re.sub(r"[^a-z0-9\s'.!?,]", ' ', text)
    
    # Simple contractions expansion
    text = re.sub(r"won't", "will not", text)
    text = re.sub(r"can't", "cannot", text)
    text = re.sub(r"n't", " not", text)
    text = re.sub(r"'re", " are", text)
    text = re.sub(r"'s", " is", text)
    text = re.sub(r"'d", " would", text)
    text = re.sub(r"'ll", " will", text)
    text = re.sub(r"'ve", " have", text)
    text = re.sub(r"'m", " am", text)
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Add emojis back
    if emojis:
        text = text + ' ' + ' '.join(emojis)
    
    return text


def augment_data(samples: List[Tuple[str, str]], 
                 augment_factor: int = 2) -> List[Tuple[str, str]]:
    """
    Simple data augmentation using text transformations.
    
    Techniques:
    - Synonym replacement (simple)
    - Random word deletion
    - Character repetition variation
    
    Args:
        samples: List of (text, label) tuples
        augment_factor: How many augmented copies per sample
    
    Returns:
        Original samples + augmented samples
    """
    # Simple synonym groups for augmentation
    synonym_groups = [
        ['ugly', 'hideous', 'gross', 'disgusting', 'repulsive'],
        ['stupid', 'dumb', 'idiotic', 'foolish', 'brainless'],
        ['hate', 'despise', 'detest', 'loathe', 'abhor'],
        ['hurt', 'harm', 'injure', 'attack', 'wound'],
        ['kill', 'destroy', 'eliminate', 'annihilate'],
        ['friend', 'buddy', 'pal', 'mate'],
        ['happy', 'glad', 'joyful', 'pleased', 'cheerful'],
        ['sad', 'unhappy', 'miserable', 'depressed', 'down'],
        ['scared', 'afraid', 'frightened', 'terrified', 'fearful'],
        ['secret', 'private', 'hidden', 'confidential'],
        ['beautiful', 'pretty', 'gorgeous', 'stunning', 'attractive'],
        ['send', 'give', 'share', 'transfer', 'provide'],
        ['photo', 'picture', 'pic', 'selfie', 'image'],
        ['money', 'cash', 'funds', 'payment'],
        ['everyone', 'everybody', 'all of them', 'the whole school'],
        ['nobody', 'no one', 'not a single person'],
    ]
    
    synonym_map = {}
    for group in synonym_groups:
        for word in group:
            synonym_map[word] = [w for w in group if w != word]
    
    augmented = list(samples)  # Start with original samples
    
    for text, label in samples:
        for _ in range(augment_factor):
            aug_text = text
            
            technique = random.choice(['synonym', 'delete', 'repeat'])
            
            if technique == 'synonym':
                # Replace one word with a synonym
                words = aug_text.split()
                replaceable = [
                    (i, w.lower()) for i, w in enumerate(words) 
                    if w.lower() in synonym_map
                ]
                if replaceable:
                    idx, word = random.choice(replaceable)
                    replacement = random.choice(synonym_map[word])
                    words[idx] = replacement
                    aug_text = ' '.join(words)
                else:
                    continue  # Skip if no synonyms available
                    
            elif technique == 'delete':
                # Delete a random word (if message is long enough)
                words = aug_text.split()
                if len(words) > 4:
                    del_idx = random.randint(0, len(words) - 1)
                    words.pop(del_idx)
                    aug_text = ' '.join(words)
                else:
                    continue
                    
            elif technique == 'repeat':
                # Add character repetition to a word (e.g., soo -> sooo)
                words = aug_text.split()
                if words:
                    idx = random.randint(0, len(words) - 1)
                    word = words[idx]
                    if len(word) > 2:
                        char_idx = random.randint(0, len(word) - 1)
                        words[idx] = word[:char_idx] + word[char_idx] * 2 + word[char_idx+1:]
                    aug_text = ' '.join(words)
                else:
                    continue
            
            if aug_text != text:  # Only add if actually different
                augmented.append((aug_text, label))
    
    return augmented


if __name__ == '__main__':
    # Demo
    test_texts = [
        "Don't tell your parents about us talking!",
        "I'll kill you in the game 😂",
        "What's your home address?",
        "We killed them in the football match",
    ]
    
    print("=== ML Text Preprocessing Demo ===")
    for text in test_texts:
        print(f"\nOriginal: {text}")
        print(f"Cleaned:  {clean_for_ml(text)}")
