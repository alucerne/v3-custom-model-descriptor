#!/usr/bin/env python3
"""
Test script to show the exact prompts being generated for different lens types.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from writer import build_prompt

# Test data
test_bank = {
    "top_terms": ["email", "deliverability", "spam", "reputation", "inbox", "sender", "authentication", "providers", "tools", "rate"],
    "top_phrases": ["email deliverability", "your emails", "sender reputation", "inbox placement", "mailbox providers"],
    "term_frequencies": {"email": 136, "deliverability": 88, "spam": 54, "reputation": 40, "inbox": 39},
    "phrase_frequencies": {"email deliverability": 45, "your emails": 25, "sender reputation": 16, "inbox placement": 15},
    "combined_text": "Email deliverability content with SPF, DKIM, and DMARC authentication protocols...",
    "total_docs": 3,
    "total_text_length": 34038,
    "seeds": ["email deliverability"]
}

# Test different lens types
lens_types = ["service", "brand", "event", "product", "solution", "function"]

print("=" * 80)
print("EXACT PROMPTS BEING GENERATED FOR DIFFERENT LENS TYPES")
print("=" * 80)

for lens in lens_types:
    print(f"\n{'='*20} LENS TYPE: {lens.upper()} {'='*20}")
    
    prompt = build_prompt(
        topic="Email Deliverability",
        lens=lens,
        category="Marketing",
        sub_category="Email",
        bank=test_bank
    )
    
    print(prompt)
    print(f"\n{'='*60}\n")

print("=" * 80)
print("END OF PROMPTS")
print("=" * 80)
