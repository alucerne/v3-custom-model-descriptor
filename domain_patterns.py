# domain_patterns.py
# Domain-specific patterns for different business verticals
# Provides specialized keyword extraction patterns for various industries

from typing import Dict, List, Set
import re

# Domain detection patterns
DOMAIN_DETECTION_PATTERNS = {
    "email_deliverability": [
        r"\b(email|mail)\s+(deliverability|delivery|inbox|spam)\b",
        r"\b(sender|domain|ip)\s+reputation\b",
        r"\b(spf|dkim|dmarc)\b",
        r"\b(bounce|open|click)\s+rate\b"
    ],
    
    "seo_marketing": [
        r"\b(seo|search\s+engine)\s+(optimization|ranking)\b",
        r"\b(keyword|backlink|link\s+building)\b",
        r"\b(google|bing|yahoo)\s+(ranking|algorithm)\b",
        r"\b(page\s+rank|domain\s+authority)\b"
    ],
    
    "social_media": [
        r"\b(social\s+media|facebook|instagram|twitter|linkedin)\s+(marketing|management)\b",
        r"\b(engagement|follower|post|content)\s+(rate|growth|strategy)\b",
        r"\b(influencer|viral|trending)\b"
    ],
    
    "ecommerce": [
        r"\b(ecommerce|online\s+store|shopify|woocommerce)\b",
        r"\b(payment|checkout|cart|inventory)\s+(system|platform)\b",
        r"\b(product|catalog|pricing)\s+(management|optimization)\b"
    ],
    
    "crm_sales": [
        r"\b(crm|customer\s+relationship)\s+(management|system|platform)\b",
        r"\b(sales|lead|prospect)\s+(management|tracking|automation)\b",
        r"\b(pipeline|funnel|conversion)\s+(management|optimization)\b"
    ],
    
    "analytics_data": [
        r"\b(analytics|data|business\s+intelligence)\s+(platform|tool|dashboard)\b",
        r"\b(reporting|metrics|kpi|dashboard)\s+(tool|platform)\b",
        r"\b(big\s+data|machine\s+learning|ai)\s+(platform|solution)\b"
    ],
    
    "cybersecurity": [
        r"\b(cybersecurity|security|threat|vulnerability)\s+(management|platform|tool)\b",
        r"\b(firewall|antivirus|malware|phishing)\s+(protection|detection)\b",
        r"\b(compliance|gdpr|hipaa|sox)\s+(compliance|management)\b"
    ],
    
    "project_management": [
        r"\b(project\s+management|task|workflow)\s+(tool|platform|software)\b",
        r"\b(agile|scrum|kanban)\s+(management|tool|platform)\b",
        r"\b(collaboration|team|communication)\s+(tool|platform)\b"
    ],
    
    "hr_recruitment": [
        r"\b(hr|human\s+resources|recruitment|hiring)\s+(software|platform|tool)\b",
        r"\b(applicant|candidate|resume)\s+(tracking|management|screening)\b",
        r"\b(employee|performance|payroll)\s+(management|system)\b"
    ],
    
    "accounting_finance": [
        r"\b(accounting|bookkeeping|financial)\s+(software|platform|tool)\b",
        r"\b(invoice|expense|budget)\s+(management|tracking|automation)\b",
        r"\b(tax|compliance|audit)\s+(software|platform)\b"
    ],
    
    "legal_social_services": [
        r"\b(legal|law|attorney|lawyer)\s+(services|assistance|representation|support)\b",
        r"\b(social\s+security|ssi|ssdi)\s+(disability|benefits|assistance)\b",
        r"\b(disability|disabilities)\s+(benefits|assistance|representation|legal)\b",
        r"\b(government|public)\s+(benefits|assistance|services)\b",
        r"\b(appeal|appeals)\s+(process|hearing|representation)\b",
        r"\b(administrative|law)\s+(judge|hearing|process)\b",
        r"\b(medical|health)\s+(evidence|records|documentation)\b",
        r"\b(legal\s+aid|pro\s+bono)\s+(services|assistance)\b",
        r"\b(civil|legal)\s+(rights|services|assistance)\b",
        r"\b(income|financial)\s+(assistance|support|benefits)\b"
    ]
}

# Domain-specific meaningful patterns
DOMAIN_PATTERNS = {
    "email_deliverability": [
        # Core concepts
        r"\b(email|mail)\s+(deliverability|delivery|inbox|spam|reputation)\b",
        r"\b(sender|domain|ip)\s+(reputation|authentication|verification)\b",
        r"\b(spf|dkim|dmarc|authentication|verification)\b",
        r"\b(inbox|spam|folder|placement|delivery)\s+(rate|score|test)\b",
        r"\b(email|mail)\s+(service|provider|tool|platform)\b",
        r"\b(cold|bulk|mass)\s+(email|mail)\b",
        r"\b(email|mail)\s+(campaign|marketing|automation)\b",
        
        # Technical terms
        r"\b(bounce|bounced|bouncing)\s+(rate|rates|email|emails)\b",
        r"\b(open|opened|opening)\s+(rate|rates|email|emails)\b",
        r"\b(click|clicked|clicking)\s+(rate|rates|through|throughs)\b",
        r"\b(unsubscribe|unsubscribed|unsubscribing)\s+(rate|rates)\b",
        r"\b(spam|junk)\s+(filter|filters|folder|folders)\b",
        r"\b(blacklist|whitelist|greylist)\b",
        r"\b(mailbox|mailboxes)\s+(provider|providers)\b",
        r"\b(postmaster|postmasters)\s+(tool|tools)\b",
        
        # Authentication and security
        r"\b(authentication|authenticated|authenticating)\s+(protocol|protocols)\b",
        r"\b(verification|verified|verifying)\s+(process|processes)\b",
        r"\b(encryption|encrypted|encrypting)\s+(email|emails)\b",
        r"\b(ssl|tls)\s+(certificate|certificates)\b",
        
        # Metrics and monitoring
        r"\b(delivery|delivered|delivering)\s+(rate|rates|status)\b",
        r"\b(reputation|reputations)\s+(score|scores|monitoring)\b",
        r"\b(engagement|engaged|engaging)\s+(rate|rates|metrics)\b",
        r"\b(performance|performing)\s+(metrics|monitoring)\b"
    ],
    
    "seo_marketing": [
        # Core SEO concepts
        r"\b(seo|search\s+engine)\s+(optimization|ranking|performance)\b",
        r"\b(keyword|keywords)\s+(research|optimization|ranking)\b",
        r"\b(backlink|backlinks|link\s+building)\b",
        r"\b(on-page|off-page)\s+(seo|optimization)\b",
        r"\b(technical|local|mobile)\s+(seo|optimization)\b",
        
        # Search engines and algorithms
        r"\b(google|bing|yahoo)\s+(ranking|algorithm|update)\b",
        r"\b(page\s+rank|domain\s+authority|page\s+authority)\b",
        r"\b(core\s+web\s+vitals|page\s+speed|mobile\s+friendly)\b",
        
        # Content and keywords
        r"\b(long-tail|short-tail)\s+(keyword|keywords)\b",
        r"\b(content|content\s+marketing)\s+(optimization|strategy)\b",
        r"\b(meta|title|description)\s+(tag|tags|optimization)\b",
        r"\b(schema|structured\s+data|rich\s+snippets)\b"
    ],
    
    "social_media": [
        # Platforms
        r"\b(facebook|instagram|twitter|linkedin|tiktok|youtube)\s+(marketing|management|strategy)\b",
        r"\b(social\s+media|social)\s+(marketing|management|strategy|platform)\b",
        
        # Engagement metrics
        r"\b(engagement|follower|post|content)\s+(rate|growth|strategy|optimization)\b",
        r"\b(like|share|comment|retweet)\s+(rate|engagement)\b",
        r"\b(reach|impression|visibility)\s+(optimization|strategy)\b",
        
        # Content and campaigns
        r"\b(content|post|story|reel)\s+(creation|scheduling|automation)\b",
        r"\b(influencer|viral|trending)\s+(marketing|campaign)\b",
        r"\b(social\s+media|social)\s+(advertising|ads|campaign)\b",
        
        # Analytics and monitoring
        r"\b(social\s+media|social)\s+(analytics|monitoring|tracking)\b",
        r"\b(sentiment|brand|reputation)\s+(analysis|monitoring)\b"
    ],
    
    "ecommerce": [
        # Platforms and systems
        r"\b(ecommerce|online\s+store|shopify|woocommerce|magento)\s+(platform|solution)\b",
        r"\b(payment|checkout|cart)\s+(system|platform|gateway)\b",
        r"\b(inventory|product|catalog)\s+(management|system|platform)\b",
        
        # Sales and conversion
        r"\b(conversion|sales|revenue)\s+(optimization|tracking|analytics)\b",
        r"\b(cart|checkout|abandonment)\s+(recovery|optimization)\b",
        r"\b(product|pricing)\s+(optimization|strategy)\b",
        
        # Customer experience
        r"\b(customer|user)\s+(experience|journey|satisfaction)\b",
        r"\b(review|rating|feedback)\s+(management|system)\b",
        r"\b(shipping|delivery|fulfillment)\s+(management|optimization)\b"
    ],
    
    "crm_sales": [
        # CRM systems
        r"\b(crm|customer\s+relationship)\s+(management|system|platform|software)\b",
        r"\b(sales|lead|prospect)\s+(management|tracking|automation|pipeline)\b",
        r"\b(contact|customer|client)\s+(management|database|tracking)\b",
        
        # Sales processes
        r"\b(pipeline|funnel|conversion)\s+(management|optimization|tracking)\b",
        r"\b(lead|prospect|opportunity)\s+(scoring|qualification|nurturing)\b",
        r"\b(sales|revenue)\s+(forecasting|analytics|reporting)\b",
        
        # Automation and workflows
        r"\b(sales|marketing)\s+(automation|workflow|process)\b",
        r"\b(email|campaign)\s+(automation|sequence|drip)\b",
        r"\b(task|activity|follow-up)\s+(automation|reminder)\b"
    ],
    
    "analytics_data": [
        # Analytics platforms
        r"\b(analytics|data|business\s+intelligence)\s+(platform|tool|dashboard|solution)\b",
        r"\b(reporting|metrics|kpi|dashboard)\s+(tool|platform|system)\b",
        r"\b(data|business)\s+(visualization|dashboard|reporting)\b",
        
        # Data types and sources
        r"\b(big\s+data|machine\s+learning|ai|artificial\s+intelligence)\s+(platform|solution|tool)\b",
        r"\b(data|database)\s+(warehouse|lake|mining|analysis)\b",
        r"\b(real-time|realtime)\s+(analytics|monitoring|tracking)\b",
        
        # Metrics and KPIs
        r"\b(performance|business|operational)\s+(metrics|kpis|analytics)\b",
        r"\b(predictive|prescriptive|descriptive)\s+(analytics|analysis)\b"
    ],
    
    "cybersecurity": [
        # Security platforms
        r"\b(cybersecurity|security|threat|vulnerability)\s+(management|platform|tool|solution)\b",
        r"\b(firewall|antivirus|malware|phishing)\s+(protection|detection|prevention)\b",
        r"\b(security|cyber)\s+(monitoring|incident|response)\b",
        
        # Compliance and governance
        r"\b(compliance|gdpr|hipaa|sox|pci)\s+(compliance|management|monitoring)\b",
        r"\b(security|cyber)\s+(policy|governance|risk)\s+(management)\b",
        r"\b(identity|access)\s+(management|authentication|authorization)\b",
        
        # Threat detection
        r"\b(threat|intrusion|anomaly)\s+(detection|prevention|response)\b",
        r"\b(security|cyber)\s+(audit|assessment|testing)\b"
    ],
    
    "project_management": [
        # PM platforms
        r"\b(project\s+management|task|workflow)\s+(tool|platform|software|system)\b",
        r"\b(agile|scrum|kanban)\s+(management|tool|platform|methodology)\b",
        r"\b(collaboration|team|communication)\s+(tool|platform|software)\b",
        
        # Project processes
        r"\b(project|task)\s+(planning|scheduling|tracking|monitoring)\b",
        r"\b(resource|time|budget)\s+(management|tracking|allocation)\b",
        r"\b(risk|issue|change)\s+(management|tracking|monitoring)\b",
        
        # Team collaboration
        r"\b(team|collaboration|communication)\s+(management|platform|tool)\b",
        r"\b(document|file)\s+(management|sharing|collaboration)\b"
    ],
    
    "hr_recruitment": [
        # HR platforms
        r"\b(hr|human\s+resources|recruitment|hiring)\s+(software|platform|tool|system)\b",
        r"\b(applicant|candidate|resume)\s+(tracking|management|screening|system)\b",
        r"\b(employee|performance|payroll)\s+(management|system|platform)\b",
        
        # Recruitment processes
        r"\b(job|position|vacancy)\s+(posting|management|tracking)\b",
        r"\b(interview|screening|assessment)\s+(management|scheduling|tracking)\b",
        r"\b(onboarding|offboarding)\s+(process|management|automation)\b",
        
        # Employee management
        r"\b(performance|appraisal|review)\s+(management|tracking|system)\b",
        r"\b(attendance|time|leave)\s+(management|tracking|system)\b",
        r"\b(compensation|benefits|payroll)\s+(management|system)\b"
    ],
    
    "accounting_finance": [
        # Accounting platforms
        r"\b(accounting|bookkeeping|financial)\s+(software|platform|tool|system)\b",
        r"\b(invoice|expense|budget)\s+(management|tracking|automation|system)\b",
        r"\b(tax|compliance|audit)\s+(software|platform|management)\b",
        
        # Financial processes
        r"\b(financial|accounting)\s+(reporting|analysis|planning)\b",
        r"\b(cash|revenue|expense)\s+(flow|management|tracking)\b",
        r"\b(budget|forecasting|planning)\s+(management|tool|system)\b",
        
        # Compliance and reporting
        r"\b(gaap|ifrs|tax)\s+(compliance|reporting|management)\b",
        r"\b(financial|accounting)\s+(audit|reconciliation|close)\b"
    ]
}

def detect_domain(seed_keywords: List[str], text_content: str = "") -> str:
    """
    Detect the most likely domain based on seed keywords and content.
    """
    combined_text = " ".join(seed_keywords) + " " + text_content.lower()
    
    domain_scores = {}
    
    for domain, patterns in DOMAIN_DETECTION_PATTERNS.items():
        score = 0
        for pattern in patterns:
            matches = re.findall(pattern, combined_text, re.IGNORECASE)
            score += len(matches)
        domain_scores[domain] = score
    
    # Return the domain with the highest score, or "general" if no clear match
    if domain_scores:
        best_domain = max(domain_scores.items(), key=lambda x: x[1])
        if best_domain[1] > 0:
            return best_domain[0]
    
    return "general"

def get_domain_patterns(domain: str) -> List[str]:
    """
    Get domain-specific patterns for keyword extraction.
    """
    return DOMAIN_PATTERNS.get(domain, [])

def get_all_domains() -> List[str]:
    """
    Get list of all supported domains.
    """
    return list(DOMAIN_PATTERNS.keys())

if __name__ == "__main__":
    # Test domain detection
    test_seeds = ["email deliverability", "spf dkim"]
    detected_domain = detect_domain(test_seeds)
    print(f"Detected domain: {detected_domain}")
    
    patterns = get_domain_patterns(detected_domain)
    print(f"Found {len(patterns)} patterns for {detected_domain}")
    
    # Test with different domains
    test_cases = [
        ["seo optimization", "keyword research"],
        ["social media marketing", "facebook ads"],
        ["ecommerce platform", "shopify"],
        ["crm system", "sales automation"]
    ]
    
    for seeds in test_cases:
        domain = detect_domain(seeds)
        print(f"Seeds: {seeds} -> Domain: {domain}")
