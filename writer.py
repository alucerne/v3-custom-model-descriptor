import os
import json
import google.generativeai as genai
from typing import Dict, Any, Optional, List
import re
from description_gotchas import DescriptionGotchas, validate_and_fix_description

# Gemini configuration
genai.configure(api_key=os.getenv("GEMINI_API_KEY", "AIzaSyAzP_pun21tcQiH2_X0AWbeDeI8iVYt7rM"))

# Constants
AUDIENCE_TERMS = [
    "audience", "target", "demographic", "segment", "user", "customer", 
    "prospect", "buyer", "consumer", "client", "subscriber", "member"
]

META_ADJ = [
    "best", "top", "leading", "premium", "quality", "professional", 
    "expert", "advanced", "comprehensive", "complete", "full", "comprehensive"
]

def build_prompt(topic: str, lens: str, category: Optional[str], sub_category: Optional[str], bank: Dict) -> str:
    """
    Build a lens-specific prompt for the LLM using enhanced raw content data.
    """
    # Enhanced content from raw extraction
    top_terms = bank.get("top_terms", [])
    top_phrases = bank.get("top_phrases", [])
    term_frequencies = bank.get("term_frequencies", {})
    phrase_frequencies = bank.get("phrase_frequencies", {})
    combined_text = bank.get("combined_text", "")
    total_docs = bank.get("total_docs", 0)
    total_text_length = bank.get("total_text_length", 0)
    
    # Get top frequency terms and phrases for context
    top_freq_terms = sorted(term_frequencies.items(), key=lambda x: x[1], reverse=True)[:15]
    top_freq_phrases = sorted(phrase_frequencies.items(), key=lambda x: x[1], reverse=True)[:10]

    # Enhanced content context with extracted keyphrases
    extracted_keyphrases = bank.get("extracted_keyphrases", [])
    content_context = f"""
CONTENT ANALYSIS:
- Documents analyzed: {total_docs}
- Total text length: {total_text_length:,} characters
- Seed keywords: {bank.get("seeds", [])}
- EXTRACTED KEYPHRASES: {extracted_keyphrases[:15]}
- Top frequency terms: {top_terms[:10]}
- Top frequency phrases: {top_phrases[:8]}
- Most frequent terms: {[term for term, freq in top_freq_terms[:8]]}
- Most frequent phrases: {[phrase for phrase, freq in top_freq_phrases[:5]]}
"""

    # Get validation rules
    gotchas = DescriptionGotchas()
    validation_rules = gotchas.get_validation_prompt()
    
    # Lens-specific prompts
    if lens.lower() == "service":
        return f"""You are an expert marketer creating an audience using intent to target prospects.

Here's an intent topic, and description.

Topic: {topic}
Category: {category or ""}
SubCategory: {sub_category or ""}

{content_context}

Use the related information to recommend three improved names that will be used by a large language classification model to analyze intent using urls and domain traffic. IMPORTANT: Generate names that are readable and properly formatted with spaces between words (e.g., "Roofing System Installation" not "RoofingSystemInstallationAndRepairIntent").
Recommend a two sentence description of the service using related LSI keywords and SEO best practices specific to the service. IMPORTANT: Use specific keyphrases from the EXTRACTED KEYPHRASES list in your description. Start with "This intent represents interest in..." and focus on technical/business aspects, not marketing language. The second sentence should start with "It encompasses..." and list specific implementation details. Make descriptions comprehensive and detailed - include specific implementation details, methodologies, and technical capabilities. Do not include details about the audience.

{validation_rules}

Return Data in the following format:
NAME1 : RECOMMENDED NAME
NAME2 : RECOMMENDED NAME
NAME3 : RECOMMENDED NAME
DESCRIPTION: RECOMMENDED DESCRIPTION"""

    elif lens.lower() == "brand":
        return f"""You are an expert marketer creating an audience using intent to target prospects.

Here's an intent brand, and description.
Brand: {topic}
Brand Description: {combined_text[:500]}...

{content_context}

Use the related information to recommend three improved names that will be used by a large language classification model to analyze intent using urls and domain traffic. Include enough keywords in the name to uniquely identify that brand compared to other common uses of the words in the brand name.
Recommend a two sentence description of the intent using related LSI keywords and SEO best practices uniquely identify that brand. IMPORTANT: Use specific keyphrases from the EXTRACTED KEYPHRASES list in your description. Start with "This intent represents interest in..." and focus on technical/business aspects, not marketing language. The second sentence should start with "It encompasses..." and list specific implementation details. Make descriptions comprehensive and detailed - include specific implementation details, methodologies, and technical capabilities. Do not include details about the audience.

{validation_rules}

Return Data in the following format:
NAME1 : RECOMMENDED NAME
NAME2 : RECOMMENDED NAME
NAME3 : RECOMMENDED NAME
DESCRIPTION: RECOMMENDED DESCRIPTION"""

    elif lens.lower() == "event":
        return f"""You are an expert marketer creating an audience using intent to target prospects.

Here's an event you'd like to track intent for, and a description.
Event: {topic}    
Event Description: {combined_text[:500]}...   
{content_context}

Use the related information to recommend three improved names that will be used by a large language classification model to analyze intent using urls and domain traffic. Include enough keywords in the name to uniquely identify that event compared to other common uses of the words in the event name.
Recommend a two sentence description of the intent using related LSI keywords and SEO best practices that are specific to the event. IMPORTANT: Use specific keyphrases from the EXTRACTED KEYPHRASES list in your description. Start with "This intent represents interest in..." and focus on technical/business aspects, not marketing language. The second sentence should start with "It encompasses..." and list specific implementation details. Make descriptions comprehensive and detailed - include specific implementation details, methodologies, and technical capabilities. Do not include details about the audience.

{validation_rules}

Return Data in the following format:   
NAME1 : RECOMMENDED NAME   
NAME2 : RECOMMENDED NAME   
NAME3 : RECOMMENDED NAME   
DESCRIPTION: RECOMMENDED DESCRIPTION"""

    elif lens.lower() == "product":
        return f"""You are an expert marketer creating an audience using intent to target prospects.

Here's an intent product, and description.   
Product: {topic}   
Product Description: {combined_text[:500]}...  
{content_context}

Use the related information to recommend three improved names that will be used by a large language classification model to analyze intent using urls and domain traffic. Include enough keywords in the name to uniquely identify that product compared to other common uses of the words in the product name.
Recommend a two sentence description of the intent using related LSI keywords and SEO best practices for that product. IMPORTANT: Use specific keyphrases from the EXTRACTED KEYPHRASES list in your description. Start with "This intent represents interest in..." and focus on technical/business aspects, not marketing language. The second sentence should start with "It encompasses..." and list specific implementation details. Make descriptions comprehensive and detailed - include specific implementation details, methodologies, and technical capabilities. Do not include details about the audience.

{validation_rules}

Return Data in the following format:    
NAME1 : RECOMMENDED NAME    
NAME2 : RECOMMENDED NAME    
NAME3 : RECOMMENDED NAME    
DESCRIPTION: RECOMMENDED DESCRIPTION"""

    elif lens.lower() == "solution":
        return f"""You are an expert marketer creating an audience using intent to target prospects.

Here's an intent solution, and description.   
Solution: {topic} 
Solution Description: {combined_text[:500]}...
{content_context}

Use the related information to recommend three improved names that will be used by a large language classification model to analyze intent using urls and domain traffic. Include enough keywords in the name to uniquely identify that solution compared to other common uses of the words in the solution name.
Recommend a two sentence description of the intent using related LSI keywords and SEO best practices specific to the solution. IMPORTANT: Use specific keyphrases from the EXTRACTED KEYPHRASES list in your description. Start with "This intent represents interest in..." and focus on technical/business aspects, not marketing language. The second sentence should start with "It encompasses..." and list specific implementation details. Make descriptions comprehensive and detailed - include specific implementation details, methodologies, and technical capabilities. Do not include details about the audience.

{validation_rules}

Return Data in the following format:  

NAME1 : RECOMMENDED NAME  
NAME2 : RECOMMENDED NAME  
NAME3 : RECOMMENDED NAME  
DESCRIPTION: RECOMMENDED DESCRIPTION"""

    elif lens.lower() == "function":
        return f"""You are an expert marketer creating an audience using intent to target prospects.

Here's an intent of a technical concept or function, and a description of the desired user intent.
Technical Concept/Function: {topic}
Description of Intent: {combined_text[:500]}...
{content_context}

Use the related information to recommend three improved names that will be used by a large language classification model to analyze intent using URLs and domain traffic. Include enough keywords in the name to specify a particular intent related to this concept, distinguishing it from other contexts or applications of the same function (e.g., distinguishing "SSL certificate providers" from "SSL implementation tutorials").
Recommend a two-sentence description of the intent using related LSI keywords and SEO best practices specific to this technical concept. IMPORTANT: Use specific keyphrases from the EXTRACTED KEYPHRASES list in your description. Start with "This intent represents interest in..." and focus on technical/business aspects, not marketing language. The second sentence should start with "It encompasses..." and list specific implementation details. Make descriptions comprehensive and detailed - include specific implementation details, methodologies, and technical capabilities. Do not include details about the audience.

{validation_rules}

Return Data in the following format:  

NAME1 : RECOMMENDED NAME  
NAME2 : RECOMMENDED NAME  
NAME3 : RECOMMENDED NAME  
DESCRIPTION: RECOMMENDED DESCRIPTION"""

    else:
        # Default fallback
        return f"""You are an expert marketer creating an audience using intent to target prospects.

Here's an intent topic, and description.

Topic: {topic}
Lens: {lens}
Category/SubCategory: {category or ""} / {sub_category or ""}

{content_context}

Use the related information to recommend three improved names that will be used by a large language classification model to analyze intent using urls and domain traffic. IMPORTANT: Generate names that are readable and properly formatted with spaces between words (e.g., "Roofing System Installation" not "RoofingSystemInstallationAndRepairIntent").
Recommend a two sentence description using related LSI keywords and SEO best practices specific to the topic. IMPORTANT: Use specific keyphrases from the EXTRACTED KEYPHRASES list in your description. Start with "This intent represents interest in..." and focus on technical/business aspects, not marketing language. The second sentence should start with "It encompasses..." and list specific implementation details. Make descriptions comprehensive and detailed - include specific implementation details, methodologies, and technical capabilities. Do not include details about the audience.

{validation_rules}

Return Data in the following format:
NAME1 : RECOMMENDED NAME
NAME2 : RECOMMENDED NAME
NAME3 : RECOMMENDED NAME
DESCRIPTION: RECOMMENDED DESCRIPTION"""

def write_description(topic: str, lens: str, category: Optional[str], sub_category: Optional[str], bank: Dict) -> str:
    """
    Generate a description using the LLM with enhanced raw content data.
    """
    prompt = build_prompt(topic, lens, category, sub_category, bank)
    
    try:
        print(f"Calling Gemini with prompt length: {len(prompt)}")
        print(f"=== FULL PROMPT ===")
        print(prompt)
        print(f"=== END PROMPT ===")
        
        # Create the full prompt with system message
        full_prompt = f"""You are an expert marketer and intent classification specialist. Follow the exact format requested in the prompt. Be specific and concise. Focus on creating audience segments for targeting prospects, not describing the audience itself.

CRITICAL: When generating descriptions, you MUST use specific keyphrases from the EXTRACTED KEYPHRASES list provided in the content analysis. Do not create generic descriptions - use the exact extracted keyphrases to ensure accuracy and specificity.

DESCRIPTION FORMAT: Start with "This intent represents interest in..." and focus on the technical/business aspects, not marketing language. The second sentence should start with "It encompasses..." and list specific implementation details, methodologies, and capabilities mentioned in the extracted keyphrases. 

STRUCTURE: 
- First sentence: Explain WHAT it's used for and WHERE/WHY (can be longer)
- Second sentence: Explain HOW it's implemented with specific technical/business details (can be longer)

Make descriptions comprehensive and detailed like the JWT example - include specific implementation details, methodologies, and technical capabilities.

MANDATORY: You MUST include at least 3-4 specific keyphrases from the EXTRACTED KEYPHRASES list in your description. Do not paraphrase or generalize - use the exact keyphrases as they appear in the list.

{prompt}"""
        
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(full_prompt)
        result = response.text.strip()
        print(f"Gemini response: {result}")
        
        # Parse the structured response to extract description
        description = parse_structured_response(result, "DESCRIPTION")
        if description:
            # Validate and fix the description using gotchas
            fixed_description, validation_results = validate_and_fix_description(description, topic)
            
            # Log validation results
            if not validation_results["is_valid"]:
                print(f"Description validation failed: {validation_results['issues']}")
                print(f"Fixed description: {fixed_description}")
            
            return fixed_description
        else:
            # If parsing fails, return the full response
            return result
    except Exception as e:
        print(f"Error calling Gemini: {e}")
        # Fallback to generate a better description using the raw content data
        return generate_fallback_description(topic, lens, bank)

def parse_structured_response(response: str, field: str) -> str:
    """
    Parse the structured response to extract specific fields.
    """
    lines = response.split('\n')
    for line in lines:
        line = line.strip()
        if line.startswith(f"{field}:"):
            return line[len(f"{field}:"):].strip()
    return ""

def format_name(name: str) -> str:
    """
    Format a name by adding spaces before capital letters and cleaning up formatting.
    Example: 'RoofingSystemInstallationAndRepairIntent' -> 'Roofing System Installation And Repair Intent'
    """
    if not name:
        return name
    
    # Add space before capital letters (except the first character)
    # Use a simpler approach that works with older Python versions
    formatted = ''
    for i, char in enumerate(name):
        if i > 0 and char.isupper():
            # Check if previous character is also uppercase (acronym) or lowercase
            prev_char = name[i-1]
            if prev_char.isupper() and i < len(name) - 1 and name[i+1].islower():
                # This is the start of a new word after an acronym
                formatted += ' ' + char
            elif prev_char.islower():
                # This is the start of a new word after lowercase
                formatted += ' ' + char
            else:
                # This is part of an acronym, don't add space
                formatted += char
        else:
            formatted += char
    
    # Clean up multiple spaces
    formatted = re.sub(r'\s+', ' ', formatted)
    
    # Remove common suffixes that shouldn't be in the name
    formatted = re.sub(r'\s+(Intent|Service|System|Platform|Tool|Solution)$', '', formatted, flags=re.IGNORECASE)
    
    return formatted.strip()

def extract_names_from_response(response: str) -> List[str]:
    """
    Extract names from the structured response and format them properly.
    """
    names = []
    lines = response.split('\n')
    for line in lines:
        line = line.strip()
        if line.startswith("NAME") and ":" in line:
            name = line.split(":", 1)[1].strip()
            if name:
                # Format the name to add proper spacing
                formatted_name = format_name(name)
                names.append(formatted_name)
    return names[:3]  # Return up to 3 names

def generate_fallback_description(topic: str, lens: str, bank: Dict) -> str:
    """
    Generate a fallback description using the raw content data when Gemini API is not available.
    """
    top_terms = bank.get("top_terms", [])
    top_phrases = bank.get("top_phrases", [])
    term_frequencies = bank.get("term_frequencies", {})
    seeds = bank.get("seeds", [])
    
    # Filter out common stop words and get meaningful terms
    stop_words = {'and', 'the', 'for', 'with', 'that', 'this', 'are', 'can', 'from', 'have', 'they', 'will', 'more', 'also', 'into', 'only', 'first', 'two', 'new', 'one', 'time', 'way', 'now', 'just', 'like', 'get', 'very', 'make', 'over', 'think', 'take', 'most', 'even', 'though', 'find', 'day', 'still', 'here', 'thing', 'give', 'many', 'well', 'only', 'those', 'tell', 'very', 'work', 'life', 'me', 'system', 'each', 'ask', 'group', 'seem', 'number', 'world', 'area', 'company', 'fact', 'hand', 'old', 'place', 'small', 'big', 'high', 'right', 'different', 'large', 'next', 'early', 'young', 'important', 'few', 'public', 'bad', 'same', 'able', 'above', 'across', 'after', 'against', 'along', 'among', 'around', 'before', 'behind', 'below', 'beneath', 'beside', 'between', 'beyond', 'during', 'except', 'inside', 'near', 'off', 'onto', 'outside', 'over', 'past', 'since', 'through', 'throughout', 'toward', 'under', 'underneath', 'until', 'up', 'upon', 'within', 'without', 'your', 'you', 'it', 'is', 'in', 'to', 'of', 'a', 'an', 'as', 'at', 'be', 'by', 'do', 'go', 'he', 'if', 'my', 'no', 'on', 'or', 'so', 'up', 'we', 'am', 'an', 'as', 'at', 'be', 'by', 'do', 'go', 'he', 'if', 'my', 'no', 'on', 'or', 'so', 'up', 'we'}
    
    relevant_terms = [term for term in top_terms[:8] if term.lower() not in stop_words and len(term) > 2]
    relevant_phrases = [phrase for phrase in top_phrases[:4] if len(phrase.split()) >= 2]
    
    # Create a specific description using the content data
    if relevant_terms and relevant_phrases:
        primary_phrase = relevant_phrases[0]
        key_terms = relevant_terms[:4]
        
        # Create a more specific description
        description = f"This audience researches {primary_phrase} solutions and evaluates {', '.join(key_terms[:2])} technologies. "
        
        if len(key_terms) > 2:
            description += f"They analyze {key_terms[2]} and {key_terms[3] if len(key_terms) > 3 else 'related'} capabilities to optimize {primary_phrase} performance and improve {relevant_terms[0]} outcomes."
        else:
            description += f"They analyze {primary_phrase} tools and capabilities to optimize performance and improve {relevant_terms[0]} outcomes."
    else:
        # Fallback for minimal data
        seed_keyword = seeds[0] if seeds else topic.lower()
        description = f"This audience researches {seed_keyword} solutions and evaluates related technologies to optimize performance and achieve specific business outcomes."
    
    return description

def validate_and_repair(description: str, bank: Dict) -> str:
    """
    Validate and repair the description to ensure quality.
    """
    # Temporarily disable validation to see raw LLM output
    print(f"Raw LLM description: {description}")
    
    # For now, just return the description as-is to see what's being generated
    return description

def write_name(topic: str, lens: str, category: Optional[str], sub_category: Optional[str], bank: Dict) -> List[str]:
    """
    Generate names using the LLM with the same structured response format.
    """
    prompt = build_prompt(topic, lens, category, sub_category, bank)
    
    try:
        print(f"Calling Gemini for names with prompt length: {len(prompt)}")
        print(f"=== FULL PROMPT FOR NAMES ===")
        print(prompt)
        print(f"=== END PROMPT FOR NAMES ===")
        
        # Create the full prompt with system message
        full_prompt = f"""You are an intent classification specialist. Follow the exact format requested in the prompt. Be specific and concise.

IMPORTANT NAME FORMATTING: Generate names that are readable and properly formatted with spaces between words. Avoid camelCase or concatenated words. Use natural language formatting like "Roofing System Installation" instead of "RoofingSystemInstallationAndRepairIntent".

{prompt}"""
        
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(full_prompt)
        result = response.text.strip()
        print(f"Gemini names response: {result}")
        
        # Extract names from the structured response
        names = extract_names_from_response(result)
        if names:
            return names
        else:
            # Fallback names
            return [f"{topic} Option 1", f"{topic} Option 2", f"{topic} Option 3"]
    except Exception as e:
        print(f"Error calling Gemini for name generation: {e}")
        return [f"{topic} Option 1", f"{topic} Option 2", f"{topic} Option 3"]