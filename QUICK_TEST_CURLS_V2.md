# 🚀 Quick Test Curls - Custom Model Descriptor API v2.0

**Base URL**: `https://v3-custom-model-descriptor.onrender.com`

## 🔍 Health Check
```bash
curl -X GET "https://v3-custom-model-descriptor.onrender.com/health"
```

## 🆕 New Two-Step Process Tests

### **Step 1: SERP Mining**

#### 1. **Basic SERP Mining**
```bash
curl -X POST "https://v3-custom-model-descriptor.onrender.com/v1/step1/serp-mining" \
  -H "Content-Type: application/json" \
  -d '{
    "seed_keywords": ["email deliverability"],
    "results_per_query": 10
  }'
```

#### 2. **Multiple Keywords with Full Content**
```bash
curl -X POST "https://v3-custom-model-descriptor.onrender.com/v1/step1/serp-mining" \
  -H "Content-Type: application/json" \
  -d '{
    "seed_keywords": ["assisted living", "retirement facility"],
    "results_per_query": 20,
    "html_fetch": true
  }'
```

#### 3. **Legal Services SERP Mining**
```bash
curl -X POST "https://v3-custom-model-descriptor.onrender.com/v1/step1/serp-mining" \
  -H "Content-Type: application/json" \
  -d '{
    "seed_keywords": ["legal support for social security disability"],
    "results_per_query": 15,
    "html_fetch": false
  }'
```

### **Step 2: Keyword Extraction**

#### 1. **Extract Keywords from SERP Results**
```bash
# First, get SERP results from Step 1
STEP1_RESPONSE=$(curl -X POST "https://v3-custom-model-descriptor.onrender.com/v1/step1/serp-mining" \
  -H "Content-Type: application/json" \
  -d '{
    "seed_keywords": ["email deliverability"],
    "results_per_query": 10
  }')

# Then extract keywords from those results
curl -X POST "https://v3-custom-model-descriptor.onrender.com/v1/step2/keyword-extraction" \
  -H "Content-Type: application/json" \
  -d "{
    \"serp_results\": $(echo $STEP1_RESPONSE | jq '.serp_results'),
    \"seed_keywords\": [\"email deliverability\"],
    \"extract_phrases\": true
  }"
```

#### 2. **Extract Keywords with Enhanced Processing**
```bash
# Get SERP results with full content
STEP1_RESPONSE=$(curl -X POST "https://v3-custom-model-descriptor.onrender.com/v1/step1/serp-mining" \
  -H "Content-Type: application/json" \
  -d '{
    "seed_keywords": ["assisted living", "retirement facility"],
    "results_per_query": 20,
    "html_fetch": true
  }')

# Extract keywords with enhanced processing
curl -X POST "https://v3-custom-model-descriptor.onrender.com/v1/step2/keyword-extraction" \
  -H "Content-Type: application/json" \
  -d "{
    \"serp_results\": $(echo $STEP1_RESPONSE | jq '.serp_results'),
    \"seed_keywords\": [\"assisted living\", \"retirement facility\"],
    \"extract_phrases\": true
  }"
```

## 🔄 Complete Two-Step Workflow Examples

### **Email Deliverability (Service Lens)**
```bash
# Step 1: Get SERP results
STEP1_RESPONSE=$(curl -X POST "https://v3-custom-model-descriptor.onrender.com/v1/step1/serp-mining" \
  -H "Content-Type: application/json" \
  -d '{
    "seed_keywords": ["email deliverability", "spam score"],
    "results_per_query": 15
  }')

# Step 2: Extract keywords
STEP2_RESPONSE=$(curl -X POST "https://v3-custom-model-descriptor.onrender.com/v1/step2/keyword-extraction" \
  -H "Content-Type: application/json" \
  -d "{
    \"serp_results\": $(echo $STEP1_RESPONSE | jq '.serp_results'),
    \"seed_keywords\": [\"email deliverability\", \"spam score\"],
    \"extract_phrases\": true
  }")

# Step 3: Generate description
curl -X POST "https://v3-custom-model-descriptor.onrender.com/v1/phase2/describe" \
  -H "Content-Type: application/json" \
  -d "{
    \"topic\": \"email deliverability\",
    \"lens\": \"service\",
    \"raw_content\": $(echo $STEP2_RESPONSE | jq '.raw_content')
  }"
```

### **Assisted Living (Brand Lens)**
```bash
# Step 1: Get SERP results
STEP1_RESPONSE=$(curl -X POST "https://v3-custom-model-descriptor.onrender.com/v1/step1/serp-mining" \
  -H "Content-Type: application/json" \
  -d '{
    "seed_keywords": ["assisted living", "retirement facility"],
    "results_per_query": 20,
    "html_fetch": true
  }')

# Step 2: Extract keywords
STEP2_RESPONSE=$(curl -X POST "https://v3-custom-model-descriptor.onrender.com/v1/step2/keyword-extraction" \
  -H "Content-Type: application/json" \
  -d "{
    \"serp_results\": $(echo $STEP1_RESPONSE | jq '.serp_results'),
    \"seed_keywords\": [\"assisted living\", \"retirement facility\"],
    \"extract_phrases\": true
  }")

# Step 3: Generate description
curl -X POST "https://v3-custom-model-descriptor.onrender.com/v1/phase2/describe" \
  -H "Content-Type: application/json" \
  -d "{
    \"topic\": \"assisted living\",
    \"lens\": \"brand\",
    \"raw_content\": $(echo $STEP2_RESPONSE | jq '.raw_content')
  }"
```

## 📊 Response Analysis (with jq)

### Extract Just SERP Results from Step 1
```bash
curl -X POST "https://v3-custom-model-descriptor.onrender.com/v1/step1/serp-mining" \
  -H "Content-Type: application/json" \
  -d '{"seed_keywords": ["email deliverability"], "results_per_query": 10}' | jq '.serp_results'
```

### Extract Total Docs Count from Step 1
```bash
curl -X POST "https://v3-custom-model-descriptor.onrender.com/v1/step1/serp-mining" \
  -H "Content-Type: application/json" \
  -d '{"seed_keywords": ["email deliverability"], "results_per_query": 10}' | jq '.total_docs'
```

### Extract Keyphrases from Step 2
```bash
# Get SERP results first
STEP1_RESPONSE=$(curl -X POST "https://v3-custom-model-descriptor.onrender.com/v1/step1/serp-mining" \
  -H "Content-Type: application/json" \
  -d '{"seed_keywords": ["email deliverability"], "results_per_query": 10}')

# Extract keyphrases
curl -X POST "https://v3-custom-model-descriptor.onrender.com/v1/step2/keyword-extraction" \
  -H "Content-Type: application/json" \
  -d "{
    \"serp_results\": $(echo $STEP1_RESPONSE | jq '.serp_results'),
    \"seed_keywords\": [\"email deliverability\"],
    \"extract_phrases\": true
  }" | jq '.raw_content.extracted_keyphrases'
```

### Extract Top Terms and Phrases from Step 2
```bash
# Get SERP results first
STEP1_RESPONSE=$(curl -X POST "https://v3-custom-model-descriptor.onrender.com/v1/step1/serp-mining" \
  -H "Content-Type: application/json" \
  -d '{"seed_keywords": ["email deliverability"], "results_per_query": 10}')

# Extract top terms and phrases
curl -X POST "https://v3-custom-model-descriptor.onrender.com/v1/step2/keyword-extraction" \
  -H "Content-Type: application/json" \
  -d "{
    \"serp_results\": $(echo $STEP1_RESPONSE | jq '.serp_results'),
    \"seed_keywords\": [\"email deliverability\"],
    \"extract_phrases\": true
  }" | jq '.raw_content | {top_terms, top_phrases}'
```

### Extract Document Sources from Step 2
```bash
# Get SERP results first
STEP1_RESPONSE=$(curl -X POST "https://v3-custom-model-descriptor.onrender.com/v1/step1/serp-mining" \
  -H "Content-Type: application/json" \
  -d '{"seed_keywords": ["email deliverability"], "results_per_query": 10}')

# Extract document sources
curl -X POST "https://v3-custom-model-descriptor.onrender.com/v1/step2/keyword-extraction" \
  -H "Content-Type: application/json" \
  -d "{
    \"serp_results\": $(echo $STEP1_RESPONSE | jq '.serp_results'),
    \"seed_keywords\": [\"email deliverability\"],
    \"extract_phrases\": true
  }" | jq '.raw_content.doc_sources'
```

## 🔄 Legacy Endpoints (Backward Compatibility)

### **Legacy Phase 1 (Combined)**
```bash
curl -X POST "https://v3-custom-model-descriptor.onrender.com/v1/phase1/process" \
  -H "Content-Type: application/json" \
  -d '{
    "seed_keywords": ["email deliverability"],
    "results_per_query": 10,
    "extract_phrases": true
  }'
```

### **Legacy Combined Pipeline**
```bash
curl -X POST "https://v3-custom-model-descriptor.onrender.com/v1/phase1+2/process" \
  -H "Content-Type: application/json" \
  -d '{
    "seed_keywords": ["email deliverability"],
    "lens_type": "service"
  }'
```

## 🎯 Test All Lens Types with Two-Step Process

### Bash Script to Test All Lenses
```bash
#!/bin/bash
KEYWORDS='["email deliverability"]'
BASE_URL="https://v3-custom-model-descriptor.onrender.com"

for lens in service brand event product solution function; do
  echo "=== Testing $lens lens ==="
  
  # Step 1: Get SERP results
  STEP1_RESPONSE=$(curl -X POST "$BASE_URL/v1/step1/serp-mining" \
    -H "Content-Type: application/json" \
    -d "{\"seed_keywords\": $KEYWORDS, \"results_per_query\": 10}")
  
  # Step 2: Extract keywords
  STEP2_RESPONSE=$(curl -X POST "$BASE_URL/v1/step2/keyword-extraction" \
    -H "Content-Type: application/json" \
    -d "{
      \"serp_results\": $(echo $STEP1_RESPONSE | jq '.serp_results'),
      \"seed_keywords\": $KEYWORDS,
      \"extract_phrases\": true
    }")
  
  # Step 3: Generate description
  curl -X POST "$BASE_URL/v1/phase2/describe" \
    -H "Content-Type: application/json" \
    -d "{
      \"topic\": \"email deliverability\",
      \"lens\": \"$lens\",
      \"raw_content\": $(echo $STEP2_RESPONSE | jq '.raw_content')
    }" | jq '.description'
  
  echo -e "\n"
done
```

## ⚠️ Error Testing

### Invalid Request - Missing Keywords
```bash
curl -X POST "https://v3-custom-model-descriptor.onrender.com/v1/step1/serp-mining" \
  -H "Content-Type: application/json" \
  -d '{}'
```

### Invalid Request - Too Many Keywords
```bash
curl -X POST "https://v3-custom-model-descriptor.onrender.com/v1/step1/serp-mining" \
  -H "Content-Type: application/json" \
  -d '{
    "seed_keywords": ["k1","k2","k3","k4","k5","k6","k7","k8","k9","k10","k11","k12","k13","k14","k15","k16","k17","k18","k19","k20","k21"]
  }'
```

### Invalid Step 2 Request - Missing SERP Results
```bash
curl -X POST "https://v3-custom-model-descriptor.onrender.com/v1/step2/keyword-extraction" \
  -H "Content-Type: application/json" \
  -d '{
    "seed_keywords": ["email deliverability"],
    "extract_phrases": true
  }'
```

## 🚀 Quick Start

1. **Test health**: `curl -X GET "https://v3-custom-model-descriptor.onrender.com/health"`

2. **Simple two-step test**: 
   ```bash
   # Step 1: Get SERP results
   STEP1_RESPONSE=$(curl -X POST "https://v3-custom-model-descriptor.onrender.com/v1/step1/serp-mining" \
     -H "Content-Type: application/json" \
     -d '{"seed_keywords": ["email deliverability"], "results_per_query": 10}')
   
   # Step 2: Extract keywords
   curl -X POST "https://v3-custom-model-descriptor.onrender.com/v1/step2/keyword-extraction" \
     -H "Content-Type: application/json" \
     -d "{
       \"serp_results\": $(echo $STEP1_RESPONSE | jq '.serp_results'),
       \"seed_keywords\": [\"email deliverability\"],
       \"extract_phrases\": true
     }"
   ```

3. **Get just keyphrases**:
   ```bash
   # Get SERP results first
   STEP1_RESPONSE=$(curl -X POST "https://v3-custom-model-descriptor.onrender.com/v1/step1/serp-mining" \
     -H "Content-Type: application/json" \
     -d '{"seed_keywords": ["email deliverability"], "results_per_query": 10}')
   
   # Extract just keyphrases
   curl -X POST "https://v3-custom-model-descriptor.onrender.com/v1/step2/keyword-extraction" \
     -H "Content-Type: application/json" \
     -d "{
       \"serp_results\": $(echo $STEP1_RESPONSE | jq '.serp_results'),
       \"seed_keywords\": [\"email deliverability\"],
       \"extract_phrases\": true
     }" | jq '.raw_content.extracted_keyphrases'
   ```

---

*For full documentation, see `API_DOCUMENTATION_V2.md`*
