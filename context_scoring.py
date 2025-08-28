# context_scoring.py
# Context-aware scoring system for keywords based on text position and importance
# Weights keywords differently based on where they appear (title, snippet, main text)

from typing import List, Dict, Tuple, Any
from collections import defaultdict
import re

# Context weights - higher weights for more important positions
CONTEXT_WEIGHTS = {
    "title": 3.0,        # Highest weight - titles are most important
    "snippet": 2.0,      # Medium weight - snippets are descriptive
    "maintext": 1.0,     # Base weight - main text provides context
    "url": 1.5,          # Medium-high weight - URLs can contain keywords
    "domain": 0.5        # Lower weight - domains are less specific
}

# Position within text weights
POSITION_WEIGHTS = {
    "beginning": 1.2,    # Slightly higher weight for beginning
    "middle": 1.0,       # Base weight for middle
    "end": 1.1          # Slightly higher weight for end
}

# Text length thresholds for position scoring
LENGTH_THRESHOLDS = {
    "short": 100,    # Short text
    "medium": 500,   # Medium text
    "long": 1000     # Long text
}

def calculate_context_score(keyword: str, text_type: str, position: str = "middle", 
                          text_length: int = 0) -> float:
    """
    Calculate context score for a keyword based on where it appears.
    """
    # Base context weight
    base_weight = CONTEXT_WEIGHTS.get(text_type, 1.0)
    
    # Position weight
    position_weight = POSITION_WEIGHTS.get(position, 1.0)
    
    # Length adjustment (longer texts get slightly higher scores for main content)
    length_adjustment = 1.0
    if text_type == "maintext":
        if text_length > LENGTH_THRESHOLDS["long"]:
            length_adjustment = 1.1
        elif text_length > LENGTH_THRESHOLDS["medium"]:
            length_adjustment = 1.05
    
    # Keyword length bonus (longer keywords are more specific)
    keyword_length_bonus = min(len(keyword.split()) * 0.1, 0.5)
    
    return base_weight * position_weight * length_adjustment * (1 + keyword_length_bonus)

def extract_keywords_with_context(docs: List[Dict[str, Any]]) -> Dict[str, List[Tuple[str, float]]]:
    """
    Extract keywords with context-aware scoring from document structure.
    """
    keyword_scores = defaultdict(list)
    
    for doc in docs:
        # Extract from title
        title = doc.get("title", "")
        if title:
            title_keywords = _extract_keywords_from_text(title)
            for keyword in title_keywords:
                score = calculate_context_score(keyword, "title", "beginning", len(title))
                keyword_scores[keyword].append(("title", score))
        
        # Extract from snippet
        snippet = doc.get("snippet", "")
        if snippet:
            snippet_keywords = _extract_keywords_from_text(snippet)
            for keyword in snippet_keywords:
                score = calculate_context_score(keyword, "snippet", "middle", len(snippet))
                keyword_scores[keyword].append(("snippet", score))
        
        # Extract from main text
        maintext = doc.get("maintext", "") or doc.get("text", "")
        if maintext:
            maintext_keywords = _extract_keywords_from_text(maintext)
            for keyword in maintext_keywords:
                # Determine position in main text
                position = _determine_position_in_text(keyword, maintext)
                score = calculate_context_score(keyword, "maintext", position, len(maintext))
                keyword_scores[keyword].append(("maintext", score))
        
        # Extract from URL
        url = doc.get("link", "")
        if url:
            url_keywords = _extract_keywords_from_url(url)
            for keyword in url_keywords:
                score = calculate_context_score(keyword, "url", "middle", len(url))
                keyword_scores[keyword].append(("url", score))
        
        # Extract from domain
        domain = doc.get("domain", "")
        if domain:
            domain_keywords = _extract_keywords_from_domain(domain)
            for keyword in domain_keywords:
                score = calculate_context_score(keyword, "domain", "middle", len(domain))
                keyword_scores[keyword].append(("domain", score))
    
    return dict(keyword_scores)

def _extract_keywords_from_text(text: str) -> List[str]:
    """
    Extract meaningful keywords from text.
    """
    if not text:
        return []
    
    # Clean text
    text = re.sub(r'[^\w\s]', ' ', text.lower())
    words = text.split()
    
    # Filter out stop words and short words
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
                  'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
                  'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those',
                  'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'}
    
    # Extract meaningful words
    meaningful_words = [w for w in words if w not in stop_words and len(w) >= 3]
    
    # Extract bigrams and trigrams
    keywords = []
    keywords.extend(meaningful_words)
    
    # Add bigrams
    for i in range(len(meaningful_words) - 1):
        bigram = f"{meaningful_words[i]} {meaningful_words[i+1]}"
        keywords.append(bigram)
    
    # Add trigrams
    for i in range(len(meaningful_words) - 2):
        trigram = f"{meaningful_words[i]} {meaningful_words[i+1]} {meaningful_words[i+2]}"
        keywords.append(trigram)
    
    return keywords

def _extract_keywords_from_url(url: str) -> List[str]:
    """
    Extract keywords from URL path and query parameters.
    """
    if not url:
        return []
    
    # Extract path and query parameters
    try:
        from urllib.parse import urlparse, parse_qs
        parsed = urlparse(url)
        
        keywords = []
        
        # Extract from path
        path_parts = parsed.path.strip('/').split('/')
        keywords.extend([part for part in path_parts if len(part) >= 3])
        
        # Extract from query parameters
        query_params = parse_qs(parsed.query)
        for param_name, param_values in query_params.items():
            if len(param_name) >= 3:
                keywords.append(param_name)
            for value in param_values:
                if len(value) >= 3:
                    keywords.append(value)
        
        return keywords
    except:
        # Fallback: simple extraction
        url_clean = re.sub(r'[^\w\s]', ' ', url.lower())
        words = url_clean.split()
        return [w for w in words if len(w) >= 3]

def _extract_keywords_from_domain(domain: str) -> List[str]:
    """
    Extract meaningful keywords from domain name.
    """
    if not domain:
        return []
    
    # Remove common TLDs and subdomains
    domain_clean = re.sub(r'^www\.', '', domain.lower())
    domain_clean = re.sub(r'\.[a-z]{2,}$', '', domain_clean)  # Remove TLD
    
    # Split by dots and hyphens
    parts = re.split(r'[.-]', domain_clean)
    
    # Return meaningful parts
    return [part for part in parts if len(part) >= 3]

def _determine_position_in_text(keyword: str, text: str) -> str:
    """
    Determine the position of a keyword within text.
    """
    if not text or not keyword:
        return "middle"
    
    text_lower = text.lower()
    keyword_lower = keyword.lower()
    
    # Find all occurrences
    start_positions = []
    start = 0
    while True:
        pos = text_lower.find(keyword_lower, start)
        if pos == -1:
            break
        start_positions.append(pos)
        start = pos + 1
    
    if not start_positions:
        return "middle"
    
    # Use the first occurrence for position determination
    first_pos = start_positions[0]
    text_length = len(text)
    
    if first_pos < text_length * 0.3:
        return "beginning"
    elif first_pos > text_length * 0.7:
        return "end"
    else:
        return "middle"

def aggregate_keyword_scores(keyword_scores: Dict[str, List[Tuple[str, float]]]) -> Dict[str, float]:
    """
    Aggregate multiple scores for the same keyword.
    """
    aggregated = {}
    
    for keyword, scores in keyword_scores.items():
        if not scores:
            continue
        
        # Sum all scores for this keyword
        total_score = sum(score for _, score in scores)
        
        # Bonus for appearing in multiple contexts
        context_bonus = min(len(scores) * 0.2, 1.0)
        
        # Final score
        final_score = total_score * (1 + context_bonus)
        aggregated[keyword] = final_score
    
    return aggregated

def get_top_keywords_with_context(docs: List[Dict[str, Any]], top_n: int = 20) -> List[Tuple[str, float, Dict[str, int]]]:
    """
    Get top keywords with context-aware scoring and context breakdown.
    """
    # Extract keywords with context scores
    keyword_scores = extract_keywords_with_context(docs)
    
    # Aggregate scores
    aggregated_scores = aggregate_keyword_scores(keyword_scores)
    
    # Get context breakdown for each keyword
    context_breakdown = {}
    for keyword, scores in keyword_scores.items():
        context_counts = defaultdict(int)
        for context, _ in scores:
            context_counts[context] += 1
        context_breakdown[keyword] = dict(context_counts)
    
    # Sort by score and return top results
    sorted_keywords = sorted(aggregated_scores.items(), key=lambda x: x[1], reverse=True)
    
    results = []
    for keyword, score in sorted_keywords[:top_n]:
        breakdown = context_breakdown.get(keyword, {})
        results.append((keyword, score, breakdown))
    
    return results

if __name__ == "__main__":
    # Test with sample documents
    test_docs = [
        {
            "title": "Email Deliverability Best Practices",
            "snippet": "Learn how to improve email deliverability and avoid spam filters",
            "maintext": "Email deliverability is crucial for successful email marketing campaigns. This guide covers SPF, DKIM, and DMARC authentication protocols that help improve deliverability rates.",
            "link": "https://example.com/email-deliverability-guide",
            "domain": "example.com"
        }
    ]
    
    top_keywords = get_top_keywords_with_context(test_docs, top_n=10)
    
    print("Top keywords with context scoring:")
    for keyword, score, breakdown in top_keywords:
        print(f"{keyword}: {score:.2f} {breakdown}")
