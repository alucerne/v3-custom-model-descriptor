
# main.py
# FastAPI entrypoint for:
# - Phase 1 (SERP mining):     POST /v1/phase1/process
# - Phase 2 (description):     POST /v1/phase2/describe
# - Combined (1 → 2 pipeline): POST /v1/phase1+2/process

import subprocess
import sys

# Initialize NLTK data
try:
    import nltk
    nltk.download('punkt', quiet=True)
    nltk.download('averaged_perceptron_tagger', quiet=True)
    nltk.download('maxent_ne_chunker', quiet=True)
    nltk.download('words', quiet=True)
except Exception as e:
    print(f"NLTK initialization warning: {e}")

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

from scraping import fetch_serps_batch, fetch_pages_maintext_batch, SEARCHAPI_API_KEY
from text_mining import build_keyword_bank, extract_raw_content
from writer import write_description, validate_and_repair, write_name

app = FastAPI(title="Phase1-2 Intent Builder", version="1.2.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://localhost:3001", 
        "http://localhost:3002", 
        "http://localhost:3003",
        "https://spark.audiencelab.io",
        "https://spark-ai-git-staging-deeeps-projects-8d9261fd.vercel.app",
        "https://sparkv3.vercel.app",
        "https://sparkv3-git-main-deeeps-projects-8d9261fd.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------
# Models
# --------------------------

class Phase1Request(BaseModel):
    seed_keywords: List[str] = Field(..., min_items=1, max_items=20)
    locale: str = "en-US"
    results_per_query: int = 30
    html_fetch: bool = False  # optional: fetch main text of SERP URLs
    extract_phrases: bool = True  # optional: extract keyphrases using keyword_extractor

class Phase1Response(BaseModel):
    raw_content: Dict[str, Any]
    draft_description: str
    meta: Dict[str, Any]

class Phase2Request(BaseModel):
    topic: str
    lens: str
    category: Optional[str] = None
    sub_category: Optional[str] = None
    raw_content: Dict[str, Any]
    use_llm: bool = True
    provider: Optional[str] = "gemini"

class Phase2Response(BaseModel):
    names: List[str]
    description: str
    validation: Dict[str, Any]

class PipelineRequest(BaseModel):
    # Phase 1 inputs
    seed_keywords: List[str] = Field(..., min_items=1, max_items=20)
    locale: str = "en-US"
    results_per_query: int = 30
    html_fetch: bool = False
    extract_phrases: bool = True  # optional: extract keyphrases using keyword_extractor

    # Phase 2 inputs
    lens_type: str = Field(..., description="One of: service, brand, event, product, solution, function")
    topic: Optional[str] = None
    category: Optional[str] = None
    sub_category: Optional[str] = None

    # LLM
    use_llm: bool = True
    provider: Optional[str] = "gemini"

class PipelineResponse(BaseModel):
    # Phase 1 out
    raw_content: Dict[str, Any]
    draft_description: str
    meta: Dict[str, Any]
    # Phase 2 out
    names: List[str]
    description: str
    validation: Dict[str, Any]

# --------------------------
# Health
# --------------------------

@app.get("/health")
async def health():
    return {"ok": True}

# --------------------------
# Direct Keyword Extraction
# --------------------------

class ExtractRequest(BaseModel):
    raw_text: str = Field(..., description="Text to extract keyphrases from")
    top_n: int = Field(15, ge=1, le=50, description="Number of keyphrases to extract")

class ExtractResponse(BaseModel):
    keyphrases: List[str]
    count: int

@app.post("/v1/extract", response_model=ExtractResponse)
async def extract_keyphrases(req: ExtractRequest):
    """
    Extract keyphrases directly from raw text using the keyword extractor.
    """
    try:
        from keyword_extractor import extract_keyphrases
        phrases = extract_keyphrases(req.raw_text, top_n=req.top_n)
        return ExtractResponse(
            keyphrases=phrases,
            count=len(phrases)
        )
    except ImportError:
        raise HTTPException(
            status_code=500, 
            detail="Keyword extractor not available. Please install required dependencies."
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Keyword extraction failed: {str(e)}"
        )

# --------------------------
# Step 1: SERP Mining Only
# --------------------------

class Step1Request(BaseModel):
    seed_keywords: List[str] = Field(..., min_items=1, max_items=20)
    locale: str = "en-US"
    results_per_query: int = 30
    html_fetch: bool = False  # optional: fetch main text of SERP URLs

class Step1Response(BaseModel):
    serp_results: List[Dict[str, Any]]  # Raw SERP data
    meta: Dict[str, Any]
    total_docs: int
    total_queries: int

@app.post("/v1/step1/serp-mining", response_model=Step1Response)
async def step1_serp_mining(req: Step1Request):
    """
    Step 1: Fetch SERP results only. No keyword extraction yet.
    User can review the SERP results before proceeding to keyword extraction.
    """
    # 1) Fetch SERPs (batch)
    try:
        serp_docs = await fetch_serps_batch(
            queries=req.seed_keywords,
            locale=req.locale,
            api_key=SEARCHAPI_API_KEY,
            per_query=req.results_per_query
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected SERP error: {str(e)}")

    # 2) (Optional) Fetch page main text for richer NLP (off by default)
    if req.html_fetch:
        # Extract all docs from SERP results
        all_docs = []
        for block in serp_docs:
            all_docs.extend(block.get("docs", []))
        
        # Fetch full page content
        if all_docs:
            enhanced_docs = await fetch_pages_maintext_batch(all_docs)
            # Merge maintext into the original docs structure
            for i, block in enumerate(serp_docs):
                if block.get("docs"):
                    for j, doc in enumerate(block["docs"]):
                        if j < len(enhanced_docs):
                            doc["maintext"] = enhanced_docs[j].get("maintext", "")
    else:
        # Ensure maintext field exists for text mining
        for block in serp_docs:
            for doc in block.get("docs", []):
                doc["maintext"] = ""

    # Count total documents
    total_docs = sum(len(block.get("docs", [])) for block in serp_docs)

    return Step1Response(
        serp_results=serp_docs,
        meta={
            "queries": req.seed_keywords,
            "locale": req.locale,
            "results_per_query": req.results_per_query,
            "html_fetch_enabled": req.html_fetch,
        },
        total_docs=total_docs,
        total_queries=len(req.seed_keywords)
    )

# --------------------------
# Step 2: Keyword Extraction from SERP Results
# --------------------------

class Step2Request(BaseModel):
    serp_results: List[Dict[str, Any]] = Field(..., description="SERP results from Step 1")
    seed_keywords: List[str] = Field(..., min_items=1, max_items=20)
    extract_phrases: bool = True  # optional: extract keyphrases using keyword_extractor

class Step2Response(BaseModel):
    raw_content: Dict[str, Any]
    draft_description: str
    meta: Dict[str, Any]

@app.post("/v1/step2/keyword-extraction", response_model=Step2Response)
async def step2_keyword_extraction(req: Step2Request):
    """
    Step 2: Extract keywords and analyze content from SERP results.
    Takes the SERP results from Step 1 and performs keyword extraction.
    """
    serp_docs = req.serp_results
    
    # 1) Extract raw content for Phase 2 processing
    raw_content = extract_raw_content(serp_docs, seeds=req.seed_keywords)
    
    # 2) (Optional) Extract keyphrases using enhanced keyword extractor
    if req.extract_phrases:
        try:
            from enhanced_keyword_extractor import extract_enhanced_keyphrases
            from domain_patterns import detect_domain
            
            # Concatenate all snippets for keyword extraction
            all_snippets = []
            for block in serp_docs:
                for doc in block.get("docs", []):
                    all_snippets.extend([
                        doc.get("title", ""),
                        doc.get("snippet", ""),
                        doc.get("maintext", "")
                    ])
            concatenated_text = " ".join(all_snippets)
            
            # Determine domain based on seed keywords and content
            domain = detect_domain(req.seed_keywords, concatenated_text)
            
            # Extract keyphrases using enhanced extractor
            keyphrases = extract_enhanced_keyphrases(concatenated_text, domain=domain, top_n=15)
            if keyphrases:
                raw_content["extracted_keyphrases"] = keyphrases
                print(f"Enhanced extracted {len(keyphrases)} keyphrases: {keyphrases[:5]}...")
        except Exception as e:
            print(f"Enhanced keyword extraction failed: {e}")
            # Fallback to simple extractor
            try:
                from simple_keyword_extractor import extract_simple_keyphrases
                concatenated_text = " ".join(all_snippets)
                keyphrases = extract_simple_keyphrases(concatenated_text, top_n=15)
                if keyphrases:
                    raw_content["extracted_keyphrases"] = keyphrases
                    print(f"Fallback extracted {len(keyphrases)} keyphrases: {keyphrases[:5]}...")
            except Exception as e2:
                print(f"Fallback keyword extraction also failed: {e2}")
                # Continue without keyword extraction

    # 3) Generate draft description
    top_terms = raw_content.get("top_terms", [])[:4]
    top_phrases = raw_content.get("top_phrases", [])[:2]
    seeds = raw_content.get("seeds", [])[:2]

    core = ", ".join([t for t in (top_terms + top_phrases) if t] or ["the topic"])
    seed_txt = f" ({', '.join(seeds)})" if seeds else ""
    draft = f"This intent captures research into {core}{seed_txt}. It focuses on pricing, reviews, comparisons for evaluation."

    return Step2Response(
        raw_content=raw_content,
        draft_description=draft,
        meta={
            "queries": req.seed_keywords,
            "docs_analyzed": raw_content.get("evidence_count", 0),
            "extract_phrases_enabled": req.extract_phrases,
        }
    )

# --------------------------
# Legacy Phase 1: Combined SERP + Keyword Extraction (for backward compatibility)
# --------------------------

@app.post("/v1/phase1/process", response_model=Phase1Response)
async def phase1_process(req: Phase1Request):
    """
    Legacy endpoint: Combined SERP mining + keyword extraction.
    For backward compatibility. New implementations should use Step 1 + Step 2.
    """
    # 1) Fetch SERPs (batch)
    try:
        serp_docs = await fetch_serps_batch(
            queries=req.seed_keywords,
            locale=req.locale,
            api_key=SEARCHAPI_API_KEY,
            per_query=req.results_per_query
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected SERP error: {str(e)}")

    # 2) (Optional) Fetch page main text for richer NLP (off by default)
    if req.html_fetch:
        # Extract all docs from SERP results
        all_docs = []
        for block in serp_docs:
            all_docs.extend(block.get("docs", []))
        
        # Fetch full page content
        if all_docs:
            enhanced_docs = await fetch_pages_maintext_batch(all_docs)
            # Merge maintext into the original docs structure
            for i, block in enumerate(serp_docs):
                if block.get("docs"):
                    for j, doc in enumerate(block["docs"]):
                        if j < len(enhanced_docs):
                            doc["text"] = enhanced_docs[j].get("maintext", "")
    else:
        # Ensure text field exists for text mining
        for block in serp_docs:
            for doc in block.get("docs", []):
                doc["text"] = ""

    # 3) Extract raw content for Phase 2 processing
    raw_content = extract_raw_content(serp_docs, seeds=req.seed_keywords)
    
    # 4) (Optional) Extract keyphrases using enhanced keyword extractor
    if req.extract_phrases:
        try:
            from enhanced_keyword_extractor import extract_enhanced_keyphrases
            from domain_patterns import detect_domain
            from semantic_clustering import cluster_keywords, get_cluster_summaries
            from context_scoring import get_top_keywords_with_context
            
            # Concatenate all snippets for keyword extraction
            all_snippets = []
            for block in serp_docs:
                for doc in block.get("docs", []):
                    all_snippets.extend([
                        doc.get("title", ""),
                        doc.get("snippet", ""),
                        doc.get("text", "")
                    ])
            concatenated_text = " ".join(all_snippets)
            
            # Determine domain based on seed keywords and content
            domain = detect_domain(req.seed_keywords, concatenated_text)
            
            # Extract keyphrases using enhanced extractor
            keyphrases = extract_enhanced_keyphrases(concatenated_text, domain=domain, top_n=15)
            if keyphrases:
                raw_content["extracted_keyphrases"] = keyphrases
                print(f"Enhanced extracted {len(keyphrases)} keyphrases: {keyphrases[:5]}...")
        except Exception as e:
            print(f"Enhanced keyword extraction failed: {e}")
            # Fallback to simple extractor
            try:
                from simple_keyword_extractor import extract_simple_keyphrases
                concatenated_text = " ".join(all_snippets)
                keyphrases = extract_simple_keyphrases(concatenated_text, top_n=15)
                if keyphrases:
                    raw_content["extracted_keyphrases"] = keyphrases
                    print(f"Fallback extracted {len(keyphrases)} keyphrases: {keyphrases[:5]}...")
            except Exception as e2:
                print(f"Fallback keyword extraction also failed: {e2}")
                # Continue without keyword extraction

    # 5) Tiny draft (not final)
    top_terms = raw_content.get("top_terms", [])[:4]
    top_phrases = raw_content.get("top_phrases", [])[:2]
    seeds = raw_content.get("seeds", [])[:2]

    core = ", ".join([t for t in (top_terms + top_phrases) if t] or ["the topic"])
    seed_txt = f" ({', '.join(seeds)})" if seeds else ""
    draft = f"This intent captures research into {core}{seed_txt}. It focuses on pricing, reviews, comparisons for evaluation."

    return Phase1Response(
        raw_content=raw_content,
        draft_description=draft,
        meta={
            "queries": req.seed_keywords,
            "locale": req.locale,
            "results_per_query": req.results_per_query,
            "html_fetch_enabled": req.html_fetch,
            "docs_analyzed": raw_content.get("evidence_count", 0),
        }
    )

# --------------------------
# Phase 2: keyword_bank + lens → names + final description
# --------------------------

@app.post("/v1/phase2/describe", response_model=Phase2Response)
async def phase2_describe(req: Phase2Request):
    raw_content = req.raw_content or {}
    
    # Extract key information from raw content for LLM processing
    top_terms = raw_content.get("top_terms", [])
    top_phrases = raw_content.get("top_phrases", [])
    combined_text = raw_content.get("combined_text", "")
    term_frequencies = raw_content.get("term_frequencies", {})
    
    # Create an enhanced keyword bank with all raw content data
    enhanced_bank = {
        "exact_terms": top_phrases[:15],
        "semantic_terms": top_terms[:20],
        "disambiguators": raw_content.get("seeds", [])[:3],
        "stop_terms": [],  # Let Phase 2 handle filtering
        "evidence_count": raw_content.get("evidence_count", 0),
        # Add all the rich content data for enhanced LLM processing
        "top_terms": top_terms,
        "top_phrases": top_phrases,
        "term_frequencies": term_frequencies,
        "phrase_frequencies": raw_content.get("phrase_frequencies", {}),
        "combined_text": combined_text,
        "total_docs": raw_content.get("total_docs", 0),
        "total_text_length": raw_content.get("total_text_length", 0),
        "seeds": raw_content.get("seeds", [])
    }

    # 1) Ask writer (Gemini first, then deterministic fallback inside writer)
    try:
        # Call write_description with correct parameters
        desc = write_description(
            topic=req.topic,
            lens=req.lens,
            category=req.category,
            sub_category=req.sub_category,
            bank=enhanced_bank
        )
        
        # Call write_name for names
        names = write_name(
            topic=req.topic,
            lens=req.lens,
            category=req.category,
            sub_category=req.sub_category,
            bank=enhanced_bank
        )
    except Exception as e:
        print(f"Error in write_description: {e}")
        names = [f"{req.topic} Services", f"{req.topic} Platform", f"{req.topic} Tools"]
        desc = "This intent captures research into core features and capabilities. It focuses on pricing, reviews, and comparisons for evaluation."

    # 2) Enforce gotchya guards and polish
    try:
        desc_final = validate_and_repair(
            text=desc,
            forbidden=enhanced_bank.get("stop_terms", []),
            disambiguators=enhanced_bank.get("disambiguators", []),
            min_words=18,
            max_words=42
        )
    except Exception:
        desc_final = desc

    return Phase2Response(
        names=names[:3] if names else [f"{req.topic} Option 1", f"{req.topic} Option 2", f"{req.topic} Option 3"],
        description=desc_final,
        validation={
            "forbidden_used": False,  # Simplified for now
            "word_count": len(desc_final.split()),
            "has_two_sentences": desc_final.count(".") >= 2
        }
    )

# --------------------------
# Combined: Phase 1 → Phase 2
# --------------------------

@app.post("/v1/phase1+2/process", response_model=PipelineResponse)
async def pipeline_process(req: PipelineRequest):
    # ---- Phase 1 ----
    try:
        serp_docs = await fetch_serps_batch(
            queries=req.seed_keywords,
            locale=req.locale,
            api_key=SEARCHAPI_API_KEY,
            per_query=req.results_per_query
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected SERP error: {str(e)}")

    # 2) (Optional) Fetch page main text for richer NLP
    if req.html_fetch:
        # Extract all docs from SERP results
        all_docs = []
        for block in serp_docs:
            all_docs.extend(block.get("docs", []))
        
        # Fetch full page content
        if all_docs:
            enhanced_docs = await fetch_pages_maintext_batch(all_docs)
            # Merge maintext into the original docs
            for i, block in enumerate(serp_docs):
                if block.get("docs"):
                    for j, doc in enumerate(block["docs"]):
                        if j < len(enhanced_docs):
                            doc["maintext"] = enhanced_docs[j].get("maintext", "")
    else:
        # Ensure maintext field exists for text mining
        for block in serp_docs:
            for doc in block.get("docs", []):
                doc["maintext"] = ""

    # 3) Extract raw content for Phase 2 processing
    raw_content = extract_raw_content(serp_docs, seeds=req.seed_keywords)
    
    # 4) (Optional) Extract keyphrases using enhanced keyword extractor
    if req.extract_phrases:
        try:
            from enhanced_keyword_extractor import extract_enhanced_keyphrases
            # Concatenate all snippets for keyword extraction
            all_snippets = []
            for block in serp_docs:
                for doc in block.get("docs", []):
                    all_snippets.extend([
                        doc.get("title", ""),
                        doc.get("snippet", ""),
                        doc.get("maintext", "")
                    ])
            concatenated_text = " ".join(all_snippets)
            
            # Determine domain based on seed keywords and content
            from domain_patterns import detect_domain
            from semantic_clustering import cluster_keywords, get_cluster_summaries
            from context_scoring import get_top_keywords_with_context
            
            domain = detect_domain(req.seed_keywords, concatenated_text)
            
            # Extract keyphrases using enhanced extractor
            keyphrases = extract_enhanced_keyphrases(concatenated_text, domain=domain, top_n=15)
            if keyphrases:
                raw_content["extracted_keyphrases"] = keyphrases
                print(f"Enhanced extracted {len(keyphrases)} keyphrases: {keyphrases[:5]}...")
        except Exception as e:
            print(f"Enhanced keyword extraction failed: {e}")
            # Fallback to simple extractor
            try:
                from simple_keyword_extractor import extract_simple_keyphrases
                concatenated_text = " ".join(all_snippets)
                keyphrases = extract_simple_keyphrases(concatenated_text, top_n=15)
                if keyphrases:
                    raw_content["extracted_keyphrases"] = keyphrases
                    print(f"Fallback extracted {len(keyphrases)} keyphrases: {keyphrases[:5]}...")
            except Exception as e2:
                print(f"Fallback keyword extraction also failed: {e2}")
                # Continue without keyword extraction

    # 5) Create draft description
    top_terms = raw_content.get("top_terms", [])[:4]
    top_phrases = raw_content.get("top_phrases", [])[:2]
    seeds = raw_content.get("seeds", [])[:2]

    core = ", ".join([t for t in (top_terms + top_phrases) if t] or ["the topic"])
    seed_txt = f" ({', '.join(seeds)})" if seeds else ""
    draft = f"This intent captures research into {core}{seed_txt}. It focuses on pricing, reviews, comparisons for evaluation."

    # Determine a sensible topic if not provided
    topic = req.topic or (top_terms[0] if top_terms else (top_phrases[0] if top_phrases else "Intent Topic"))

    # ---- Phase 2 ----
    # Create an enhanced keyword bank with all raw content data
    enhanced_bank = {
        "exact_terms": raw_content.get("top_phrases", [])[:15],
        "semantic_terms": raw_content.get("top_terms", [])[:20],
        "disambiguators": raw_content.get("seeds", [])[:3],
        "stop_terms": [],  # Let Phase 2 handle filtering
        "evidence_count": raw_content.get("evidence_count", 0),
        # Add all the rich content data for enhanced LLM processing
        "top_terms": raw_content.get("top_terms", []),
        "top_phrases": raw_content.get("top_phrases", []),
        "term_frequencies": raw_content.get("term_frequencies", {}),
        "phrase_frequencies": raw_content.get("phrase_frequencies", {}),
        "combined_text": raw_content.get("combined_text", ""),
        "total_docs": raw_content.get("total_docs", 0),
        "total_text_length": raw_content.get("total_text_length", 0),
        "seeds": raw_content.get("seeds", [])
    }
    
    try:
        # Call write_description with correct parameters
        desc = write_description(
            topic=topic,
            lens=req.lens_type,
            category=req.category,
            sub_category=req.sub_category,
            bank=enhanced_bank
        )
        
        # Call write_name for names
        names = write_name(
            topic=topic,
            lens=req.lens_type,
            category=req.category,
            sub_category=req.sub_category,
            bank=enhanced_bank
        )
    except Exception as e:
        print(f"Error in write_description: {e}")
        names = [f"{topic} Services", f"{topic} Platform", f"{topic} Tools"]
        desc = "This intent captures research into core features and capabilities. It focuses on pricing, reviews, and comparisons for evaluation."

    try:
        desc_final = validate_and_repair(
            text=desc,
            forbidden=enhanced_bank.get("stop_terms", []),
            disambiguators=enhanced_bank.get("disambiguators", []),
            min_words=18,
            max_words=42
        )
    except Exception:
        desc_final = desc

    return PipelineResponse(
        # phase 1
        raw_content=raw_content,
        draft_description=draft,
        meta={
            "queries": req.seed_keywords,
            "locale": req.locale,
            "results_per_query": req.results_per_query,
            "html_fetch_enabled": req.html_fetch,
            "docs_analyzed": raw_content.get("evidence_count", 0),
        },
        # phase 2
        names=names[:3] if names else [f"{topic} Option 1", f"{topic} Option 2", f"{topic} Option 3"],
        description=desc_final,
        validation={
            "forbidden_used": False,  # Simplified for now
            "word_count": len(desc_final.split()),
            "has_two_sentences": desc_final.count(".") >= 2
        }
    )
