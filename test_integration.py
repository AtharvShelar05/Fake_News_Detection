import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app import app
from realtime.integration import fetch_news

def test_fetch_news():
    print("Testing fetch news...")
    news = fetch_news(query="ai", page_size=1)
    if news:
        print("Success: ", news[0]["title"])
    else:
        print("No news fetched (might expect this if API key is not set)")

def test_check_news():
    print("Testing /check-news endpoint...")
    client = app.test_client()
    
    # Text that should trigger REAL or FAKE depending on ML model (using common phrases)
    test_texts = [
        "NASA scientists confirm that the earth is completely round and water is wet.",
        "Shocking: Secret alien base found on the dark side of the moon by whistleblowers!",
        "Vaccines cause autism says new shocking discovery that nobody knew about!"
    ]
    
    for text in test_texts:
        print(f"\nEvaluating: {text[:50]}...")
        response = client.post('/check-news', json={'text': text})
        
        if response.status_code == 200:
            data = response.get_json()
            print(" final_label       :", data.get('final_label'))
            print(" confidence_score  :", data.get('confidence_score'))
            print(" fact_check_status :", data.get('fact_check_status'))
        else:
            print("Error: status code ", response.status_code)
            print("Details: ", response.get_json())
            
if __name__ == "__main__":
    test_fetch_news()
    test_check_news()
