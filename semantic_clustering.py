# semantic_clustering.py
# Groups related keywords and phrases into semantic clusters
# Uses pattern matching and domain knowledge to create meaningful groups

from typing import List, Dict, Set, Tuple
import re
from collections import defaultdict

# Domain-specific semantic clusters
EMAIL_DELIVERABILITY_CLUSTERS = {
    "authentication_protocols": {
        "patterns": [
            r"\b(spf|dkim|dmarc)\b",
            r"\b(authentication|verification)\s+(protocol|method|system)\b",
            r"\b(ssl|tls)\s+(certificate|cert)\b"
        ],
        "keywords": ["spf", "dkim", "dmarc", "authentication", "verification", "ssl", "tls"]
    },
    
    "delivery_metrics": {
        "patterns": [
            r"\b(bounce|open|click|unsubscribe)\s+rate\b",
            r"\b(delivery|deliverability)\s+rate\b",
            r"\b(engagement|performance)\s+metrics\b"
        ],
        "keywords": ["bounce rate", "open rate", "click rate", "delivery rate", "engagement rate"]
    },
    
    "reputation_management": {
        "patterns": [
            r"\b(sender|domain|ip)\s+reputation\b",
            r"\b(blacklist|whitelist|greylist)\b",
            r"\b(postmaster)\s+(tool|tools)\b"
        ],
        "keywords": ["sender reputation", "domain reputation", "ip reputation", "blacklist", "whitelist"]
    },
    
    "spam_filtering": {
        "patterns": [
            r"\b(spam|junk)\s+(filter|folder)\b",
            r"\b(spam)\s+(trap|score|analysis)\b",
            r"\b(inbox|promotions)\s+(placement|folder)\b"
        ],
        "keywords": ["spam filter", "spam folder", "spam trap", "inbox placement", "promotions folder"]
    },
    
    "list_management": {
        "patterns": [
            r"\b(list)\s+(hygiene|cleaning|validation)\b",
            r"\b(subscriber|email)\s+(list|database)\b",
            r"\b(opt-in|opt-out|unsubscribe)\b"
        ],
        "keywords": ["list hygiene", "subscriber list", "opt-in", "opt-out", "unsubscribe"]
    },
    
    "email_campaigns": {
        "patterns": [
            r"\b(cold|bulk|mass)\s+email\b",
            r"\b(email)\s+(campaign|marketing|automation)\b",
            r"\b(campaign)\s+(monitoring|tracking)\b"
        ],
        "keywords": ["cold email", "bulk email", "email campaign", "email marketing"]
    }
}

# Generic technical clusters
GENERIC_TECH_CLUSTERS = {
    "api_integration": {
        "patterns": [
            r"\b(api|apis)\s+(integration|endpoint|key)\b",
            r"\b(rest|graphql|soap)\s+(api|service)\b"
        ],
        "keywords": ["api integration", "rest api", "graphql", "endpoint"]
    },
    
    "cloud_services": {
        "patterns": [
            r"\b(cloud|saas|software)\s+(service|platform)\b",
            r"\b(aws|azure|gcp|google)\s+(service|platform)\b"
        ],
        "keywords": ["cloud service", "saas", "aws", "azure", "gcp"]
    },
    
    "security_features": {
        "patterns": [
            r"\b(security|secure|encryption)\s+(feature|protocol)\b",
            r"\b(two-factor|2fa|mfa)\s+(authentication)\b"
        ],
        "keywords": ["security", "encryption", "two-factor", "authentication"]
    },
    
    "monitoring_analytics": {
        "patterns": [
            r"\b(monitoring|tracking|analytics)\s+(tool|platform)\b",
            r"\b(real-time|realtime)\s+(monitoring|tracking)\b"
        ],
        "keywords": ["monitoring", "analytics", "real-time", "tracking"]
    }
}

def cluster_keywords(keywords: List[str], domain: str = "general") -> Dict[str, List[str]]:
    """
    Group keywords into semantic clusters based on domain-specific patterns.
    """
    clusters = defaultdict(list)
    unclustered = []
    
    # Select appropriate cluster definitions
    cluster_definitions = EMAIL_DELIVERABILITY_CLUSTERS if domain == "email_deliverability" else GENERIC_TECH_CLUSTERS
    
    # Assign keywords to clusters
    for keyword in keywords:
        keyword_lower = keyword.lower()
        assigned = False
        
        for cluster_name, cluster_info in cluster_definitions.items():
            # Check patterns
            for pattern in cluster_info["patterns"]:
                if re.search(pattern, keyword_lower, re.IGNORECASE):
                    clusters[cluster_name].append(keyword)
                    assigned = True
                    break
            
            # Check keyword list
            if not assigned:
                for cluster_keyword in cluster_info["keywords"]:
                    if cluster_keyword.lower() in keyword_lower or keyword_lower in cluster_keyword.lower():
                        clusters[cluster_name].append(keyword)
                        assigned = True
                        break
            
            if assigned:
                break
        
        if not assigned:
            unclustered.append(keyword)
    
    # Add unclustered keywords to a separate cluster
    if unclustered:
        clusters["other_keywords"] = unclustered
    
    return dict(clusters)

def get_cluster_summaries(clusters: Dict[str, List[str]]) -> Dict[str, str]:
    """
    Generate human-readable summaries for each cluster.
    """
    summaries = {}
    
    cluster_descriptions = {
        "authentication_protocols": "Email authentication and security protocols",
        "delivery_metrics": "Email delivery and engagement metrics",
        "reputation_management": "Sender and domain reputation management",
        "spam_filtering": "Spam detection and filtering systems",
        "list_management": "Email list hygiene and subscriber management",
        "email_campaigns": "Email campaign and marketing tools",
        "api_integration": "API and integration capabilities",
        "cloud_services": "Cloud and SaaS platforms",
        "security_features": "Security and authentication features",
        "monitoring_analytics": "Monitoring and analytics capabilities",
        "other_keywords": "Additional relevant terms"
    }
    
    for cluster_name, keywords in clusters.items():
        if cluster_name in cluster_descriptions:
            summaries[cluster_name] = f"{cluster_descriptions[cluster_name]}: {', '.join(keywords[:5])}"
        else:
            summaries[cluster_name] = f"{cluster_name}: {', '.join(keywords[:5])}"
    
    return summaries

def extract_primary_clusters(clusters: Dict[str, List[str]], max_clusters: int = 3) -> Dict[str, List[str]]:
    """
    Extract the most important clusters based on keyword count and relevance.
    """
    # Score clusters by size and importance
    cluster_scores = {}
    for cluster_name, keywords in clusters.items():
        if cluster_name == "other_keywords":
            score = len(keywords) * 0.5  # Lower weight for unclustered
        else:
            score = len(keywords) * 1.0  # Full weight for semantic clusters
        
        cluster_scores[cluster_name] = score
    
    # Get top clusters
    sorted_clusters = sorted(cluster_scores.items(), key=lambda x: x[1], reverse=True)
    top_cluster_names = [name for name, score in sorted_clusters[:max_clusters]]
    
    return {name: clusters[name] for name in top_cluster_names if name in clusters}

if __name__ == "__main__":
    # Test clustering
    test_keywords = [
        "email deliverability", "spf", "dkim", "bounce rate", "sender reputation",
        "spam filter", "list hygiene", "cold email", "api integration", "cloud service"
    ]
    
    clusters = cluster_keywords(test_keywords, domain="email_deliverability")
    summaries = get_cluster_summaries(clusters)
    
    print("Clustered keywords:")
    for cluster_name, keywords in clusters.items():
        print(f"{cluster_name}: {keywords}")
    
    print("\nCluster summaries:")
    for cluster_name, summary in summaries.items():
        print(f"{cluster_name}: {summary}")
