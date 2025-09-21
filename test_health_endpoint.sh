#!/bin/bash

# Test script for custom model descriptor health endpoint
# This tests the CORS configuration and endpoint availability

echo "Testing Custom Model Descriptor Health Endpoint..."
echo "=================================================="

# Test 1: Basic health check
echo "1. Testing basic health endpoint..."
curl -X GET "https://v3-custom-model-descriptor.onrender.com/health" \
  -H "Content-Type: application/json" \
  -v

echo -e "\n\n"

# Test 2: Custom model descriptor health endpoint
echo "2. Testing custom-model-descriptor-health endpoint..."
curl -X GET "https://v3-custom-model-descriptor.onrender.com/custom-model-descriptor-health" \
  -H "Content-Type: application/json" \
  -v

echo -e "\n\n"

# Test 3: CORS preflight request
echo "3. Testing CORS preflight request..."
curl -X OPTIONS "https://v3-custom-model-descriptor.onrender.com/custom-model-descriptor-health" \
  -H "Origin: https://spark.audiencelab.io" \
  -H "Access-Control-Request-Method: GET" \
  -H "Access-Control-Request-Headers: Content-Type,Authorization" \
  -v

echo -e "\n\n"

# Test 4: Actual request with CORS headers
echo "4. Testing actual request with CORS headers..."
curl -X GET "https://v3-custom-model-descriptor.onrender.com/custom-model-descriptor-health" \
  -H "Origin: https://spark.audiencelab.io" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRyYXBldnl2YmFrcnpobXFudmRtIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTMwOTM0NTYsImV4cCI6MjA2ODY2OTQ1Nn0.2bmquNWzujFRcopi_nYigXPD2ybxZ-eObUk3SLtc4s8" \
  -v

echo -e "\n\nTest completed!"
