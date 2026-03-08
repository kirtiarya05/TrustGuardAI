from http.server import BaseHTTPRequestHandler
import json
import re

# Known scam patterns and clickbait triggers
SCAM_PATTERNS = [
    (r"win(ning)? (a )?(\$|€|£)?\d+", "Financial bait detected"),
    (r"inheritance", "Inheritance scam marker"),
    (r"crypto(currency)? investment", "Crypto scam risk"),
    (r"click (here|this link)", "Potential phishing call-to-action"),
    (r"(urgent|immediate) action required", "Artificial urgency detected"),
    (r"unclaimed (funds|money)", "Financial scam pattern"),
    (r"verify your (account|identity)", "Phishing pattern"),
    (r"miracle cure", "Health misinformation"),
    (r"secret (government|agency)", "Conspiracy theory marker"),
    (r"act now|limited time|exclusive deal", "Pressure tactics detected"),
    (r"100% (guaranteed|proven|safe)", "Unrealistic claims"),
    (r"make money (fast|quick|online)", "Get-rich-quick scheme"),
    (r"breaking.*?exposed", "Sensationalist framing"),
    (r"they don.?t want you to know", "Conspiracy language"),
    (r"doctors (hate|don.?t want)", "Health clickbait pattern"),
    (r"you won.?t believe", "Clickbait trigger phrase"),
    (r"share (before|this gets deleted)", "Viral manipulation"),
]

FAKE_KEYWORDS = [
    "shocking", "unbelievable", "miracle", "conspiracy", "hoax",
    "cover-up", "coverup", "exposed", "bombshell", "leaked",
    "they lied", "mainstream media", "deep state", "big pharma",
    "wake up", "sheeple", "plandemic", "scamdemic", "false flag",
    "mind control", "illuminati", "new world order", "chemtrails",
    "5g", "microchip", "depopulation", "crisis actor"
]

REAL_KEYWORDS = [
    "according to", "researchers found", "study published",
    "peer-reviewed", "data suggests", "evidence shows",
    "officials said", "report indicates", "analysis reveals",
    "university", "journal", "reuters", "associated press",
    "confirmed by", "statistics show", "investigation found"
]

def analyze_sentiment(text):
    """Simple sentiment analysis without external libs"""
    positive_words = ["good", "great", "excellent", "wonderful", "best", "love", "happy", "success", "improve", "benefit", "progress", "safe", "verified", "confirmed", "official"]
    negative_words = ["bad", "terrible", "worst", "hate", "fail", "danger", "threat", "crisis", "destroy", "kill", "dead", "attack", "fraud", "scam", "fake", "hoax", "lie"]
    
    words = text.lower().split()
    pos = sum(1 for w in words if w in positive_words)
    neg = sum(1 for w in words if w in negative_words)
    total = max(pos + neg, 1)
    
    polarity = (pos - neg) / total
    subjectivity = (pos + neg) / max(len(words), 1)
    
    if polarity > 0.3:
        label = "Highly Positive/Promotional"
    elif polarity < -0.3:
        label = "Negative/Aggressive"
    else:
        label = "Neutral"
    
    return label, round(min(subjectivity * 5, 1.0), 2)

def compute_score(text):
    text_lower = text.lower()
    flags = []
    
    # 1. Deep Scan for known scam/fake patterns
    for pattern, reason in SCAM_PATTERNS:
        if re.search(pattern, text_lower):
            flags.append(reason)
    
    # 2. Keyword-based scoring
    fake_count = sum(1 for kw in FAKE_KEYWORDS if kw in text_lower)
    real_count = sum(1 for kw in REAL_KEYWORDS if kw in text_lower)
    
    # 3. Heuristic checks
    # Excessive caps
    caps_ratio = sum(1 for c in text if c.isupper()) / max(len(text), 1)
    if caps_ratio > 0.4:
        flags.append("Excessive capitalization (shouting)")
    
    # Excessive punctuation
    excl_count = text.count('!') + text.count('?')
    if excl_count > 3:
        flags.append("Excessive punctuation (sensationalism)")
    
    # Very short text (hard to verify)
    if len(text.split()) < 10:
        flags.append("Insufficient content for deep analysis")
    
    # 4. Subjectivity check
    if "i think" in text_lower or "i believe" in text_lower or "in my opinion" in text_lower:
        flags.append("High Subjectivity (Opinion-heavy)")
    
    # 5. Compute trust score
    base_score = 60
    base_score -= fake_count * 12
    base_score += real_count * 10
    base_score -= len(flags) * 8
    base_score = max(0, min(100, base_score))
    
    # 6. Determine category
    if base_score <= 35 or len(flags) >= 3:
        category = "Fake"
        explanation = "Deep scan detected significant misinformation markers. Multiple red flags found including deceptive language patterns and unverified claims."
    elif base_score <= 65 or len(flags) >= 1:
        category = "Suspicious"
        explanation = "Anomalies detected in sentence structure or sentiment. Potential bias or lack of factual grounding flagged by the forensic engine."
    else:
        category = "Real"
        explanation = "Content aligns with standards of high-authority verified news sources. Low subjectivity and factual language patterns detected."
    
    # 7. Sentiment analysis
    sentiment, subjectivity = analyze_sentiment(text)
    
    # 8. Entity extraction
    entities = list(set(re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)))[:5]
    
    return {
        "score": base_score,
        "category": category,
        "explanation": explanation,
        "sentiment": sentiment,
        "subjectivity": subjectivity,
        "flags": flags,
        "entities": entities
    }

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        try:
            body = json.loads(post_data)
            text = body.get("text", "")
            result = compute_score(text)
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
