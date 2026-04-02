import requests

API_KEY = "60227d3000884b76a0f534b54fc1e37a"

def fetch_latest_news():
    url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={API_KEY}"
    response = requests.get(url)
    data = response.json()
    
    articles = []
    for article in data["articles"]:
        articles.append({
            "title": article["title"],
            "description": article["description"]
        })
    
    return articles
