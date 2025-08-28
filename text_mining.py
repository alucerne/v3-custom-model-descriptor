from typing import List, Dict, Any, Optional
import re
from collections import Counter, defaultdict

# --- lightweight filters & helpers ---
STOPWORDS = set("""
a an and are as at be by for from has have how i in is it its of on or that the to was were what when where which who why will with you your
""".split())

EXTRA_STOPS = set("""
about across after also because before can could does each find get good great help here into like make many may more most much new now off one our out over see show since some take than then there these thing things those through try under use used using very via way well while within without work year years
""".split())

# Enhanced stop words for better filtering
ENHANCED_STOPS = set("""
what when where why how which who whom whose
here there now then today yesterday tomorrow
very really quite rather just only even still also
too as like such so than more most less least
much many few several some any all every each
both either neither no not never always often sometimes
usually generally typically commonly frequently rarely seldom
get got getting make made making take took taking
give gave giving go went going come came coming
see saw seeing look looked looking find found finding
use used using want wanted wanting need needed needing
know knew knowing think thought thinking feel felt feeling
good bad big small large little new old young
high low long short wide narrow thick thin
easy hard difficult simple complex important necessary
possible impossible available unavailable ready ready
click clicked clicking page pages website web site
link links button buttons menu menus form forms
data information content text image images file files
download downloads upload uploads search searches searching
result results list lists item items product products
service services tool tools feature features option options
""".split())

BOILER = re.compile(r"(cookie|privacy|terms|subscribe|login|sign in|sign up|accept|advertis|newsletter)", re.I)

# intent modifier lexicons
TXN = ["pricing", "price", "cost", "quote", "buy", "near me", "tickets", "registration", "warranty"]
EVAL = ["reviews", "review", "vs", "compare", "alternatives", "best"]
IMPL = ["installation", "installer", "install", "replacement", "setup", "integration", "api", "docs", "specs", "materials"]
GENERIC = ["what is", "guide", "definition", "overview"]

# gotchya guard (audience/business-model words we don't want)
FORBIDDEN_DEFAULT = [
    "homeowner","homeowners","manager","owner","marketer","student","developer","cio","smb","enterprise",
    "middle aged","parents","men","women","luxury","affordable","budget","trusted","premium",
    "award-winning","top rated","quality","this intent","represents interest","captures research"
]

DOMAIN_BAN = {"this","home","water"}  # trivial junk for gutters/etc.; extend per vertical
BRAND_FIXES = {"leaffilter":"LeafFilter"}  # example brand normalizer

# Comprehensive stop/block phrases that don't add value to descriptions
BLOCK_PHRASES = {
    # Generic filler phrases
    "these services send your", "if you", "if you d", "you d like", "d like to", "like to",
    "need to", "want to", "going to", "trying to", "planning to", "looking to",
    "in the", "on the", "at the", "of the", "to the", "for the", "with the",
    "it s", "that s", "there s", "here s", "what s", "how s", "when s",
    "you re", "they re", "we re", "i m", "he s", "she s",
    
    # Common web content phrases
    "click here", "learn more", "read more", "find out", "get started",
    "sign up", "sign in", "log in", "create account", "join now",
    "subscribe to", "follow us", "contact us", "get in touch",
    
    # Generic marketing phrases
    "best in", "top rated", "award winning", "trusted by", "used by",
    "recommended by", "chosen by", "selected by", "featured in",
    
    # Common web navigation
    "home page", "main page", "about us", "our services", "our products",
    "customer support", "help center", "faq", "privacy policy", "terms of service",
    
    # Generic content phrases
    "in this article", "in this guide", "in this post", "in this blog",
    "as mentioned", "as stated", "as noted", "according to",
    "for example", "for instance", "such as", "like this",
    
    # Common web boilerplate
    "cookie policy", "privacy policy", "terms of use", "disclaimer",
    "copyright", "all rights reserved", "powered by", "built with",
    
    # Generic action phrases
    "take a look", "check out", "have a look", "give it a try",
    "start using", "begin using", "continue reading", "keep reading"
}


def _tokenize(txt: str) -> List[str]:
    """Basic tokenizer; no stopword removal here—handled later per ngram."""
    txt = BOILER.sub(" ", txt.lower())
    txt = re.sub(r"[^a-z0-9\- ]+", " ", txt)
    toks = [t for t in txt.split() if t]
    return toks


def _ngrams(tokens: List[str], n: int) -> List[str]:
    return [" ".join(tokens[i:i+n]) for i in range(len(tokens)-n+1)]


def _is_good_unigram(t: str) -> bool:
    # keep domainish unigrams; ditch tiny/generic/junk
    if t in STOPWORDS or t in EXTRA_STOPS or t in ENHANCED_STOPS or t in DOMAIN_BAN:
        return False
    return len(t) >= 4 and not t.isdigit()


def _clean_term(t: str) -> str:
    if t in BRAND_FIXES:
        return BRAND_FIXES[t]
    if len(t.split()) >= 2:
        # Title-case phrases lightly
        return " ".join(w if w.isupper() else w.capitalize() for w in t.split())
    return t


def _score_terms(docs: List[Dict[str, Any]]) -> Dict[str, int]:
    """Doc-frequency style term scoring with phrase preference."""
    seen = defaultdict(set)
    doc_idx = 0
    
    # Handle nested structure: docs is a list of {"query": str, "docs": List[Dict]}
    for block in docs:
        if isinstance(block, dict) and "docs" in block:
            # This is a SERP block with nested docs
            for d in block.get("docs", []):
                text = " ".join([
                    d.get("title", ""),
                    d.get("snippet", ""),
                    d.get("text", "")
                ])
                toks = _tokenize(text)

                # build n-grams with stopword filtering for phrases
                unis = [t for t in toks if _is_good_unigram(t)]
                filtered = [t for t in toks if t not in STOPWORDS and t not in EXTRA_STOPS and t not in ENHANCED_STOPS]
                bis = _ngrams(filtered, 2)
                tris = _ngrams(filtered, 3)

                # use sets per doc to avoid overcounting duplicates in same page
                for ng in set(unis + bis + tris):
                    seen[ng].add(doc_idx)
                doc_idx += 1
        else:
            # This is a flat list of docs
            d = block
            text = " ".join([
                d.get("title", ""),
                d.get("snippet", ""),
                d.get("text", "")
            ])
            toks = _tokenize(text)

            # build n-grams with stopword filtering for phrases
            unis = [t for t in toks if _is_good_unigram(t)]
            filtered = [t for t in toks if t not in STOPWORDS and t not in EXTRA_STOPS and t not in ENHANCED_STOPS]
            bis = _ngrams(filtered, 2)
            tris = _ngrams(filtered, 3)

            # use sets per doc to avoid overcounting duplicates in same page
            for ng in set(unis + bis + tris):
                seen[ng].add(doc_idx)
            doc_idx += 1

    # convert to counts with higher bar for unigrams
    scores: Dict[str, int] = {}
    for term, idxs in seen.items():
        df = len(idxs)
        wc = len(term.split())
        min_df = 4 if wc == 1 else 2
        if df >= min_df:
            scores[term] = df
    return scores


def build_keyword_bank(docs: List[Dict[str, Any]], seeds: Optional[List[str]] = None) -> Dict[str, Any]:
    scores = _score_terms(docs)
    # sort by support
    items = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)

    # prefer phrases over unigrams
    phrases = [(_clean_term(t), s) for t, s in items if len(t.split()) in (2, 3)]
    unis    = [(_clean_term(t), s) for t, s in items if len(t.split()) == 1]

    exact_terms = [t for t, _ in phrases][:15]
    # fallback to a few decent unigrams if not enough phrases
    if len(exact_terms) < 8:
        exact_terms.extend([t for t, _ in unis if _is_good_unigram(t)][: (8 - len(exact_terms))])

    # semantic terms: extra phrases not already used
    semantic_terms = [t for t, _ in phrases if t not in exact_terms][:12]

    # action modifiers — keep order TXN > EVAL > IMPL > GENERIC
    present = {m for m in scores.keys()}
    ordered_mods: List[str] = []
    for group in (TXN, EVAL, IMPL, GENERIC):
        for m in group:
            if m in present and m not in ordered_mods:
                ordered_mods.append(m)
    action_modifiers = ordered_mods[:8]

    # disambiguators: top phrases or seed heads
    disambiguators: List[str] = []
    if exact_terms:
        disambiguators.extend(exact_terms[:2])
    if seeds:
        for s in seeds[:2]:
            if s not in disambiguators:
                disambiguators.append(s)
    disambiguators = disambiguators[:3]

    # stop terms from gotchyas
    stop_terms = sorted(list(set(FORBIDDEN_DEFAULT)))

    # top domains for debug/QA
    domains = [d.get("domain", "") for d in docs if d.get("domain")]
    top_domains = [dom for dom, _ in Counter(domains).most_common(10)]

    return {
        "exact_terms": exact_terms,
        "semantic_terms": semantic_terms,
        "action_modifiers": action_modifiers,
        "disambiguators": disambiguators,
        "stop_terms": stop_terms,
        "top_domains": top_domains,
        "evidence_count": len(docs),
    }


def extract_raw_content(docs: List[Dict[str, Any]], seeds: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Extract maximum raw content from SERP pages with minimal filtering.
    This provides rich semantic content for Phase 2 LLM processing.
    """
    raw_texts = []
    all_terms = []
    doc_sources = []
    
    # Handle nested structure: docs is a list of {"query": str, "docs": List[Dict]}
    for block in docs:
        if isinstance(block, dict) and "docs" in block:
            # This is a SERP block with nested docs
            for d in block.get("docs", []):
                # Extract all available text content
                title = d.get("title", "")
                snippet = d.get("snippet", "")
                maintext = d.get("maintext", "")
                domain = d.get("domain", "")
                link = d.get("link", "")
                
                # Combine all text content
                full_text = " ".join([title, snippet, maintext])
                raw_texts.append(full_text)
                
                # Extract all terms (minimal filtering)
                toks = _tokenize(full_text)
                # Enhanced filtering for better quality terms
                filtered_toks = [t for t in toks if len(t) >= 3 and t not in DOMAIN_BAN and t not in ENHANCED_STOPS]
                all_terms.extend(filtered_toks)
                
                doc_sources.append({
                    "title": title,
                    "snippet": snippet,
                    "domain": domain,
                    "link": link,
                    "text_length": len(full_text)
                })
        else:
            # This is a flat list of docs
            d = block
            title = d.get("title", "")
            snippet = d.get("snippet", "")
            maintext = d.get("maintext", "")
            domain = d.get("domain", "")
            link = d.get("link", "")
            
            full_text = " ".join([title, snippet, maintext])
            raw_texts.append(full_text)
            
            toks = _tokenize(full_text)
            # Enhanced filtering for better quality terms
            filtered_toks = [t for t in toks if len(t) >= 3 and t not in DOMAIN_BAN and t not in ENHANCED_STOPS]
            all_terms.extend(filtered_toks)
            
            doc_sources.append({
                "title": title,
                "snippet": snippet,
                "domain": domain,
                "link": link,
                "text_length": len(full_text)
            })
    
    # Get term frequencies with enhanced filtering
    term_counts = Counter(all_terms)
    
    # Filter out stop words from top terms
    filtered_terms = []
    for term, count in term_counts.most_common(100):
        if (term not in STOPWORDS and 
            term not in EXTRA_STOPS and 
            term not in ENHANCED_STOPS and
            len(term) >= 3 and
            not term.isdigit()):
            filtered_terms.append(term)
            if len(filtered_terms) >= 50:
                break
    
    top_terms = filtered_terms
    
    # Extract key phrases (bigrams and trigrams)
    all_phrases = []
    for text in raw_texts:
        toks = _tokenize(text)
        # Get all bigrams and trigrams
        bigrams = _ngrams(toks, 2)
        trigrams = _ngrams(toks, 3)
        all_phrases.extend(bigrams)
        all_phrases.extend(trigrams)
    
    phrase_counts = Counter(all_phrases)
    
    # Filter out blocked phrases
    filtered_phrases = []
    for phrase, count in phrase_counts.most_common(50):
        # Check if phrase contains any blocked phrases
        should_block = False
        for blocked in BLOCK_PHRASES:
            if blocked in phrase.lower():
                should_block = True
                break
        
        if not should_block:
            filtered_phrases.append((phrase, count))
    
    top_phrases = [phrase for phrase, count in filtered_phrases[:30]]
    
    # Combine all content
    combined_text = " ".join(raw_texts)
    
    return {
        "raw_texts": raw_texts,
        "combined_text": combined_text,
        "top_terms": top_terms,
        "top_phrases": top_phrases,
        "term_frequencies": dict(term_counts.most_common(100)),
        "phrase_frequencies": dict(filtered_phrases[:50]),
        "doc_sources": doc_sources,
        "total_docs": len(doc_sources),
        "total_text_length": len(combined_text),
        "seeds": seeds or [],
        "evidence_count": len(doc_sources),
    }


def enrich_with_keyphrases(snippets: str, bank: dict, top_n: int = 15) -> dict:
    """
    Enrich keyword bank with extracted keyphrases using the keyword extractor.
    """
    try:
        from keyword_extractor import extract_keyphrases
        phrases = extract_keyphrases(snippets, top_n=top_n)
        # Prefer to put into semantic_terms so the writer can use them
        sem = bank.get("semantic_terms", [])
        exact = bank.get("exact_terms", [])
        # merge, dedupe, cap
        merged_sem = list(dict.fromkeys(phrases + sem))[:max(10, top_n)]
        bank["semantic_terms"] = merged_sem
        return bank
    except ImportError:
        # If keyword_extractor is not available, return bank unchanged
        return bank
    except Exception as e:
        print(f"Error in keyword extraction: {e}")
        return bank
