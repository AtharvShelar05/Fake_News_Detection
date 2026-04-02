"""
Test script for the upgraded FakeShield /check-news endpoint.
Run this script *after* train_bert.py has successfully completed.
"""
import urllib.request
import json
import time

URL = "http://127.0.0.1:5000/check-news"

def test_endpoint(text_sample, desc):
    print(f"\n[{desc}] Testing with text:")
    print(f"'{text_sample[:100]}...'")
    print("-" * 50)
    
    data = json.dumps({"text": text_sample}).encode("utf-8")
    req = urllib.request.Request(
        URL, 
        data=data, 
        headers={"Content-Type": "application/json"}
    )
    
    start_time = time.time()
    try:
        resp = urllib.request.urlopen(req, timeout=30)
        elapsed = time.time() - start_time
        res = json.loads(resp.read().decode())
        
        print(f"Time taken:      {elapsed:.2f}s")
        print(f"ML Prediction:   {res.get('ml_prediction')} ({res.get('ml_confidence')}%)")
        print(f"Verdict:         {res.get('final_verdict')} (Confidence: {res.get('confidence')})")
        print(f"Model Source:    {res.get('model_source')}")
        print(f"Model Agreement: {res.get('model_agreement')}")
        
        preds = res.get('individual_predictions', {})
        print(f"Individual:      TF-IDF={preds.get('tfidf')} | BERT={preds.get('bert', 'N/A')}")
        
        shap = res.get('shap_explanations', {})
        top_words = shap.get('top_words', [])
        print(f"SHAP Highlights: {len(shap.get('highlighted_text', []))} words processed")
        
        print("Top 5 Contributing Words:")
        for w in top_words[:5]:
            dir_arrow = "↑ Fake" if w['direction'] == 'fake' else "↓ Real"
            print(f"  - {w['word']:<15} {dir_arrow:<8} (Score: {w['score']})")
        
    except Exception as e:
        print(f"Error calling {URL}: {e}")

if __name__ == "__main__":
    print("WARNING: Ensure that `python run_app.py --no-train` is running in a separate terminal.")
    
    # Test 1: General claim
    test_endpoint(
        "Scientists discover that drinking water helps maintain hydration, but does not cure all diseases.",
        "General News"
    )
    
    # Test 2: Known fake claim
    test_endpoint(
        "SHOCKING: 5G networks and COVID vaccines are spreading brain control chips! It's a massive hoax by the government.",
        "Fake/Misinformation Template"
    )
