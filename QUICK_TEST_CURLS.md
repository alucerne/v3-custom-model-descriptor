# 🚀 Quick Test Curls - Custom Model Descriptor API

**Base URL**: `https://v3-custom-model-descriptor.onrender.com`

## 🔍 Health Check
```bash
curl -X GET "https://v3-custom-model-descriptor.onrender.com/health"
```

## 🎯 Combined Pipeline Tests (Most Common)

### 1. **Email Deliverability (Service Lens)**
```bash
curl -X POST "https://v3-custom-model-descriptor.onrender.com/v1/phase1+2/process" \
  -H "Content-Type: application/json" \
  -d '{"seed_keywords": ["email deliverability"], "lens_type": "service"}'
```

### 2. **Assisted Living (Brand Lens)**
```bash
curl -X POST "https://v3-custom-model-descriptor.onrender.com/v1/phase1+2/process" \
  -H "Content-Type: application/json" \
  -d '{"seed_keywords": ["assisted living", "retirement facility"], "lens_type": "brand"}'
```

### 3. **SEO Tools (Product Lens)**
```bash
curl -X POST "https://v3-custom-model-descriptor.onrender.com/v1/phase1+2/process" \
  -H "Content-Type: application/json" \
  -d '{"seed_keywords": ["SEO tools", "keyword research"], "lens_type": "product"}'
```

### 4. **Legal Services (Service Lens)**
```bash
curl -X POST "https://v3-custom-model-descriptor.onrender.com/v1/phase1+2/process" \
  -H "Content-Type: application/json" \
  -d '{"seed_keywords": ["legal support for social security disability"], "lens_type": "service"}'
```

### 5. **Marketing Conferences (Event Lens)**
```bash
curl -X POST "https://v3-custom-model-descriptor.onrender.com/v1/phase1+2/process" \
  -H "Content-Type: application/json" \
  -d '{"seed_keywords": ["marketing conference", "digital marketing event"], "lens_type": "event"}'
```

### 6. **Customer Retention (Solution Lens)**
```bash
curl -X POST "https://v3-custom-model-descriptor.onrender.com/v1/phase1+2/process" \
  -H "Content-Type: application/json" \
  -d '{"seed_keywords": ["customer retention", "churn reduction"], "lens_type": "solution"}'
```

### 7. **Data Analytics (Function Lens)**
```bash
curl -X POST "https://v3-custom-model-descriptor.onrender.com/v1/phase1+2/process" \
  -H "Content-Type: application/json" \
  -d '{"seed_keywords": ["data analytics", "business intelligence"], "lens_type": "function"}'
```

## 🔧 Phase 1 Only (Keyword Extraction)

### Basic Keyword Extraction
```bash
curl -X POST "https://v3-custom-model-descriptor.onrender.com/v1/phase1/process" \
  -H "Content-Type: application/json" \
  -d '{
    "seed_keywords": ["email deliverability"],
    "results_per_query": 10,
    "extract_phrases": true
  }'
```

### Multiple Keywords with Full Content
```bash
curl -X POST "https://v3-custom-model-descriptor.onrender.com/v1/phase1/process" \
  -H "Content-Type: application/json" \
  -d '{
    "seed_keywords": ["assisted living", "retirement facility"],
    "results_per_query": 20,
    "html_fetch": true,
    "extract_phrases": true
  }'
```

## 📊 Response Analysis (with jq)

### Extract Just Description
```bash
curl -X POST "https://v3-custom-model-descriptor.onrender.com/v1/phase1+2/process" \
  -H "Content-Type: application/json" \
  -d '{"seed_keywords": ["email deliverability"], "lens_type": "service"}' | jq '.description'
```

### Extract Keyphrases
```bash
curl -X POST "https://v3-custom-model-descriptor.onrender.com/v1/phase1+2/process" \
  -H "Content-Type: application/json" \
  -d '{"seed_keywords": ["email deliverability"], "lens_type": "service"}' | jq '.raw_content.extracted_keyphrases'
```

### Extract Names and Description
```bash
curl -X POST "https://v3-custom-model-descriptor.onrender.com/v1/phase1+2/process" \
  -H "Content-Type: application/json" \
  -d '{"seed_keywords": ["email deliverability"], "lens_type": "service"}' | jq '{names: .names, description: .description}'
```

### Extract Top Terms and Phrases
```bash
curl -X POST "https://v3-custom-model-descriptor.onrender.com/v1/phase1+2/process" \
  -H "Content-Type: application/json" \
  -d '{"seed_keywords": ["email deliverability"], "lens_type": "service"}' | jq '.raw_content | {top_terms, top_phrases}'
```

## 🎯 Test All Lens Types

### Bash Script to Test All Lenses
```bash
#!/bin/bash
KEYWORDS='["email deliverability"]'
BASE_URL="https://v3-custom-model-descriptor.onrender.com"

for lens in service brand event product solution function; do
  echo "=== Testing $lens lens ==="
  curl -X POST "$BASE_URL/v1/phase1+2/process" \
    -H "Content-Type: application/json" \
    -d "{\"seed_keywords\": $KEYWORDS, \"lens_type\": \"$lens\"}" | jq '.description'
  echo -e "\n"
done
```

### One-liner to Test All Lenses
```bash
for lens in service brand event product solution function; do echo "=== $lens ==="; curl -X POST "https://v3-custom-model-descriptor.onrender.com/v1/phase1+2/process" -H "Content-Type: application/json" -d "{\"seed_keywords\": [\"email deliverability\"], \"lens_type\": \"$lens\"}" | jq '.description'; echo; done
```

## ⚠️ Error Testing

### Invalid Request
```bash
curl -X POST "https://v3-custom-model-descriptor.onrender.com/v1/phase1+2/process" \
  -H "Content-Type: application/json" \
  -d '{}'
```

### Invalid Lens Type
```bash
curl -X POST "https://v3-custom-model-descriptor.onrender.com/v1/phase1+2/process" \
  -H "Content-Type: application/json" \
  -d '{"seed_keywords": ["test"], "lens_type": "invalid_lens"}'
```

### Too Many Keywords
```bash
curl -X POST "https://v3-custom-model-descriptor.onrender.com/v1/phase1+2/process" \
  -H "Content-Type: application/json" \
  -d '{"seed_keywords": ["k1","k2","k3","k4","k5","k6","k7","k8","k9","k10","k11","k12","k13","k14","k15","k16","k17","k18","k19","k20","k21"], "lens_type": "service"}'
```

## 🚀 Quick Start

1. **Test health**: `curl -X GET "https://v3-custom-model-descriptor.onrender.com/health"`

2. **Simple test**: 
   ```bash
   curl -X POST "https://v3-custom-model-descriptor.onrender.com/v1/phase1+2/process" \
     -H "Content-Type: application/json" \
     -d '{"seed_keywords": ["email deliverability"], "lens_type": "service"}'
   ```

3. **Get just description**:
   ```bash
   curl -X POST "https://v3-custom-model-descriptor.onrender.com/v1/phase1+2/process" \
     -H "Content-Type: application/json" \
     -d '{"seed_keywords": ["email deliverability"], "lens_type": "service"}' | jq '.description'
   ```

---

*For full documentation, see `API_DOCUMENTATION.md`*
