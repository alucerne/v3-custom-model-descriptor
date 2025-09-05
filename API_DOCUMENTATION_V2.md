# 🚀 Custom Model Descriptor API Documentation v2.0

**Base URL**: `http://localhost:8000` (Local Development)

## 📋 Table of Contents

1. [Health Check](#health-check)
2. [New Two-Step Process](#new-two-step-process)
   - [Step 1: SERP Mining](#step-1-serp-mining)
   - [Step 2: Keyword Extraction](#step-2-keyword-extraction)
3. [Legacy Endpoints](#legacy-endpoints)
4. [Phase 2: Description Generation](#phase-2-description-generation)
5. [Combined Pipeline](#combined-pipeline)
6. [Lens Types](#lens-types)
7. [Error Handling](#error-handling)
8. [Rate Limits](#rate-limits)

---

## 🔍 Health Check

### GET `/health`

Check if the service is running.

**Response:**
```json
{
  "ok": true
}
```

**Test Curl:**
```bash
curl -X GET "https://v3-custom-model-descriptor.onrender.com/health"
```

---

## 🆕 New Two-Step Process

The API now supports a **two-step workflow** that allows users to review SERP results before proceeding to keyword extraction. This gives users more control over the process and allows them to validate the quality of search results.

### **Step 1: SERP Mining**

### POST `/v1/step1/serp-mining`

Fetch SERP results only. No keyword extraction yet. User can review the SERP results before proceeding to keyword extraction.

**Request Body:**
```json
{
  "seed_keywords": ["email deliverability", "spam score"],
  "locale": "en-US",
  "results_per_query": 30,
  "html_fetch": false
}
```

**Parameters:**
- `seed_keywords` (required): Array of keywords to search for (1-20 items)
- `locale` (optional): Search locale (default: "en-US")
- `results_per_query` (optional): Number of SERP results per query (default: 30)
- `html_fetch` (optional): Whether to fetch full page content (default: false)

**Response:**
```json
{
  "serp_results": [
    {
      "query": "email deliverability",
      "docs": [
        {
          "title": "Email Deliverability Guide - Best Practices",
          "snippet": "Learn about email deliverability best practices...",
          "domain": "example.com",
          "link": "https://example.com/email-deliverability",
          "maintext": "Full page content if html_fetch=true"
        }
      ]
    }
  ],
  "meta": {
    "queries": ["email deliverability", "spam score"],
    "locale": "en-US",
    "results_per_query": 30,
    "html_fetch_enabled": false
  },
  "total_docs": 60,
  "total_queries": 2
}
```

**Test Curls:**

```bash
# Basic SERP mining
curl -X POST "https://v3-custom-model-descriptor.onrender.com/v1/step1/serp-mining" \
  -H "Content-Type: application/json" \
  -d '{
    "seed_keywords": ["email deliverability"],
    "results_per_query": 10
  }'

# With full content fetch
curl -X POST "https://v3-custom-model-descriptor.onrender.com/v1/step1/serp-mining" \
  -H "Content-Type: application/json" \
  -d '{
    "seed_keywords": ["assisted living", "retirement facility"],
    "results_per_query": 20,
    "html_fetch": true
  }'
```

---

### **Step 2: Keyword Extraction**

### POST `/v1/step2/keyword-extraction`

Extract keywords and analyze content from SERP results. Takes the SERP results from Step 1 and performs keyword extraction.

**Request Body:**
```json
{
  "serp_results": [
    {
      "query": "email deliverability",
      "docs": [
        {
          "title": "Email Deliverability Guide",
          "snippet": "Learn about email deliverability best practices...",
          "domain": "example.com",
          "link": "https://example.com/email-deliverability",
          "maintext": "Full page content"
        }
      ]
    }
  ],
  "seed_keywords": ["email deliverability", "spam score"],
  "extract_phrases": true
}
```

**Parameters:**
- `serp_results` (required): SERP results from Step 1
- `seed_keywords` (required): Original seed keywords (1-20 items)
- `extract_phrases` (optional): Whether to extract keyphrases (default: true)

**Response:**
```json
{
  "raw_content": {
    "extracted_keyphrases": ["email deliverability", "spam score analysis", "inbox placement"],
    "top_terms": ["email", "deliverability", "spam", "score", "inbox"],
    "top_phrases": ["email deliverability", "spam score", "inbox placement"],
    "term_frequencies": {
      "email": 45,
      "deliverability": 32,
      "spam": 28
    },
    "phrase_frequencies": {
      "email deliverability": 25,
      "spam score": 18
    },
    "doc_sources": [
      {
        "title": "Email Deliverability Guide",
        "snippet": "Learn about email deliverability best practices...",
        "domain": "example.com",
        "link": "https://example.com/email-deliverability",
        "text_length": 150
      }
    ],
    "total_docs": 30,
    "total_text_length": 5000,
    "seeds": ["email deliverability", "spam score"],
    "evidence_count": 30
  },
  "draft_description": "This intent captures research into email deliverability and spam score analysis...",
  "meta": {
    "queries": ["email deliverability", "spam score"],
    "docs_analyzed": 30,
    "extract_phrases_enabled": true
  }
}
```

**Test Curls:**

```bash
# Extract keywords from SERP results
curl -X POST "https://v3-custom-model-descriptor.onrender.com/v1/step2/keyword-extraction" \
  -H "Content-Type: application/json" \
  -d '{
    "serp_results": [SERP_RESULTS_FROM_STEP1],
    "seed_keywords": ["email deliverability"],
    "extract_phrases": true
  }'
```

---

## 🔄 Complete Two-Step Workflow Example

```bash
# Step 1: Get SERP results
STEP1_RESPONSE=$(curl -X POST "https://v3-custom-model-descriptor.onrender.com/v1/step1/serp-mining" \
  -H "Content-Type: application/json" \
  -d '{
    "seed_keywords": ["email deliverability"],
    "results_per_query": 10
  }')

# Step 2: Extract keywords from SERP results
curl -X POST "https://v3-custom-model-descriptor.onrender.com/v1/step2/keyword-extraction" \
  -H "Content-Type: application/json" \
  -d "{
    \"serp_results\": $(echo $STEP1_RESPONSE | jq '.serp_results'),
    \"seed_keywords\": [\"email deliverability\"],
    \"extract_phrases\": true
  }"
```

---

## 🔄 Legacy Endpoints

### POST `/v1/phase1/process` (Legacy)

**Note**: This endpoint is maintained for backward compatibility. New implementations should use the two-step process above.

Combined SERP mining + keyword extraction in one call.

**Request Body:**
```json
{
  "seed_keywords": ["email deliverability", "spam score"],
  "locale": "en-US",
  "results_per_query": 30,
  "html_fetch": false,
  "extract_phrases": true
}
```

**Response:**
```json
{
  "raw_content": {
    "extracted_keyphrases": ["email deliverability", "spam score analysis"],
    "top_terms": ["email", "deliverability", "spam", "score"],
    "top_phrases": ["email deliverability", "spam score"],
    "term_frequencies": {
      "email": 45,
      "deliverability": 32
    },
    "phrase_frequencies": {
      "email deliverability": 25,
      "spam score": 18
    },
    "doc_sources": [...],
    "total_docs": 30,
    "total_text_length": 5000,
    "seeds": ["email deliverability", "spam score"],
    "evidence_count": 30
  },
  "draft_description": "This intent captures research into email deliverability...",
  "meta": {
    "queries": ["email deliverability", "spam score"],
    "locale": "en-US",
    "results_per_query": 30,
    "html_fetch_enabled": false,
    "docs_analyzed": 30
  }
}
```

---

## ✍️ Phase 2: Description Generation

### POST `/v1/phase2/describe`

Generate descriptions and names based on raw content and lens type.

**Request Body:**
```json
{
  "topic": "email deliverability",
  "lens": "service",
  "category": "marketing",
  "sub_category": "email marketing",
  "raw_content": {
    "extracted_keyphrases": ["email deliverability", "spam score", "inbox placement"],
    "top_terms": ["email", "deliverability", "spam", "score"],
    "top_phrases": ["email deliverability", "spam score"]
  },
  "use_llm": true,
  "provider": "gemini"
}
```

**Parameters:**
- `topic` (required): Main topic for description generation
- `lens` (required): Lens type (service, brand, event, product, solution, function)
- `category` (optional): Category classification
- `sub_category` (optional): Sub-category classification
- `raw_content` (required): Raw content from Step 2 or Phase 1
- `use_llm` (optional): Whether to use LLM (default: true)
- `provider` (optional): LLM provider (default: "gemini")

**Response:**
```json
{
  "names": [
    "Email Deliverability Service",
    "Spam Score Analysis Tool",
    "Inbox Placement Optimizer"
  ],
  "description": "This intent represents interest in email deliverability optimization and spam score analysis for improving inbox placement rates. It encompasses monitoring sender reputation, analyzing authentication protocols, and implementing best practices for email infrastructure management.",
  "validation": {
    "forbidden_used": false,
    "word_count": 45,
    "has_two_sentences": true
  }
}
```

---

## 🔄 Combined Pipeline

### POST `/v1/phase1+2/process`

Complete pipeline: SERP mining → keyword extraction → description generation.

**Request Body:**
```json
{
  "seed_keywords": ["email deliverability", "spam score"],
  "locale": "en-US",
  "results_per_query": 30,
  "html_fetch": false,
  "extract_phrases": true,
  "lens_type": "service",
  "topic": "email deliverability",
  "category": "marketing",
  "sub_category": "email marketing",
  "use_llm": true,
  "provider": "gemini"
}
```

**Response:**
```json
{
  "raw_content": {
    "extracted_keyphrases": ["email deliverability", "spam score analysis"],
    "top_terms": ["email", "deliverability", "spam", "score"],
    "top_phrases": ["email deliverability", "spam score"],
    "term_frequencies": {
      "email": 45,
      "deliverability": 32
    },
    "phrase_frequencies": {
      "email deliverability": 25,
      "spam score": 18
    },
    "doc_sources": [...],
    "total_docs": 30,
    "total_text_length": 5000,
    "seeds": ["email deliverability", "spam score"],
    "evidence_count": 30
  },
  "draft_description": "This intent captures research into email deliverability...",
  "meta": {
    "queries": ["email deliverability", "spam score"],
    "locale": "en-US",
    "results_per_query": 30,
    "html_fetch_enabled": false,
    "docs_analyzed": 30
  },
  "names": [
    "Email Deliverability Service",
    "Spam Score Analysis Tool"
  ],
  "description": "This intent represents interest in email deliverability optimization and spam score analysis for improving inbox placement rates. It encompasses monitoring sender reputation, analyzing authentication protocols, and implementing best practices for email infrastructure management.",
  "validation": {
    "forbidden_used": false,
    "word_count": 45,
    "has_two_sentences": true
  }
}
```

---

## 🎯 Lens Types

The API supports 6 different lens types for generating descriptions from different perspectives:

### 1. **Service** (`service`)
Focuses on services and solutions offered to customers.

### 2. **Brand** (`brand`)
Focuses on brand recognition and company-specific offerings.

### 3. **Event** (`event`)
Focuses on events, conferences, and gatherings.

### 4. **Product** (`product`)
Focuses on specific products and tools.

### 5. **Solution** (`solution`)
Focuses on solving specific business problems.

### 6. **Function** (`function`)
Focuses on technical capabilities and functions.

---

## ⚠️ Error Handling

### Common Error Responses

**400 Bad Request:**
```json
{
  "detail": "Validation error: seed_keywords must contain at least 1 item"
}
```

**404 Not Found:**
```json
{
  "detail": "Not Found"
}
```

**500 Internal Server Error:**
```json
{
  "detail": "Internal server error"
}
```

---

## 🚦 Rate Limits

- **Requests per minute**: 60
- **Requests per hour**: 1000
- **Concurrent requests**: 10

### Rate Limit Response
```json
{
  "detail": "Rate limit exceeded. Please try again later."
}
```

---

## 🚀 Quick Start Guide

### New Two-Step Process

1. **Test the service is running:**
   ```bash
   curl -X GET "https://v3-custom-model-descriptor.onrender.com/health"
   ```

2. **Step 1: Get SERP results:**
   ```bash
   curl -X POST "https://v3-custom-model-descriptor.onrender.com/v1/step1/serp-mining" \
     -H "Content-Type: application/json" \
     -d '{"seed_keywords": ["email deliverability"], "results_per_query": 10}'
   ```

3. **Step 2: Extract keywords (use SERP results from Step 1):**
   ```bash
   curl -X POST "https://v3-custom-model-descriptor.onrender.com/v1/step2/keyword-extraction" \
     -H "Content-Type: application/json" \
     -d '{
       "serp_results": [SERP_RESULTS_FROM_STEP1],
       "seed_keywords": ["email deliverability"],
       "extract_phrases": true
     }'
   ```

4. **Step 3: Generate description (use raw_content from Step 2):**
   ```bash
   curl -X POST "https://v3-custom-model-descriptor.onrender.com/v1/phase2/describe" \
     -H "Content-Type: application/json" \
     -d '{
       "topic": "email deliverability",
       "lens": "service",
       "raw_content": [RAW_CONTENT_FROM_STEP2]
     }'
   ```

### Legacy One-Step Process

```bash
# Combined pipeline (legacy)
curl -X POST "https://v3-custom-model-descriptor.onrender.com/v1/phase1+2/process" \
  -H "Content-Type: application/json" \
  -d '{"seed_keywords": ["email deliverability"], "lens_type": "service"}'
```

---

## 📞 Support

For issues or questions:
- **Service Status**: Check `/health` endpoint
- **Documentation**: This file
- **API Explorer**: Visit `/docs` for interactive documentation

---

*Last Updated: January 2025*
*Version: 2.0.0*
