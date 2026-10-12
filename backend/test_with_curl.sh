#!/bin/bash
# Test the profile endpoint with curl and show detailed response

echo "=========================================="
echo "Testing Profile Endpoint"
echo "=========================================="
echo ""

# Replace with your actual Supabase JWT token
TOKEN="YOUR_JWT_TOKEN_HERE"

echo "Making request to http://localhost:8000/api/v1/student/profile"
echo ""

curl -v \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  http://localhost:8000/api/v1/student/profile

echo ""
echo ""
echo "=========================================="
echo "Test Complete"
echo "=========================================="
