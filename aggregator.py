from newsapi import NewsApiClient
import re
import requests

NEWS_API_KEY = "3635d28530f843a0aa7afa2a0e22bd7c"
newsapi = NewsApiClient(api_key=NEWS_API_KEY)

def preprocess_query(query):
    """Process longer queries into an optimized search format for NewsAPI"""
    # Remove extra whitespace and normalize
    query = query.strip()
    
    # Check for conflict-related terms to enhance query
    conflict_terms = ["attack", "war", "conflict", "tension", "military", "border", "terrorism"]
    country_pairs = [
        ("india", "pakistan"), ("israel", "palestine"), ("russia", "ukraine"), 
        ("china", "taiwan"), ("north korea", "south korea")
    ]
    
    # Check if query involves conflicts between specific countries
    for term1, term2 in country_pairs:
        if term1 in query.lower() and term2 in query.lower():
            # For queries involving country conflicts, add relevant terms for better results
            for conflict_term in conflict_terms:
                if conflict_term in query.lower():
                    # Already has conflict term, use as is
                    return query
            # Add general conflict terms to improve results
            return f"{query} conflict tension"
    
    # If query is very long (over 100 chars), extract key phrases
    if len(query) > 100:
        # Split into sentences if possible
        sentences = re.split(r'[.!?]', query)
        
        # Extract nouns and important words (simplified approach)
        important_words = []
        for sentence in sentences:
            # Remove common words
            words = sentence.strip().split()
            # Keep longer words that are likely more meaningful
            words = [word for word in words if len(word) > 3 and word.lower() not in 
                    ['this', 'that', 'with', 'from', 'have', 'what', 'when', 'where', 'which']]
            important_words.extend(words[:3])  # Take up to 3 important words from each sentence
        
        # Build a query with OR logic for wider coverage
        if len(important_words) > 1:
            return " OR ".join(important_words[:7])  # Limit to 7 terms
        
    return query  # Return original if not very long

def get_news(query, language="en", page_size=10, advanced=False):
    """
    Get news with support for longer queries and more results
    
    Args:
        query: Search query text
        language: Language code (default 'en')
        page_size: Number of results to return (max 100)
        advanced: If True, treat as an advanced query with preprocessing
    """
    # Check if query contains conflict-related terms
    conflict_terms = ["attack", "war", "conflict", "tension", "military", "border", "terrorism"]
    conflict_countries = ["india", "pakistan", "israel", "palestine", "russia", "ukraine", "china", "taiwan"]
    
    query_lower = query.lower()
    contains_conflict_term = any(term in query_lower for term in conflict_terms)
    contains_conflict_country = any(country in query_lower for country in conflict_countries)
    
    # If query is about conflicts between countries, use specialized function
    if contains_conflict_term and contains_conflict_country:
        return get_conflict_news(query, language, page_size)
    
    # Limit page size to valid range
    page_size = min(100, max(5, page_size))
    
    # Process long or complex queries
    if advanced and len(query) > 30:
        processed_query = preprocess_query(query)
    else:
        processed_query = query
    
    # Print the actual query being sent to the API for debugging
    print(f"Searching NewsAPI with query: '{processed_query}'")
    
    try:
        # Use 'everything' endpoint for maximum flexibility
        articles = newsapi.get_everything(
            q=processed_query, 
            language=language, 
            page_size=page_size,
            sort_by='relevancy'  # Sort by relevancy for best matches
        )
        
        results = []
        for article in articles.get('articles', []):
            # Only include articles with both title and description
            if article.get('title') and article.get('description'):
                # Extract country from source if possible (simplified)
                source_name = article.get('source', {}).get('name', '').lower()
                country = "Unknown"
                
                # Simple source-based country detection
                if any(c in source_name for c in ['india', 'ndtv', 'hindustan']):
                    country = "India"
                elif any(c in source_name for c in ['pakistan', 'dawn']):
                    country = "Pakistan"
                elif any(c in source_name for c in ['bbc', 'guardian', 'telegraph', 'uk']):
                    country = "UK"
                elif any(c in source_name for c in ['cnn', 'fox', 'nbc', 'cbs', 'usa today']):
                    country = "USA"
                
                results.append({
                    'title': article.get('title', ''),
                    'description': article.get('description', ''),
                    'url': article.get('url', '#'),
                    'source': article.get('source', {}).get('name', 'Unknown'),
                    'publishedAt': article.get('publishedAt', ''),
                    'country': country
                })
        
        return results
    except Exception as e:
        print(f"Error fetching news from NewsAPI: {e}")
        return []

def get_advanced_news(query, language="en", max_results=15):
    """Specialized function for handling long complex queries and returning more results"""
    return get_news(query, language, page_size=max_results, advanced=True)

def get_conflict_news(query, language="en", max_results=10):
    """
    Specialized function for searching news about conflicts and geopolitical tensions
    
    This function is optimized for news about conflicts, wars, attacks, and political tensions
    between countries which are often challenging to find accurate news about.
    """
    # Detect country names in the query
    countries = ["india", "pakistan", "china", "russia", "ukraine", "israel", "palestine", 
                "gaza", "iran", "iraq", "afghanistan", "syria", "yemen", "north korea", 
                "south korea", "taiwan"]
    
    # Check if query contains country names
    query_lower = query.lower()
    mentioned_countries = [country for country in countries if country in query_lower]
    
    if mentioned_countries:
        # Combine the original query with specific parameters for better results
        conflict_terms = ["attack", "war", "conflict", "tension", "violence", "military", "border", "terrorism"]
        
        # Check if query already contains conflict terms
        has_conflict_term = any(term in query_lower for term in conflict_terms)
        
        # If no conflict term is in the query, try adding some relevant ones
        if not has_conflict_term:
            query_with_terms = f"{query} (conflict OR tensions OR attack)"
        else:
            query_with_terms = query
        
        # Print the actual query being sent to the API for debugging
        print(f"Searching conflict news with query: '{query_with_terms}'")
        
        try:
            # For conflicts, searching by 'everything' endpoint often works better
            articles = newsapi.get_everything(
                q=query_with_terms,
                language=language,
                page_size=max_results,
                sort_by='relevancy'
            )
            
            results = []
            for article in articles.get('articles', []):
                if article.get('title') and article.get('description'):
                    # Determine which country is relevant
                    article_country = "Unknown"
                    for country in mentioned_countries:
                        if country in article.get('title', '').lower() or country in article.get('description', '').lower():
                            article_country = country.title()
                            break
                    
                    results.append({
                        'title': article.get('title', ''),
                        'description': article.get('description', ''),
                        'url': article.get('url', '#'),
                        'source': article.get('source', {}).get('name', 'Unknown'),
                        'publishedAt': article.get('publishedAt', ''),
                        'country': article_country
                    })
            
            # Return the results
            return results[:max_results]
                
        except Exception as e:
            print(f"Error fetching conflict news: {e}")
            return []
    
    # If no specific countries detected, fallback to regular advanced search
    return get_advanced_news(query, language, max_results)
