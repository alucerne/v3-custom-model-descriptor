# 🚀 Custom Model Descriptor API Documentation

**Base URL**: `https://v3-custom-model-descriptor.onrender.com`

## 📋 Table of Contents

1. [Health Check](#health-check)
2. [Phase 1: SERP Mining & Keyword Extraction](#phase-1-serp-mining--keyword-extraction)
3. [Phase 2: Description Generation](#phase-2-description-generation)
4. [Combined Pipeline](#combined-pipeline)
5. [Lens Types](#lens-types)
6. [Error Handling](#error-handling)
7. [Rate Limits](#rate-limits)

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

## 🔍 Phase 1: SERP Mining & Keyword Extraction

### POST `/v1/phase1/process`

Extract keywords and analyze SERP content from seed keywords.

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

**Parameters:**
- `seed_keywords` (required): Array of keywords to search for (1-20 items)
- `locale` (optional): Search locale (default: "en-US")
- `results_per_query` (optional): Number of SERP results per query (default: 30)
- `html_fetch` (optional): Whether to fetch full page content (default: false)
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
    "locale": "en-US",
    "results_per_query": 30,
    "html_fetch_enabled": false,
    "docs_analyzed": 30
  }
}
```

**Test Curls:**

```bash
# Basic keyword extraction
curl -X POST "https://v3-custom-model-descriptor.onrender.com/v1/phase1/process" \
  -H "Content-Type: application/json" \
  -d '{
    "seed_keywords": ["email deliverability"],
    "locale": "en-US",
    "results_per_query": 10,
    "extract_phrases": true
  }'

# Multiple keywords with full content fetch
curl -X POST "https://v3-custom-model-descriptor.onrender.com/v1/phase1/process" \
  -H "Content-Type: application/json" \
  -d '{
    "seed_keywords": ["assisted living", "retirement facility"],
    "locale": "en-US",
    "results_per_query": 20,
    "html_fetch": true,
    "extract_phrases": true
  }'

# Legal services example
curl -X POST "https://v3-custom-model-descriptor.onrender.com/v1/phase1/process" \
  -H "Content-Type: application/json" \
  -d '{
    "seed_keywords": ["legal support for social security disability"],
    "locale": "en-US",
    "results_per_query": 15,
    "extract_phrases": true
  }'
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
- `raw_content` (required): Raw content from Phase 1
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

**Test Curls:**

```bash
# Service lens description
curl -X POST "https://v3-custom-model-descriptor.onrender.com/v1/phase2/describe" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "email deliverability",
    "lens": "service",
    "raw_content": {
      "extracted_keyphrases": ["email deliverability", "spam score", "inbox placement"],
      "top_terms": ["email", "deliverability", "spam", "score"],
      "top_phrases": ["email deliverability", "spam score"]
    }
  }'

# Brand lens description
curl -X POST "https://v3-custom-model-descriptor.onrender.com/v1/phase2/describe" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "assisted living",
    "lens": "brand",
    "raw_content": {
      "extracted_keyphrases": ["assisted living", "senior living", "retirement communities"],
      "top_terms": ["living", "assisted", "senior", "retirement"],
      "top_phrases": ["assisted living", "senior living"]
    }
  }'
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

**Parameters:**
- **Phase 1 parameters**: `seed_keywords`, `locale`, `results_per_query`, `html_fetch`, `extract_phrases`
- **Phase 2 parameters**: `lens_type`, `topic`, `category`, `sub_category`, `use_llm`, `provider`

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

**Test Curls:**

```bash
# Service lens - Email deliverability
curl -X POST "https://v3-custom-model-descriptor.onrender.com/v1/phase1+2/process" \
  -H "Content-Type: application/json" \
  -d '{
    "seed_keywords": ["email deliverability", "spam score"],
    "lens_type": "service"
  }'

# Brand lens - Assisted living
curl -X POST "https://v3-custom-model-descriptor.onrender.com/v1/phase1+2/process" \
  -H "Content-Type: application/json" \
  -d '{
    "seed_keywords": ["assisted living", "retirement facility"],
    "lens_type": "brand"
  }'

# Product lens - SEO tools
curl -X POST "https://v3-custom-model-descriptor.onrender.com/v1/phase1+2/process" \
  -H "Content-Type: application/json" \
  -d '{
    "seed_keywords": ["SEO tools", "keyword research"],
    "lens_type": "product"
  }'

# Event lens - Marketing conferences
curl -X POST "https://v3-custom-model-descriptor.onrender.com/v1/phase1+2/process" \
  -H "Content-Type: application/json" \
  -d '{
    "seed_keywords": ["marketing conference", "digital marketing event"],
    "lens_type": "event"
  }'

# Solution lens - Business problems
curl -X POST "https://v3-custom-model-descriptor.onrender.com/v1/phase1+2/process" \
  -H "Content-Type: application/json" \
  -d '{
    "seed_keywords": ["customer retention", "churn reduction"],
    "lens_type": "solution"
  }'

# Function lens - Technical capabilities
curl -X POST "https://v3-custom-model-descriptor.onrender.com/v1/phase1+2/process" \
  -H "Content-Type: application/json" \
  -d '{
    "seed_keywords": ["data analytics", "business intelligence"],
    "lens_type": "function"
  }'
```

---

## 🎯 Lens Types

The API supports 6 different lens types for generating descriptions from different perspectives:

### 1. **Service** (`service`)
Focuses on services and solutions offered to customers.

**Example Output:**
> "This intent represents interest in email deliverability optimization and spam score analysis for improving inbox placement rates. It encompasses monitoring sender reputation, analyzing authentication protocols, and implementing best practices for email infrastructure management."

### 2. **Brand** (`brand`)
Focuses on brand recognition and company-specific offerings.

**Example Output:**
> "This intent represents interest in locating and researching assisted living and independent living facilities, specifically within the state of Iowa. It encompasses the identification of 'assisted living facilities,' 'independent living,' and 'senior living communities' available in Iowa, considering factors such as community features and care services offered."

### 3. **Event** (`event`)
Focuses on events, conferences, and gatherings.

**Example Output:**
> "This intent represents interest in attending and participating in marketing conferences and digital marketing events. It encompasses networking opportunities, learning about industry trends, and discovering new marketing strategies and technologies."

### 4. **Product** (`product`)
Focuses on specific products and tools.

**Example Output:**
> "This intent represents interest in senior living options, specifically assisted living and independent living facilities. It encompasses researching 'retirement community' choices, exploring 'senior living' facilities in 'new york,' and comparing 'assisted living' and 'independent living' care models."

### 5. **Solution** (`solution`)
Focuses on solving specific business problems.

**Example Output:**
> "This intent represents interest in addressing customer retention challenges and implementing churn reduction strategies. It encompasses analyzing customer behavior patterns, developing loyalty programs, and creating personalized engagement strategies."

### 6. **Function** (`function`)
Focuses on technical capabilities and functions.

**Example Output:**
> "This intent represents interest in data analytics capabilities and business intelligence implementation. It encompasses data collection and processing, reporting and visualization tools, and analytical insights for decision-making."

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

### Error Handling Test Curls

```bash
# Invalid request - missing required fields
curl -X POST "https://v3-custom-model-descriptor.onrender.com/v1/phase1+2/process" \
  -H "Content-Type: application/json" \
  -d '{}'

# Invalid lens type
curl -X POST "https://v3-custom-model-descriptor.onrender.com/v1/phase1+2/process" \
  -H "Content-Type: application/json" \
  -d '{
    "seed_keywords": ["test"],
    "lens_type": "invalid_lens"
  }'

# Too many seed keywords
curl -X POST "https://v3-custom-model-descriptor.onrender.com/v1/phase1+2/process" \
  -H "Content-Type: application/json" \
  -d '{
    "seed_keywords": ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5", "keyword6", "keyword7", "keyword8", "keyword9", "keyword10", "keyword11", "keyword12", "keyword13", "keyword14", "keyword15", "keyword16", "keyword17", "keyword18", "keyword19", "keyword20", "keyword21"],
    "lens_type": "service"
  }'
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

## 🔧 Advanced Usage Examples

### 1. **Legal Services Research**
```bash
curl -X POST "https://v3-custom-model-descriptor.onrender.com/v1/phase1+2/process" \
  -H "Content-Type: application/json" \
  -d '{
    "seed_keywords": ["legal support for social security disability", "disability attorney"],
    "lens_type": "service",
    "results_per_query": 25,
    "html_fetch": true
  }'
```

### 2. **Business Intelligence Tools**
```bash
curl -X POST "https://v3-custom-model-descriptor.onrender.com/v1/phase1+2/process" \
  -H "Content-Type: application/json" \
  -d '{
    "seed_keywords": ["business intelligence", "data analytics platform"],
    "lens_type": "product",
    "results_per_query": 20
  }'
```

### 3. **Marketing Technology**
```bash
curl -X POST "https://v3-custom-model-descriptor.onrender.com/v1/phase1+2/process" \
  -H "Content-Type: application/json" \
  -d '{
    "seed_keywords": ["marketing automation", "lead generation software"],
    "lens_type": "solution",
    "results_per_query": 30
  }'
```

### 4. **Healthcare Services**
```bash
curl -X POST "https://v3-custom-model-descriptor.onrender.com/v1/phase1+2/process" \
  -H "Content-Type: application/json" \
  -d '{
    "seed_keywords": ["telemedicine", "virtual healthcare"],
    "lens_type": "service",
    "results_per_query": 15
  }'
```

---

## 📊 Response Analysis

### Understanding the Response Structure

**raw_content**: Contains all extracted data from SERP analysis
- `extracted_keyphrases`: AI-extracted meaningful phrases
- `top_terms`: Most frequent individual terms
- `top_phrases`: Most frequent multi-word phrases
- `term_frequencies`: Detailed frequency counts for terms
- `phrase_frequencies`: Detailed frequency counts for phrases
- `doc_sources`: List of analyzed documents with metadata
- `total_docs`: Number of documents analyzed
- `total_text_length`: Total characters analyzed
- `evidence_count`: Number of evidence sources

**names**: Generated name suggestions for the intent
**description**: Comprehensive description using extracted keyphrases
**validation**: Quality checks on the generated description

### Example Response Analysis
```bash
# Extract just the description
curl -X POST "https://v3-custom-model-descriptor.onrender.com/v1/phase1+2/process" \
  -H "Content-Type: application/json" \
  -d '{"seed_keywords": ["email deliverability"], "lens_type": "service"}' | jq '.description'

# Extract just the keyphrases
curl -X POST "https://v3-custom-model-descriptor.onrender.com/v1/phase1+2/process" \
  -H "Content-Type: application/json" \
  -d '{"seed_keywords": ["email deliverability"], "lens_type": "service"}' | jq '.raw_content.extracted_keyphrases'

# Extract names and description
curl -X POST "https://v3-custom-model-descriptor.onrender.com/v1/phase1+2/process" \
  -H "Content-Type: application/json" \
  -d '{"seed_keywords": ["email deliverability"], "lens_type": "service"}' | jq '{names: .names, description: .description}'
```

---

## 🚀 Quick Start Guide

1. **Test the service is running:**
   ```bash
   curl -X GET "https://v3-custom-model-descriptor.onrender.com/health"
   ```

2. **Run a simple test:**
   ```bash
   curl -X POST "https://v3-custom-model-descriptor.onrender.com/v1/phase1+2/process" \
     -H "Content-Type: application/json" \
     -d '{"seed_keywords": ["email deliverability"], "lens_type": "service"}'
   ```

3. **Test different lens types:**
   ```bash
   # Try each lens type with the same keywords
   for lens in service brand event product solution function; do
     echo "Testing $lens lens:"
     curl -X POST "https://v3-custom-model-descriptor.onrender.com/v1/phase1+2/process" \
       -H "Content-Type: application/json" \
       -d "{\"seed_keywords\": [\"email deliverability\"], \"lens_type\": \"$lens\"}" | jq '.description'
     echo -e "\n"
   done
   ```

---

## 📞 Support

For issues or questions:
- **Service Status**: Check `/health` endpoint
- **Documentation**: This file
- **API Explorer**: Visit `/docs` for interactive documentation

---

*Last Updated: August 2025*
*Version: 1.2.0*
