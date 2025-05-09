from newsapi import NewsApiClient
import requests
import json

NEWS_API_KEY = "your api key"
NEWSDATA_API_KEY = "your api key"

def test_newsapi(query="pakistan india attacks"):
    """Test NewsAPI functionality"""
    print(f"Testing NewsAPI with query: '{query}'...")
    try:
        newsapi = NewsApiClient(api_key=NEWS_API_KEY)
        
        # Try the everything endpoint
        everything_response = newsapi.get_everything(
            q=query,
            language='en',
            page_size=5,
            sort_by='relevancy'
        )
        
        if everything_response.get("status") == "ok":
            articles = everything_response.get("articles", [])
            print(f"✅ NewsAPI 'everything' endpoint returned {len(articles)} articles")
            
            if articles:
                print("\nSample article:")
                sample = articles[0]
                print(f"Title: {sample.get('title')}")
                print(f"Source: {sample.get('source', {}).get('name')}")
                print(f"URL: {sample.get('url')}")
        else:
            print(f"❌ NewsAPI error: {everything_response.get('message', 'Unknown error')}")
        
        # Try the top headlines endpoint with category
        headlines_response = newsapi.get_top_headlines(
            category='general',
            language='en',
            country='us',
            page_size=5
        )
        
        if headlines_response.get("status") == "ok":
            articles = headlines_response.get("articles", [])
            print(f"\n✅ NewsAPI 'top headlines' endpoint returned {len(articles)} articles")
        else:
            print(f"\n❌ NewsAPI headlines error: {headlines_response.get('message', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ NewsAPI error: {str(e)}")

def test_newsdata(query="pakistan india attacks"):
    """Test NewsData.io API functionality"""
    print(f"\nTesting NewsData.io with query: '{query}'...")
    try:
        # NewsData.io API endpoint
        url = "https://newsdata.io/api/1/news"
        
        params = {
            "apikey": NEWSDATA_API_KEY,
            "q": query,
            "language": "en",
            "size": 5  # Number of results to fetch
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        
        if data.get("status") == "success":
            articles = data.get("results", [])
            print(f"✅ NewsData.io returned {len(articles)} articles")
            
            if articles:
                print("\nSample article:")
                sample = articles[0]
                print(f"Title: {sample.get('title')}")
                print(f"Source: {sample.get('source_id')}")
                print(f"URL: {sample.get('link')}")
        else:
            print(f"❌ NewsData.io error: {data.get('results', {}).get('message', 'Unknown error')}")
    except Exception as e:
        print(f"❌ NewsData.io error: {str(e)}")

if __name__ == "__main__":
    query = "pakistan india attacks"
    test_newsapi(query)
    test_newsdata(query)
    
    # Also test with a more general query
    general_query = "climate change"
    print("\n" + "="*50)
    test_newsapi(general_query)
    test_newsdata(general_query) 
