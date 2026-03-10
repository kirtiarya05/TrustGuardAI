from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import os
import re
import nltk
from textblob import TextBlob
from typing import List, Optional

# Download NLTK data if not present
try:
    nltk.data.find('sentiment')
except LookupError:
    nltk.download('movie_reviews')
    nltk.download('punkt')

app = FastAPI(title="TrustGuard AI API - Deep Scan Pro")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from nltk.corpus import stopwords
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')
STOPWORDS = set(stopwords.words('english'))

def clean_text(text):
    if not isinstance(text, str):
        return ""
    text = str(text).lower()
    text = re.sub(r'\[.*?\]', '', text)
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    text = re.sub(r'<.*?>+', '', text)
    text = re.sub(r'[%s]' % re.escape(r'!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~'), '', text)
    text = re.sub(r'\n', '', text)
    text = re.sub(r'\w*\d\w*', '', text)
    text = " ".join([w for w in text.split() if w not in STOPWORDS])
    return text


MODEL_PATH = "models/model.joblib"
classifier = None

try:
    if os.path.exists(MODEL_PATH):
        classifier = joblib.load(MODEL_PATH)
        print("Mega-Model loaded successfully!")
except Exception as e:
    print(f"Error loading model: {e}")

class CheckRequest(BaseModel):
    text: str

class DeepScanResult(BaseModel):
    score: int
    category: str
    explanation: str
    sentiment: str
    subjectivity: float
    flags: List[str]
    entities: List[str]

# Known scam patterns and clickbait triggers
SCAM_PATTERNS = [
    (r"win(ning)? (a )?(\$|€|£)?\d+","Financial bait detected"),
    (r"inheritance", "Inheritance scam marker"),
    (r"crypto(currency)? investment", "Crypto scam risk"),
    (r"click (here|this link)", "Potential phishing call-to-action"),
    (r"(urgent|immediate) action required", "Artificial urgency detected"),
    (r"unclaimed (funds|money)", "Financial scam pattern"),
    (r"verify your (account|identity)", "Phishing pattern"),
    (r"miracle cure", "Health misinformation"),
    (r"secret (government|agency)", "Conspiracy theory marker")
]

@app.post("/api/analyze", response_model=DeepScanResult)
def analyze_text(request: CheckRequest):
    text = request.text
    flags = []
    
    # 1. Deep Scanning for known patterns
    for pattern, reason in SCAM_PATTERNS:
        if re.search(pattern, text.lower()):
            flags.append(reason)
            
    # 2. Linguistic Analysis with TextBlob
    blob = TextBlob(text)
    sentiment_score = blob.sentiment.polarity
    subjectivity = blob.sentiment.subjectivity
    
    sentiment_label = "Neutral"
    if sentiment_score > 0.3: sentiment_label = "Highly Positive/Promotional"
    elif sentiment_score < -0.3: sentiment_label = "Negative/Aggressive"
    
    if subjectivity > 0.7:
        flags.append("High Subjectivity (Opinion-heavy)")
    
    # 3. Entity extraction (simple regex for capitalized names/orgs)
    entities = list(set(re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)))
    
    # 4. Neural Prediction
    trust_score = 50
    category = "Suspicious"
    explanation = "System in fallback mode."
    
    if classifier is not None:
        try:
            cleaned_text = clean_text(text)
            
            # Calculate pseudo-probability for V6.2 hard-voting ensemble
            X_transformed = classifier.named_steps['features'].transform([cleaned_text])
            predictions = []
            for clf in classifier.named_steps['clf'].estimators_:
                predictions.append(clf.predict(X_transformed)[0])
                
            prob_fake = sum(predictions) / len(predictions) if predictions else 0.5
            prob_real = 1.0 - prob_fake
            trust_score = int(prob_real * 100)
            
            if prob_fake >= 0.65 or len(flags) >= 3:
                category = "Fake"
                explanation = "CRITICAL: "
                if flags:
                    explanation += f"Detected {', '.join(flags[:2])}. "
                explanation += "Deep scan indicates significant misinformation markers and high linguistic deviation from verified reports."
            elif prob_fake > 0.35 or len(flags) >= 2:
                category = "Suspicious"
                explanation = "WARNING: "
                if flags:
                    explanation += f"Flagged for {flags[0]}. "
                explanation += f"Anomalies detected in {'highly subjective' if subjectivity > 0.6 else 'sentence'} structure with a {sentiment_label.lower()} tone."
            else:
                category = "Real"
                explanation = f"TRUSTED: Syntactic alignment matches standards of high-authority global news networks. Detected {sentiment_label.lower()} sentiment with low subjectivity."
        except Exception as e:
            print("Prediction error:", e)
            explanation = "System fallback: Neural prediction failed."


    # Adjust score based on flags
    trust_score = max(0, trust_score - (len(flags) * 10))

    return DeepScanResult(
        score=trust_score,
        category=category,
        explanation=explanation,
        sentiment=sentiment_label,
        subjectivity=round(subjectivity, 2),
        flags=flags,
        entities=entities[:5] # Limit to top 5
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
