import os
import requests
import logging
from typing import List, Dict, Tuple, Any

from realtime.ensemble import EnsemblePredictor
from realtime.fact_checker import FactChecker

logger = logging.getLogger(__name__)

# Singletons for lazy loading
_predictor = None
_fact_checker = None

def _init_models():
    """Lazy initialize the models to save startup time."""
    global _predictor, _fact_checker
    if _predictor is None:
        try:
            _predictor = EnsemblePredictor()
            logger.info("EnsemblePredictor initialized in integration module.")
        except Exception as e:
            logger.error(f"Failed to load EnsemblePredictor: {e}")
    if _fact_checker is None:
        try:
            _fact_checker = FactChecker()
            logger.info("FactChecker initialized in integration module.")
        except Exception as e:
            logger.error(f"Failed to load FactChecker: {e}")

def fetch_news(query: str = "breaking news", page_size: int = 5) -> List[Dict[str, str]]:
    """
    Fetch real-time news articles from NewsAPI.
    Returns a list of dictionaries with 'title' and 'description'.
    """
    api_key = os.environ.get("NEWS_API_KEY", "").strip()
    if not api_key:
        logger.warning("No NEWS_API_KEY set. Cannot fetch real-time news.")
        return []
        
    url = f"https://newsapi.org/v2/everything?q={query}&pageSize={page_size}&apiKey={api_key}&language=en"
    
    try:
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            articles = data.get("articles", [])
            results = []
            for a in articles:
                title = a.get("title") or ""
                desc = a.get("description") or ""
                if title:
                    results.append({"title": title, "description": desc})
            return results
        else:
            logger.error(f"NewsAPI error: {resp.status_code} - {resp.text}")
    except Exception as e:
        logger.error(f"Exception during fetch_news: {e}")
        
    return []

def verify_claim(text: str) -> str:
    """
    Verify a claim using the integrated FactChecker.
    Ensures output is exactly "True", "False", or "Not Found".
    """
    _init_models()
    if _fact_checker is None or not _fact_checker.is_available():
        return "Not Found"
        
    try:
        result = _fact_checker.check(text)
    except Exception as e:
        logger.error(f"verify_claim exception: {e}")
        return "Not Found"
        
    if not result.get("matched"):
        return "Not Found"
        
    label = result.get("verified_label")
    if label == "Verified Fake":
        return "False"
    elif label == "Verified True":
        return "True"
        
    return "Not Found"

def predict_news(text: str) -> Tuple[str, float]:
    """
    Predict using the ML Ensemble.
    Returns: (label: "FAKE"|"REAL", confidence: float)
    Using 'real_proba' as the unified confidence score.
    """
    _init_models()
    if _predictor is None:
        raise RuntimeError("EnsemblePredictor is not loaded.")
        
    result = _predictor.predict(text)
    # Return the label and the confidence of the claim being REAL
    label = result["label"].upper() # "FAKE" or "REAL"
    confidence = result["real_proba"]
    return label, confidence

def final_decision(confidence: float, text: str) -> Tuple[str, str]:
    """
    Smart Decision Engine Core Logic.
    
    Rules based on REAL confidence (0.0=FAKE, 1.0=REAL):
    - If >= 0.75 -> REAL
    - If <= 0.25 -> FAKE
    - If 0.25 < confidence < 0.75:
       -> Optimization: Call fact-check API ONLY if between 0.4 and 0.6
       -> Result tree assigns VERIFIED FAKE, VERIFIED REAL, or UNCERTAIN.
       
    Returns:
       (final_label, fact_check_status)
    """
    if confidence >= 0.75:
        return "REAL", "Not Called"
        
    elif confidence <= 0.25:
        return "FAKE", "Not Called"
        
    else:
        # Check optimization window
        if 0.4 <= confidence <= 0.6:
            fc_status = verify_claim(text)
            if fc_status == "False":
                return "VERIFIED FAKE", fc_status
            elif fc_status == "True":
                return "VERIFIED REAL", fc_status
            else:
                return "UNCERTAIN", fc_status
        else:
            return "UNCERTAIN", "Not Called"
