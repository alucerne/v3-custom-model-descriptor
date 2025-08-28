#!/usr/bin/env python3
"""
Test script to demonstrate Description Gotchas validation with various examples.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from description_gotchas import DescriptionGotchas, validate_and_fix_description

def test_gotchas():
    """Test the Description Gotchas validation with various examples."""
    
    gotchas = DescriptionGotchas()
    
    # Test cases with different gotchas
    test_cases = [
        {
            "name": "Good Description",
            "description": "Email deliverability solutions and inbox placement optimization",
            "topic": "Email Deliverability"
        },
        {
            "name": "Gotcha #2 - Audience Focus",
            "description": "Users seeking email deliverability solutions for their marketing campaigns",
            "topic": "Email Deliverability"
        },
        {
            "name": "Gotcha #3 - Business Model",
            "description": "Premium email deliverability services for enterprise customers",
            "topic": "Email Deliverability"
        },
        {
            "name": "Gotcha #4 - Too Many Words",
            "description": "This comprehensive email deliverability solution provides advanced features including SPF, DKIM, and DMARC authentication protocols, sender reputation monitoring, inbox placement optimization, bounce rate analysis, spam score checking, and detailed reporting capabilities for enterprise-level email marketing campaigns",
            "topic": "Email Deliverability"
        },
        {
            "name": "Gotcha #5 - Explanation",
            "description": "This intent captures users researching email deliverability to improve their sender reputation and avoid spam filters",
            "topic": "Email Deliverability"
        },
        {
            "name": "Multiple Gotchas",
            "description": "Premium email deliverability services for enterprise users who want to improve their sender reputation and avoid spam filters, with advanced features and comprehensive reporting",
            "topic": "Email Deliverability"
        }
    ]
    
    print("=" * 80)
    print("DESCRIPTION GOTCHAS VALIDATION TEST")
    print("=" * 80)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}")
        print("-" * 60)
        print(f"Original: {test_case['description']}")
        
        # Validate the description
        fixed_description, results = validate_and_fix_description(
            test_case['description'], 
            test_case['topic']
        )
        
        print(f"Word Count: {results['word_count']}")
        print(f"Valid: {results['is_valid']}")
        
        if results['issues']:
            print(f"Failed Gotchas: {results['gotchas_failed']}")
            print("Issues:")
            for issue in results['issues']:
                print(f"  - {issue}")
            print("Suggestions:")
            for suggestion in results['suggestions']:
                print(f"  - {suggestion}")
        
        if fixed_description != test_case['description']:
            print(f"Fixed: {fixed_description}")
        
        print()

if __name__ == "__main__":
    test_gotchas()
