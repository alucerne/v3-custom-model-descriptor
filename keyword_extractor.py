# keyword_extractor.py
# Extracts the most important keywords/keyphrases from raw text.
# Hybrid approach: spaCy noun chunks + KeyBERT (embeddings) + YAKE (statistics)
# with a small domain allowlist and brand whitelist.

from typing import List, Set
import re

# Deps:
# pip install keybert sentence-transformers yake nltk
from keybert import KeyBERT
from sentence_transformers import SentenceTransformer
import yake
import nltk
from nltk import pos_tag, word_tokenize
from nltk.chunk import ne_chunk

# --- Models (load lazily) ---
_embedder = None
_kw = None
_yake = None

def _get_nlp():
    # Use NLTK instead of spaCy
    try:
        nltk.download('punkt', quiet=True)
        nltk.download('averaged_perceptron_tagger', quiet=True)
        nltk.download('maxent_ne_chunker', quiet=True)
        nltk.download('words', quiet=True)
        return True
    except Exception as e:
        print(f"NLTK initialization failed: {e}")
        return False

def _get_kw():
    global _embedder, _kw
    if _kw is None:
        _embedder = SentenceTransformer("all-MiniLM-L6-v2")
        _kw = KeyBERT(model=_embedder)
    return _kw

def _get_yake():
    global _yake
    if _yake is None:
        _yake = yake.KeywordExtractor(lan="en", n=2, top=12, dedupLim=0.9, features=None)
    return _yake

# --- Domain filters: adjust to your vertical ---
ALLOWLIST_PAT = re.compile(
    r"(inbox placement|seed list( testing)?|spam score( analysis)?|authentication checks?|"
    r"sender reputation|postmaster|google postmaster tools?|mailbox providers?|"
    r"primary inbox|promotions tab|spam folder|deliverability|ip reputation|domain reputation)",
    re.IGNORECASE
)

BRAND_WHITELIST = {
    # deliverability examples
    "glockapps", "unspam", "folderly", "mailmeteor",
    "gmail", "outlook", "yahoo"
}

BLOCKLIST = {
    "such as", "free service", "valuable data", "before you hit send",
    "real-time snapshot", "these tools", "these are the tools"
}

def _normalize(p: str) -> str:
    p = re.sub(r"\s+", " ", p.strip())
    return p.lower()

def _is_filler(p: str) -> bool:
    lp = _normalize(p)
    if lp in BLOCKLIST:
        return True
    if len(lp) < 3:
        return True
    if lp in {"tools", "service", "services", "data"}:
        return True
    return False

def _keep_by_domain(p: str) -> bool:
    if p.lower() in BRAND_WHITELIST:
        return True
    if ALLOWLIST_PAT.search(p):
        return True
    # keep nouny/technical chunks if not filler
    return not _is_filler(p)

def extract_keyphrases(raw_text: str, top_n: int = 15) -> List[str]:
    """
    Returns a deduped, prioritized list of keyphrases.
    Order: allowlist hits > others, limited to top_n.
    """
    txt = (raw_text or "").strip()
    if not txt:
        return []
    
    # Lazy load models only when function is called
    try:
        nlp = _get_nlp()
        kw = _get_kw()
        yake = _get_yake()
    except Exception as e:
        print(f"Model loading failed: {e}")
        return []

    # 1) NLTK noun chunks + proper nouns
    try:
        if not _get_nlp():
            candidates = set()
        else:
            tokens = word_tokenize(txt)
            pos_tags = pos_tag(tokens)
            
            # Extract noun phrases (simplified)
            np_chunks = set()
            current_chunk = []
            
            for token, pos in pos_tags:
                if pos.startswith('NN'):  # Noun
                    current_chunk.append(token)
                else:
                    if current_chunk:
                        chunk_text = " ".join(current_chunk).strip()
                        if len(current_chunk) <= 6 and not _is_filler(chunk_text):
                            np_chunks.add(chunk_text)
                        current_chunk = []
            
            # Add final chunk
            if current_chunk:
                chunk_text = " ".join(current_chunk).strip()
                if len(current_chunk) <= 6 and not _is_filler(chunk_text):
                    np_chunks.add(chunk_text)
            
            # Extract proper nouns
            propn_tokens = set()
            for token, pos in pos_tags:
                if pos == 'NNP':  # Proper noun
                    propn_tokens.add(token)
            
            candidates: Set[str] = {c for c in (np_chunks | propn_tokens) if not _is_filler(c)}
    except Exception as e:
        print(f"NLTK processing failed: {e}")
        candidates = set()

    # 2) KeyBERT semantic ranking
    try:
        kw = _get_kw()
        kb = kw.extract_keywords(
            txt,
            keyphrase_ngram_range=(1, 3),
            stop_words="english",
            use_maxsum=True,
            nr_candidates=40,
            top_n=top_n
        )
        kb_terms = [k for (k, _score) in kb]
    except Exception as e:
        print(f"KeyBERT processing failed: {e}")
        kb_terms = []

    # 3) YAKE statistical extraction
    try:
        yake_extractor = _get_yake()
        yake_terms = [k for (k, _score) in yake_extractor.extract_keywords(txt)]
    except Exception as e:
        print(f"YAKE processing failed: {e}")
        yake_terms = []

    # 4) Merge
    merged = list(candidates) + kb_terms + yake_terms

    # 5) Clean + filter + dedupe
    cleaned = []
    seen = set()
    for p in merged:
        p = re.sub(r"[^\w\s\-\&/]+", "", p).strip()
        p = re.sub(r"\s+", " ", p)
        if not p or _is_filler(p):
            continue
        if len(p.split()) == 1 and p.lower() in {"tools", "service", "data", "testing"}:
            continue
        lp = p.lower()
        if lp in seen:
            continue
        if _keep_by_domain(p):
            cleaned.append(p)
            seen.add(lp)

    # 6) Prioritize allowlist hits
    allow_hits = [p for p in cleaned if ALLOWLIST_PAT.search(p)]
    others = [p for p in cleaned if p not in allow_hits]
    out = (allow_hits + others)[:top_n]
    return out

if __name__ == "__main__":
    sample = """Inbox placement and content testing tools... Seed list testing tools (GlockApps, Unspam).
    Content and spam score checkers (Folderly, Mailmeteor). Sender reputation monitoring, Google Postmaster Tools,
    spam folder vs primary inbox vs promotions tab, authentication checks, IP and domain reputation."""
    print(extract_keyphrases(sample))
