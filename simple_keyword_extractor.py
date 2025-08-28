# simple_keyword_extractor.py
# Lightweight keyword extraction without heavy ML dependencies
# Uses TF-IDF, POS tagging, and simple heuristics

import re
from collections import Counter
from typing import List, Set

# Simple stop words
STOP_WORDS = {
    'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
    'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
    'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those',
    'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them',
    'my', 'your', 'his', 'her', 'its', 'our', 'their', 'mine', 'yours', 'hers', 'ours', 'theirs'
}

# Domain-specific patterns for email deliverability
DOMAIN_PATTERNS = [
    r'\b(?:email|mail)\s+(?:deliverability|delivery|inbox|spam|reputation)\b',
    r'\b(?:sender|domain|ip)\s+(?:reputation|authentication|verification)\b',
    r'\b(?:spf|dkim|dmarc|authentication|verification)\b',
    r'\b(?:inbox|spam|folder|placement|delivery)\s+(?:rate|score|test)\b',
    r'\b(?:email|mail)\s+(?:service|provider|tool|platform)\b',
    r'\b(?:cold|bulk|mass)\s+(?:email|mail)\b',
    r'\b(?:email|mail)\s+(?:campaign|marketing|automation)\b'
]

def extract_simple_keyphrases(text: str, top_n: int = 15) -> List[str]:
    """
    Extract keyphrases using simple NLP techniques without heavy dependencies.
    """
    if not text:
        return []
    
    # Clean and normalize text
    text = re.sub(r'[^\w\s]', ' ', text.lower())
    words = text.split()
    
    # Remove stop words and short words
    filtered_words = [w for w in words if w not in STOP_WORDS and len(w) > 2]
    
    # Extract bigrams and trigrams
    bigrams = [' '.join(filtered_words[i:i+2]) for i in range(len(filtered_words)-1)]
    trigrams = [' '.join(filtered_words[i:i+3]) for i in range(len(filtered_words)-2)]
    
    # Find domain-specific phrases
    domain_phrases = []
    for pattern in DOMAIN_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        domain_phrases.extend(matches)
    
    # Count frequencies
    all_phrases = filtered_words + bigrams + trigrams + domain_phrases
    phrase_counts = Counter(all_phrases)
    
    # Filter out low-quality phrases
    quality_phrases = []
    for phrase, count in phrase_counts.most_common(top_n * 2):
        if _is_quality_phrase(phrase, count):
            quality_phrases.append(phrase)
            if len(quality_phrases) >= top_n:
                break
    
    return quality_phrases

def _is_quality_phrase(phrase: str, count: int) -> bool:
    """Check if a phrase is high quality."""
    # Must appear at least twice
    if count < 2:
        return False
    
    # Must not be too short or too long
    if len(phrase) < 3 or len(phrase) > 50:
        return False
    
    # Must contain at least one meaningful word
    words = phrase.split()
    meaningful_words = [w for w in words if w not in STOP_WORDS and len(w) > 2]
    if len(meaningful_words) == 0:
        return False
    
    return True

if __name__ == "__main__":
    # Test the simple extractor
    test_text = """
    Email deliverability is crucial for inbox placement. 
    Sender reputation affects whether emails reach the inbox or spam folder.
    SPF, DKIM, and DMARC authentication improve email deliverability rates.
    Cold email services need proper authentication to avoid spam filters.
    """
    
    phrases = extract_simple_keyphrases(test_text)
    print("Extracted phrases:", phrases)
