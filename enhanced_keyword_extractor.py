# enhanced_keyword_extractor.py
# Enhanced keyword extraction focusing on meaningful, domain-specific terms
# Combines statistical, semantic, and domain-specific approaches

import re
from collections import Counter, defaultdict
from typing import List, Dict, Set, Tuple
import spacy
from textblob import TextBlob

# Enhanced stop words - more comprehensive
ENHANCED_STOP_WORDS = {
    # Basic stop words
    'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
    'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
    'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those',
    'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them',
    'my', 'your', 'his', 'her', 'its', 'our', 'their', 'mine', 'yours', 'hers', 'ours', 'theirs',
    
    # Additional common words that don't add value
    'what', 'when', 'where', 'why', 'how', 'which', 'who', 'whom', 'whose',
    'here', 'there', 'now', 'then', 'today', 'yesterday', 'tomorrow',
    'very', 'really', 'quite', 'rather', 'just', 'only', 'even', 'still', 'also',
    'too', 'as', 'like', 'such', 'so', 'than', 'more', 'most', 'less', 'least',
    'much', 'many', 'few', 'several', 'some', 'any', 'all', 'every', 'each',
    'both', 'either', 'neither', 'no', 'not', 'never', 'always', 'often', 'sometimes',
    'usually', 'generally', 'typically', 'commonly', 'frequently', 'rarely', 'seldom',
    
    # Generic action words
    'get', 'got', 'getting', 'make', 'made', 'making', 'take', 'took', 'taking',
    'give', 'gave', 'giving', 'go', 'went', 'going', 'come', 'came', 'coming',
    'see', 'saw', 'seeing', 'look', 'looked', 'looking', 'find', 'found', 'finding',
    'use', 'used', 'using', 'want', 'wanted', 'wanting', 'need', 'needed', 'needing',
    'know', 'knew', 'knowing', 'think', 'thought', 'thinking', 'feel', 'felt', 'feeling',
    
    # Generic descriptive words
    'good', 'bad', 'big', 'small', 'large', 'little', 'new', 'old', 'young',
    'high', 'low', 'long', 'short', 'wide', 'narrow', 'thick', 'thin',
    'easy', 'hard', 'difficult', 'simple', 'complex', 'important', 'necessary',
    'possible', 'impossible', 'available', 'unavailable', 'ready', 'ready',
    
    # Web/tech generic terms
    'click', 'clicked', 'clicking', 'page', 'pages', 'website', 'web', 'site',
    'link', 'links', 'button', 'buttons', 'menu', 'menus', 'form', 'forms',
    'data', 'information', 'content', 'text', 'image', 'images', 'file', 'files',
    'download', 'downloads', 'upload', 'uploads', 'search', 'searches', 'searching',
    'result', 'results', 'list', 'lists', 'item', 'items', 'product', 'products',
    'service', 'services', 'tool', 'tools', 'feature', 'features', 'option', 'options'
}

# Domain-specific meaningful patterns for email deliverability
EMAIL_DELIVERABILITY_PATTERNS = [
    # Core concepts
    r'\b(?:email|mail)\s+(?:deliverability|delivery|inbox|spam|reputation)\b',
    r'\b(?:sender|domain|ip)\s+(?:reputation|authentication|verification)\b',
    r'\b(?:spf|dkim|dmarc|authentication|verification)\b',
    r'\b(?:inbox|spam|folder|placement|delivery)\s+(?:rate|score|test)\b',
    r'\b(?:email|mail)\s+(?:service|provider|tool|platform)\b',
    r'\b(?:cold|bulk|mass)\s+(?:email|mail)\b',
    r'\b(?:email|mail)\s+(?:campaign|marketing|automation)\b',
    
    # Technical terms
    r'\b(?:bounce|bounced|bouncing)\s+(?:rate|rates|email|emails)\b',
    r'\b(?:open|opened|opening)\s+(?:rate|rates|email|emails)\b',
    r'\b(?:click|clicked|clicking)\s+(?:rate|rates|through|throughs)\b',
    r'\b(?:unsubscribe|unsubscribed|unsubscribing)\s+(?:rate|rates)\b',
    r'\b(?:spam|junk)\s+(?:filter|filters|folder|folders)\b',
    r'\b(?:blacklist|whitelist|greylist)\b',
    r'\b(?:mailbox|mailboxes)\s+(?:provider|providers)\b',
    r'\b(?:postmaster|postmasters)\s+(?:tool|tools)\b',
    
    # Authentication and security
    r'\b(?:authentication|authenticated|authenticating)\s+(?:protocol|protocols)\b',
    r'\b(?:verification|verified|verifying)\s+(?:process|processes)\b',
    r'\b(?:encryption|encrypted|encrypting)\s+(?:email|emails)\b',
    r'\b(?:ssl|tls)\s+(?:certificate|certificates)\b',
    
    # Metrics and monitoring
    r'\b(?:delivery|delivered|delivering)\s+(?:rate|rates|status)\b',
    r'\b(?:reputation|reputations)\s+(?:score|scores|monitoring)\b',
    r'\b(?:engagement|engaged|engaging)\s+(?:rate|rates|metrics)\b',
    r'\b(?:performance|performing)\s+(?:metrics|monitoring)\b'
]

# Generic meaningful patterns for any domain
GENERIC_MEANINGFUL_PATTERNS = [
    # Technical/Professional terms
    r'\b(?:api|apis)\s+(?:integration|integrations|endpoint|endpoints)\b',
    r'\b(?:software|application|app|platform)\s+(?:solution|solutions)\b',
    r'\b(?:cloud|saas|software)\s+(?:service|services)\b',
    r'\b(?:database|databases)\s+(?:management|system|systems)\b',
    r'\b(?:security|secure|securing)\s+(?:feature|features|protocol|protocols)\b',
    
    # Business/Professional terms
    r'\b(?:enterprise|business|corporate)\s+(?:solution|solutions|service|services)\b',
    r'\b(?:professional|pro|premium)\s+(?:version|versions|plan|plans)\b',
    r'\b(?:customer|customers)\s+(?:support|service|services)\b',
    r'\b(?:pricing|price|cost)\s+(?:plan|plans|model|models)\b',
    
    # Technical features
    r'\b(?:real-time|realtime)\s+(?:monitoring|tracking|updates)\b',
    r'\b(?:automated|automatic|automation)\s+(?:process|processes|workflow|workflows)\b',
    r'\b(?:advanced|advanced)\s+(?:feature|features|capability|capabilities)\b',
    r'\b(?:integrated|integration)\s+(?:system|systems|platform|platforms)\b'
]

# Low-value phrases to filter out
LOW_VALUE_PHRASES = {
    # Generic web content
    "click here", "learn more", "read more", "find out", "get started",
    "sign up", "sign in", "log in", "create account", "join now",
    "subscribe to", "follow us", "contact us", "get in touch",
    
    # Generic marketing
    "best in", "top rated", "award winning", "trusted by", "used by",
    "recommended by", "chosen by", "selected by", "featured in",
    
    # Generic navigation
    "home page", "main page", "about us", "our services", "our products",
    "customer support", "help center", "faq", "privacy policy", "terms of service",
    
    # Generic content
    "in this article", "in this guide", "in this post", "in this blog",
    "as mentioned", "as stated", "as noted", "according to",
    "for example", "for instance", "such as", "like this",
    
    # Generic actions
    "take a look", "check out", "have a look", "give it a try",
    "start using", "begin using", "continue reading", "keep reading"
}

def extract_enhanced_keyphrases(text: str, domain: str = "general", top_n: int = 15) -> List[str]:
    """
    Extract meaningful keyphrases using enhanced filtering and domain-specific patterns.
    """
    if not text:
        return []
    
    # Clean text
    text = re.sub(r'[^\w\s]', ' ', text.lower())
    
    # Extract domain-specific phrases first
    domain_phrases = _extract_domain_phrases(text, domain)
    
    # Extract meaningful n-grams
    meaningful_ngrams = _extract_meaningful_ngrams(text)
    
    # Extract technical terms and proper nouns
    technical_terms = _extract_technical_terms(text)
    
    # Combine and score
    all_candidates = domain_phrases + meaningful_ngrams + technical_terms
    scored_phrases = _score_phrases(all_candidates, text)
    
    # Filter and return top results
    filtered_phrases = _filter_quality_phrases(scored_phrases)
    
    return filtered_phrases[:top_n]

def _extract_domain_phrases(text: str, domain: str) -> List[str]:
    """Extract domain-specific phrases using patterns."""
    patterns = EMAIL_DELIVERABILITY_PATTERNS if domain == "email_deliverability" else GENERIC_MEANINGFUL_PATTERNS
    
    phrases = []
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        phrases.extend(matches)
    
    return list(set(phrases))

def _extract_meaningful_ngrams(text: str) -> List[str]:
    """Extract meaningful n-grams with enhanced filtering."""
    words = text.split()
    
    # Filter out stop words
    filtered_words = [w for w in words if w not in ENHANCED_STOP_WORDS and len(w) > 2]
    
    # Extract bigrams and trigrams
    bigrams = [' '.join(filtered_words[i:i+2]) for i in range(len(filtered_words)-1)]
    trigrams = [' '.join(filtered_words[i:i+3]) for i in range(len(filtered_words)-2)]
    
    # Filter out low-value phrases
    meaningful_ngrams = []
    for phrase in bigrams + trigrams:
        if not _is_low_value_phrase(phrase):
            meaningful_ngrams.append(phrase)
    
    return meaningful_ngrams

def _extract_technical_terms(text: str) -> List[str]:
    """Extract technical terms, proper nouns, and domain-specific words."""
    try:
        # Use TextBlob for POS tagging (lighter than spaCy)
        blob = TextBlob(text)
        technical_terms = []
        
        for word, tag in blob.tags:
            # Keep proper nouns, technical terms, and domain-specific words
            if (tag.startswith('NNP') or  # Proper nouns
                tag.startswith('NN') and len(word) > 4 or  # Long nouns
                _is_technical_word(word)):  # Technical terms
                technical_terms.append(word)
        
        return technical_terms
    except:
        # Fallback: extract words that look technical
        words = text.split()
        return [w for w in words if _is_technical_word(w)]

def _is_technical_word(word: str) -> bool:
    """Check if a word looks technical."""
    # Technical word patterns
    tech_patterns = [
        r'^[A-Z]{2,}$',  # Acronyms
        r'.*api$',  # API-related
        r'.*sdk$',  # SDK-related
        r'.*ssl$',  # SSL-related
        r'.*tls$',  # TLS-related
        r'.*http$',  # HTTP-related
        r'.*json$',  # JSON-related
        r'.*xml$',   # XML-related
        r'.*sql$',   # SQL-related
        r'.*auth$',  # Auth-related
        r'.*encrypt$',  # Encryption-related
        r'.*secure$',   # Security-related
        r'.*integrat$', # Integration-related
        r'.*automation$', # Automation-related
        r'.*monitoring$', # Monitoring-related
        r'.*analytics$',  # Analytics-related
        r'.*dashboard$',  # Dashboard-related
        r'.*reporting$',  # Reporting-related
    ]
    
    for pattern in tech_patterns:
        if re.match(pattern, word.lower()):
            return True
    
    return False

def _is_low_value_phrase(phrase: str) -> bool:
    """Check if a phrase is low value."""
    phrase_lower = phrase.lower()
    
    # Check against low-value phrases
    for low_value in LOW_VALUE_PHRASES:
        if low_value in phrase_lower:
            return True
    
    # Check if phrase is too generic
    generic_words = {'thing', 'things', 'stuff', 'way', 'ways', 'time', 'times', 'place', 'places'}
    words = phrase_lower.split()
    if len(words) == 1 and words[0] in generic_words:
        return True
    
    return False

def _score_phrases(phrases: List[str], text: str) -> List[Tuple[str, float]]:
    """Score phrases based on frequency and meaningfulness."""
    # Count frequencies
    phrase_counts = Counter(phrases)
    
    scored = []
    for phrase, count in phrase_counts.items():
        if count < 2:  # Must appear at least twice
            continue
        
        # Base score is frequency
        score = count
        
        # Bonus for domain-specific patterns
        if any(re.search(pattern, phrase, re.IGNORECASE) for pattern in EMAIL_DELIVERABILITY_PATTERNS):
            score *= 2.0
        
        # Bonus for technical terms
        if _is_technical_word(phrase):
            score *= 1.5
        
        # Bonus for longer phrases (more specific)
        word_count = len(phrase.split())
        if word_count >= 3:
            score *= 1.3
        elif word_count == 2:
            score *= 1.1
        
        scored.append((phrase, score))
    
    return sorted(scored, key=lambda x: x[1], reverse=True)

def _filter_quality_phrases(scored_phrases: List[Tuple[str, float]]) -> List[str]:
    """Filter to only high-quality phrases."""
    quality_phrases = []
    
    for phrase, score in scored_phrases:
        # Must have minimum score
        if score < 2.0:
            continue
        
        # Must not be too short or too long
        if len(phrase) < 3 or len(phrase) > 50:
            continue
        
        # Must contain meaningful words
        words = phrase.split()
        meaningful_words = [w for w in words if w not in ENHANCED_STOP_WORDS and len(w) > 2]
        if len(meaningful_words) == 0:
            continue
        
        quality_phrases.append(phrase)
    
    return quality_phrases

if __name__ == "__main__":
    # Test with email deliverability content
    test_text = """
    Email deliverability is crucial for inbox placement. Sender reputation affects whether emails reach the inbox or spam folder.
    SPF, DKIM, and DMARC authentication improve email deliverability rates. Cold email services need proper authentication to avoid spam filters.
    Bounce rates and open rates are key metrics for email deliverability monitoring. Mailbox providers like Gmail and Outlook use sophisticated filtering.
    """
    
    phrases = extract_enhanced_keyphrases(test_text, domain="email_deliverability")
    print("Enhanced extracted phrases:", phrases)
