# description_gotchas.py
# Validation rules for intent descriptions to ensure they are correct and focused

import re
from typing import List, Dict, Tuple

class DescriptionGotchas:
    """
    Validates intent descriptions against 5 critical gotchas to ensure they are
    correct and focused for intent classification.
    """
    
    def __init__(self):
        # Keywords that indicate audience-focused descriptions (Gotcha #2)
        self.audience_keywords = [
            "audience", "users", "people", "customers", "clients", "buyers", 
            "consumers", "professionals", "businesses", "companies", "organizations",
            "individuals", "teams", "departments", "managers", "executives",
            "developers", "marketers", "salespeople", "administrators",
            "who", "those who", "anyone who", "people who", "users who"
        ]
        
        # Keywords that indicate business model/meta descriptions (Gotcha #3)
        self.meta_keywords = [
            "luxury", "premium", "affordable", "budget", "low-cost", "high-end",
            "quality", "premium quality", "best", "top-rated", "leading",
            "enterprise", "small business", "startup", "freemium", "subscription",
            "one-time", "monthly", "annual", "pricing", "cost", "price",
            "business model", "revenue", "profit", "ROI", "investment"
        ]
        
        # Keywords that indicate explanation of intent (Gotcha #5)
        self.explanation_keywords = [
            "by focusing on", "the taxonomy", "segments", "targeting",
            "rather than", "instead of", "this includes", "this excludes",
            "the intent", "the algorithm", "measurement", "tracking",
            "classification", "segmentation", "audience targeting"
        ]
    
    def validate_description(self, description: str, topic: str) -> Dict[str, any]:
        """
        Validates a description against all 5 gotchas.
        Returns a dictionary with validation results and suggestions.
        """
        results = {
            "is_valid": True,
            "issues": [],
            "suggestions": [],
            "word_count": len(description.split()),
            "gotchas_failed": []
        }
        
        # Gotcha #1: Something to find (not too specific/obscure)
        if not self._has_sufficient_search_volume(description, topic):
            results["is_valid"] = False
            results["gotchas_failed"].append(1)
            results["issues"].append("Description may be too specific or obscure - insufficient search volume")
            results["suggestions"].append("Broaden the topic to include more common search terms")
        
        # Gotcha #2: No audience details
        audience_issues = self._check_audience_keywords(description)
        if audience_issues:
            results["is_valid"] = False
            results["gotchas_failed"].append(2)
            results["issues"].extend(audience_issues)
            results["suggestions"].append("Remove audience-focused language, focus only on the product/service")
        
        # Gotcha #3: No business model/meta descriptions
        meta_issues = self._check_meta_keywords(description)
        if meta_issues:
            results["is_valid"] = False
            results["gotchas_failed"].append(3)
            results["issues"].extend(meta_issues)
            results["suggestions"].append("Remove business model, pricing, or quality descriptors")
        
        # Gotcha #4: Not too many words
        if len(description.split()) > 50:
            results["is_valid"] = False
            results["gotchas_failed"].append(4)
            results["issues"].append(f"Description too long ({len(description.split())} words)")
            results["suggestions"].append("Keep description to 2-3 sentences maximum")
        
        # Gotcha #5: No explanation of intent
        explanation_issues = self._check_explanation_keywords(description)
        if explanation_issues:
            results["is_valid"] = False
            results["gotchas_failed"].append(5)
            results["issues"].extend(explanation_issues)
            results["suggestions"].append("Remove explanations about intent or targeting - focus only on the subject")
        
        return results
    
    def _has_sufficient_search_volume(self, description: str, topic: str) -> bool:
        """
        Quick check for sufficient search volume.
        For now, we'll use a simple heuristic based on common terms.
        """
        # Extract key terms from description
        words = re.findall(r'\b\w+\b', description.lower())
        
        # Check if description contains common, searchable terms
        common_terms = ["email", "deliverability", "service", "tool", "software", 
                       "solution", "platform", "system", "technology", "product"]
        
        # If topic is very specific and description doesn't contain common terms, flag it
        if len(words) < 5 or not any(term in words for term in common_terms):
            return False
        
        return True
    
    def _check_audience_keywords(self, description: str) -> List[str]:
        """Check for audience-focused language (Gotcha #2)"""
        issues = []
        description_lower = description.lower()
        
        for keyword in self.audience_keywords:
            if keyword in description_lower:
                issues.append(f"Contains audience keyword: '{keyword}'")
        
        return issues
    
    def _check_meta_keywords(self, description: str) -> List[str]:
        """Check for business model/meta descriptions (Gotcha #3)"""
        issues = []
        description_lower = description.lower()
        
        for keyword in self.meta_keywords:
            if keyword in description_lower:
                issues.append(f"Contains meta keyword: '{keyword}'")
        
        return issues
    
    def _check_explanation_keywords(self, description: str) -> List[str]:
        """Check for explanation of intent (Gotcha #5)"""
        issues = []
        description_lower = description.lower()
        
        for keyword in self.explanation_keywords:
            if keyword in description_lower:
                issues.append(f"Contains explanation keyword: '{keyword}'")
        
        return issues
    
    def get_validation_prompt(self) -> str:
        """
        Returns a prompt that can be added to the LLM instructions to prevent gotchas.
        """
        return """
VALIDATION RULES - Follow these exactly:

1. SOMETHING TO FIND: Ensure the topic has sufficient search volume. If too specific/obscure, broaden it.

2. NO AUDIENCE DETAILS: Do NOT include anything about who might use/buy the service. Focus ONLY on the product/service itself.

3. NO BUSINESS MODEL: Do NOT include pricing, quality descriptors, business models, or meta information.

4. CONCISE: Keep to 2-3 sentences maximum. Remove unnecessary words.

5. NO EXPLANATION: Do NOT explain intent, targeting, or classification. Focus only on the subject matter.

BAD EXAMPLES:
- "Users seeking email deliverability solutions for their marketing campaigns" (audience focus)
- "Premium email deliverability services for enterprise customers" (business model)
- "This intent captures users researching email deliverability to improve their sender reputation" (explanation)

GOOD EXAMPLES:
- "Email deliverability solutions and inbox placement optimization"
- "SPF, DKIM, and DMARC authentication for email delivery"
- "Email deliverability testing and reputation monitoring"
"""

def validate_and_fix_description(description: str, topic: str) -> Tuple[str, Dict[str, any]]:
    """
    Validates a description and attempts to fix common issues.
    Returns the fixed description and validation results.
    """
    gotchas = DescriptionGotchas()
    results = gotchas.validate_description(description, topic)
    
    if results["is_valid"]:
        return description, results
    
    # Attempt to fix common issues
    fixed_description = description
    
    # Remove audience keywords
    for keyword in gotchas.audience_keywords:
        pattern = re.compile(rf'\b{re.escape(keyword)}\b', re.IGNORECASE)
        fixed_description = pattern.sub('', fixed_description)
    
    # Remove meta keywords
    for keyword in gotchas.meta_keywords:
        pattern = re.compile(rf'\b{re.escape(keyword)}\b', re.IGNORECASE)
        fixed_description = pattern.sub('', fixed_description)
    
    # Remove explanation keywords
    for keyword in gotchas.explanation_keywords:
        pattern = re.compile(rf'\b{re.escape(keyword)}\b', re.IGNORECASE)
        fixed_description = pattern.sub('', fixed_description)
    
    # Clean up extra whitespace
    fixed_description = re.sub(r'\s+', ' ', fixed_description).strip()
    
    # Validate the fixed description
    fixed_results = gotchas.validate_description(fixed_description, topic)
    
    return fixed_description, fixed_results
