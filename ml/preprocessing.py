"""
ML-specific Text Preprocessing for Child Safety Classifier.

Provides text cleaning, normalization, and optional data augmentation
for the training pipeline.
"""

import re
import random
from typing import List, Tuple


# Regex for common emojis
EMOJI_PATTERN = re.compile(
    "[\U0001F600-\U0001F64F"
    "\U0001F300-\U0001F5FF"
    "\U0001F680-\U0001F6FF"
    "\U0001F1E0-\U0001F1FF"
    "\U00002702-\U000027B0"
    "\U000024C2-\U0001F251"
    "\U0001F900-\U0001F9FF"
    "\U0001FA70-\U0001FAFF"
    "\u2640-\u2642"
    "\u2600-\u2B55]+",
    flags=re.UNICODE
)

# Common leetspeak and character obfuscation replacements
LEETSPEAK_MAPPINGS = [
    (re.compile(r'\bk[!1|l]{2,}\b', re.I), 'kill'),
    (re.compile(r'\bk[!1]ll\b', re.I), 'kill'),
    (re.compile(r'\bd[!1]e\b', re.I), 'die'),
    (re.compile(r'\b[@a][s$]{2}\b', re.I), 'ass'),
    (re.compile(r'\bb[!1]tch\b', re.I), 'bitch'),
    (re.compile(r'\bsh[!1]t\b', re.I), 'shit'),
    (re.compile(r'\bf[\*u]ck\b', re.I), 'fuck'),
    (re.compile(r'\bfck\b', re.I), 'fuck'),
    (re.compile(r'\bh[@a]te\b', re.I), 'hate'),
    (re.compile(r'\bp[!1]c\b', re.I), 'pic'),
    (re.compile(r'\bp[!1]cs\b', re.I), 'pics'),
    (re.compile(r'\bd0xx\b', re.I), 'doxx'),
]

# Configurable slang & abbreviation dictionary
SLANG_MAPPINGS = [
    (re.compile(r'\bkys\b', re.I), 'kill yourself'),
    (re.compile(r'\bkms\b', re.I), 'kill myself'),
    (re.compile(r'\bu\b', re.I), 'you'),
    (re.compile(r'\bur\b', re.I), 'your'),
    (re.compile(r'\br\b', re.I), 'are'),
    (re.compile(r'\bpls\b', re.I), 'please'),
    (re.compile(r'\bplz\b', re.I), 'please'),
    (re.compile(r'\bwanna\b', re.I), 'want to'),
    (re.compile(r'\bgonna\b', re.I), 'going to'),
    (re.compile(r'\bgotta\b', re.I), 'got to'),
    (re.compile(r'\bidk\b', re.I), 'i do not know'),
    (re.compile(r'\btbh\b', re.I), 'to be honest'),
    (re.compile(r'\brn\b', re.I), 'right now'),
    (re.compile(r'\bomg\b', re.I), 'oh my god'),
    (re.compile(r'\bwth\b', re.I), 'what the hell'),
    (re.compile(r'\bwtf\b', re.I), 'what the fuck'),
    (re.compile(r'\bdm\b', re.I), 'direct message'),
    (re.compile(r'\bdms\b', re.I), 'direct messages'),
    (re.compile(r'\bsnap\b', re.I), 'snapchat'),
    (re.compile(r'\bpic\b', re.I), 'picture'),
    (re.compile(r'\bpics\b', re.I), 'pictures'),
    (re.compile(r'\bvid\b', re.I), 'video'),
    (re.compile(r'\bvids\b', re.I), 'videos'),
    (re.compile(r'\bbrb\b', re.I), 'be right back'),
    (re.compile(r'\bgtg\b', re.I), 'got to go'),
    (re.compile(r'\bg2g\b', re.I), 'got to go'),
    (re.compile(r'\basap\b', re.I), 'as soon as possible'),
    (re.compile(r'\bbc\b', re.I), 'because'),
    (re.compile(r'\bcuz\b', re.I), 'because'),
    (re.compile(r'\bcos\b', re.I), 'because'),
    (re.compile(r'\bw/\b', re.I), 'with'),
    (re.compile(r'\bw/o\b', re.I), 'without'),
    (re.compile(r'\bppl\b', re.I), 'people'),
    (re.compile(r'\btho\b', re.I), 'though'),
    (re.compile(r'\bfam\b', re.I), 'family'),
    (re.compile(r'\bmsg\b', re.I), 'message'),
    (re.compile(r'\bmsgs\b', re.I), 'messages'),
]


def normalize_text(text: str) -> str:
    """
    Standardized, safe text normalization used for both training and inference.
    
    Operations:
    1. Lowercases text while normalizing Unicode quotes and hyphens.
    2. Replaces URLs with a neutral token.
    3. Preserves meaningful emojis.
    4. Compresses elongated repeated characters (e.g. 'sooooo' -> 'soo', 'kiiiill' -> 'kill').
    5. Normalizes common leetspeak obfuscations (e.g. 'k!ll' -> 'kill').
    6. Expands common contractions and preserves negation (e.g. 'won't' -> 'will not').
    7. Expands common chat abbreviations (e.g. 'kys' -> 'kill yourself', 'u' -> 'you').
    8. Normalizes whitespace without aggressive stemming or semantic loss.
    """
    if not text or not isinstance(text, str):
        return ""
    
    text = text.lower().strip()
    
    # 1. Unicode quotes, dashes, and apostrophes
    text = text.replace('\u2019', "'").replace('\u2018', "'")
    text = text.replace('\u201c', '"').replace('\u201d', '"')
    text = text.replace('\u2013', '-').replace('\u2014', '-')
    
    # 2. URLs
    text = re.sub(r'https?://\S+', ' url ', text)
    text = re.sub(r'www\.\S+', ' url ', text)
    
    # 3. Preserve emojis
    emojis = EMOJI_PATTERN.findall(text)
    
    # 4. Collapse elongated repeated characters (3 or more down to 2)
    # E.g. 'sooooo' -> 'soo', 'stopppp' -> 'stopp', 'kiiiill' -> 'kill'
    text = re.sub(r'(.)\1{2,}', r'\1\1', text)
    
    # 5. Leetspeak / Obfuscation decoding
    for pattern, replacement in LEETSPEAK_MAPPINGS:
        text = pattern.sub(replacement, text)
    
    # 6. Contractions expansion (strictly preserves negation semantics)
    text = re.sub(r"won't", "will not", text)
    text = re.sub(r"can't", "cannot", text)
    text = re.sub(r"shan't", "shall not", text)
    text = re.sub(r"n't", " not", text)
    text = re.sub(r"'re", " are", text)
    text = re.sub(r"'s", " is", text)
    text = re.sub(r"'d", " would", text)
    text = re.sub(r"'ll", " will", text)
    text = re.sub(r"'ve", " have", text)
    text = re.sub(r"'m", " am", text)
    
    # 7. Common internet slang & abbreviations
    for pattern, replacement in SLANG_MAPPINGS:
        text = pattern.sub(replacement, text)
    
    # 8. Filter non-essential special chars but keep alphanumeric, basic punctuation, spaces
    text = re.sub(r"[^a-z0-9\s'.!?,]", ' ', text)
    
    # 9. Clean excessive spaces
    text = re.sub(r'\s+', ' ', text).strip()
    
    # 10. Re-append emojis if stripped by punctuation filter
    if emojis:
        emoji_str = ' '.join(emojis)
        # Avoid duplicating if already present in text
        for em in set(emojis):
            if em not in text:
                text = f"{text} {emoji_str}".strip()
                break
    
    return text


def clean_for_ml(text: str) -> str:
    """Backward-compatible wrapper for normalize_text."""
    return normalize_text(text)


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
    # Comprehensive synonym groups for augmentation
    synonym_groups = [
        ['ugly', 'hideous', 'gross', 'disgusting', 'repulsive', 'grotesque', 'vile'],
        ['stupid', 'dumb', 'idiotic', 'foolish', 'brainless', 'moron', 'clueless', 'imbecile'],
        ['hate', 'despise', 'detest', 'loathe', 'abhor'],
        ['hurt', 'harm', 'injure', 'attack', 'wound', 'assault', 'batter'],
        ['kill', 'destroy', 'eliminate', 'annihilate', 'murder', 'slaughter', 'end', 'execute'],
        ['strangle', 'choke', 'suffocate'],
        ['beat', 'bash', 'punch', 'hit', 'strike', 'pound', 'smash'],
        ['stab', 'slash', 'cut', 'slice', 'knife'],
        ['shoot', 'gun down', 'snipe'],
        ['stalk', 'track', 'follow', 'hunt down', 'watch'],
        ['friend', 'buddy', 'pal', 'mate', 'bro', 'dude'],
        ['happy', 'glad', 'joyful', 'pleased', 'cheerful'],
        ['sad', 'unhappy', 'miserable', 'depressed', 'down', 'hopeless'],
        ['scared', 'afraid', 'frightened', 'terrified', 'fearful'],
        ['secret', 'private', 'hidden', 'confidential', 'covert'],
        ['beautiful', 'pretty', 'gorgeous', 'stunning', 'attractive'],
        ['send', 'give', 'share', 'transfer', 'provide', 'leak'],
        ['photo', 'picture', 'pic', 'selfie', 'image', 'snapshot', 'nude'],
        ['money', 'cash', 'funds', 'payment', 'dollars'],
        ['everyone', 'everybody', 'all of them', 'the whole school'],
        ['nobody', 'no one', 'not a single person', 'none of them'],
        ['loser', 'freak', 'failure', 'outcast', 'waste of space', 'joke'],
        ['die', 'perish', 'disappear', 'cease to exist', 'drop dead'],
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
