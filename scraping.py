# scraping.py
# Async SearchAPI client + optional article main-text fetch
# Requires: aiohttp, tldextract, beautifulsoup4, readability-lxml

import asyncio

# ---------------------------------------------------------------------
# API Key Configuration
# ---------------------------------------------------------------------
SEARCHAPI_API_KEY = "WLcBQEMKS8U7PByABFZg3hUd"
import html
import re
from typing import List, Dict, Any, Optional

import aiohttp
from bs4 import BeautifulSoup
import tldextract
from readability import Document

# ---------------------------------------------------------------------
# Utils
# ---------------------------------------------------------------------
USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)

def _domain_from_url(url: str) -> str:
    try:
        parts = tldextract.extract(url)
        if parts.domain and parts.suffix:
            return f"{parts.domain}.{parts.suffix}"
        return url
    except Exception:
        return url

def _clean_snippet(text: Optional[str]) -> str:
    if not text:
        return ""
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

# ---------------------------------------------------------------------
# SearchAPI: fetch Google SERPs
# ---------------------------------------------------------------------
async def _fetch_single_serp(
    session: aiohttp.ClientSession,
    query: str,
    locale: str,
    api_key: str,
    num: int = 30,
) -> Dict[str, Any]:
    """
    Calls SearchAPI (Google) for a single query and returns a normalized result.
    """
    # Basic locale handling: 'en-US' -> hl=en, gl=US
    hl = "en"
    gl = ""
    if "-" in locale:
        hl, gl = locale.split("-", 1)
    elif locale:
        hl = locale

    # SearchAPI endpoint
    # Docs typically accept: engine=google, q=..., api_key=..., hl=..., gl=..., num=...
    params = {
        "engine": "google",
        "q": query,
        "api_key": api_key,
        "hl": hl,
        "gl": gl,
        "num": str(num),
    }

    url = "https://www.searchapi.io/api/v1/search"

    try:
        async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=25)) as resp:
            resp.raise_for_status()
            data = await resp.json()
    except Exception as e:
        # Return empty docs but include the error
        return {"query": query, "docs": [], "error": f"{e}"}

    docs: List[Dict[str, Any]] = []

    # SearchAPI often returns an array under keys like "organic_results" (common)
    # We'll parse organic results if present, otherwise try a few fallbacks.
    organic = data.get("organic_results") or data.get("results") or []
    pos = 1
    for item in organic:
        link = item.get("link") or item.get("url") or ""
        title = item.get("title") or item.get("headline") or ""
        snippet = (
            item.get("snippet")
            or item.get("description")
            or item.get("content")
            or ""
        )

        if not link:
            continue

        docs.append(
            {
                "query": query,
                "title": _clean_snippet(title),
                "link": link,
                "snippet": _clean_snippet(snippet),
                "domain": _domain_from_url(link),
                "position": pos,
            }
        )
        pos += 1

    return {"query": query, "docs": docs, "error": None}

async def fetch_serps_batch(
    queries: List[str],
    locale: str,
    api_key: str,
    per_query: int = 30,
    concurrency: int = 6,
) -> List[Dict[str, Any]]:
    """
    Fetch SERPs for multiple queries concurrently.
    Returns: List of { "query": <q>, "docs": [ ...normalized docs... ], "error": str|None }
    """
    if not api_key:
        raise ValueError("fetch_serps_batch() requires api_key")

    connector = aiohttp.TCPConnector(limit_per_host=concurrency)
    headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}

    async with aiohttp.ClientSession(connector=connector, headers=headers) as session:
        tasks = [
            _fetch_single_serp(session, q, locale=locale, api_key=api_key, num=per_query)
            for q in queries
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

    normalized: List[Dict[str, Any]] = []
    for q, res in zip(queries, results):
        if isinstance(res, Exception):
            normalized.append({"query": q, "docs": [], "error": str(res)})
        else:
            normalized.append(res)

    return normalized

# ---------------------------------------------------------------------
# Optional: fetch each page and extract readable main text
# ---------------------------------------------------------------------
async def _fetch_html(session: aiohttp.ClientSession, url: str) -> Optional[str]:
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=20)) as resp:
            if resp.status >= 400:
                return None
            # attempt text (some sites require encoding detection, but we'll rely on aiohttp)
            return await resp.text(errors="ignore")
    except Exception:
        return None

def _extract_main_text(html_content: str) -> str:
    """
    Use readability-lxml to extract a clean article text. Fallback to BS4 text.
    """
    try:
        doc = Document(html_content)
        summary_html = doc.summary(html_partial=True)
        soup = BeautifulSoup(summary_html, "html.parser")
        # readability summary can include a lot of markup; get text
        text = soup.get_text(separator=" ", strip=True)
        text = re.sub(r"\s+", " ", text).strip()
        return text
    except Exception:
        try:
            soup = BeautifulSoup(html_content, "html.parser")
            text = soup.get_text(separator=" ", strip=True)
            return re.sub(r"\s+", " ", text).strip()
        except Exception:
            return ""

async def fetch_pages_maintext_batch(
    docs: List[Dict[str, Any]],
    concurrency: int = 8
) -> List[Dict[str, Any]]:
    """
    For each doc in docs, fetch HTML and add "maintext" key.
    Returns a NEW list of docs with "maintext".
    """
    connector = aiohttp.TCPConnector(limit_per_host=concurrency)
    headers = {"User-Agent": USER_AGENT, "Accept": "text/html,application/xhtml+xml"}

    async with aiohttp.ClientSession(connector=connector, headers=headers) as session:
        sem = asyncio.Semaphore(concurrency)

        async def _worker(doc: Dict[str, Any]) -> Dict[str, Any]:
            url = doc.get("link")
            if not url:
                out = dict(doc)
                out["maintext"] = ""
                return out

            async with sem:
                html_content = await _fetch_html(session, url)
                if not html_content:
                    out = dict(doc)
                    out["maintext"] = ""
                    return out

                maintext = _extract_main_text(html_content)
                out = dict(doc)
                out["maintext"] = maintext
                return out

        tasks = [_worker(d) for d in docs]
        results = await asyncio.gather(*tasks, return_exceptions=True)

    final_docs: List[Dict[str, Any]] = []
    for d, res in zip(docs, results):
        if isinstance(res, Exception):
            out = dict(d)
            out["maintext"] = ""
            final_docs.append(out)
        else:
            final_docs.append(res)

    return final_docs

