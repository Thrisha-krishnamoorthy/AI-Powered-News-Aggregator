from aggregator import get_news, get_conflict_news, get_advanced_news

def test_specific_query():
    # Test the query from the screenshot
    query = "the pakistan and india attacks"
    print(f"\nTesting query: '{query}'")
    
    # Test with conflict detection
    print("Using get_conflict_news:")
    results = get_conflict_news(query)
    print(f"Found {len(results)} articles")
    for i, article in enumerate(results[:3]):  # Show first 3 results
        print(f"{i+1}. {article['title']} - {article['source']}")
    
    # Test with regular search
    print("\nUsing regular get_news:")
    results = get_news(query)
    print(f"Found {len(results)} articles")
    for i, article in enumerate(results[:3]):  # Show first 3 results
        print(f"{i+1}. {article['title']} - {article['source']}")
    
    # Test with advanced search
    print("\nUsing get_advanced_news:")
    results = get_advanced_news(query)
    print(f"Found {len(results)} articles")
    for i, article in enumerate(results[:3]):  # Show first 3 results
        print(f"{i+1}. {article['title']} - {article['source']}")
    
if __name__ == "__main__":
    test_specific_query() 