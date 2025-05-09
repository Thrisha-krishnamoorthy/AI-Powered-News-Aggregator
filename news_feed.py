import streamlit as st
import requests
import sqlite3

NEWS_API_KEY = " Your actual key"  

TOPIC_OPTIONS = [
    "business", "entertainment", "general", "health",
    "science", "sports", "technology", "politics", "finance", "stock"
]

COUNTRY_OPTIONS = {
    "India": "in",
    "USA": "us",
    "UK": "gb",
    "Canada": "ca",
    "Singapore": "sg",
    "Australia": "au",
    "World": "global"  # pseudo-country, we'll use everything
}

# Map user-friendly topic names to API category names
TOPIC_TO_CATEGORY = {
    "Finance": "business",  
    "Sports": "sports",
    "Politics": "politics",
    "Stock": "business", 
    "Technology": "technology",
    "science": "science",
    "health": "health",
    "entertainment": "entertainment"
}

# Function to fetch user interests from the database
def get_user_interests(user_id):
    try:
        conn = sqlite3.connect("news_app.db")
        c = conn.cursor()
        c.execute("SELECT topics, countries FROM user_interests WHERE user_id = ?", (user_id,))
        interests = c.fetchone()  # Only one row should exist for each user
        conn.close()

        if interests:
            topics = interests[0].split(",") if interests[0] else []
            countries = interests[1].split(",") if interests[1] else []
            return {"topics": topics, "countries": countries}
        return None
    except Exception as e:
        print(f"Error getting user interests: {e}")
        return None

# Function to update user interests in the database
def update_user_interests(user_id, topics, countries):
    try:
        conn = sqlite3.connect("news_app.db")
        c = conn.cursor()
        
        # Use INSERT OR REPLACE instead of DELETE + INSERT for better performance
        topics_str = ",".join(topics) if topics else ""
        countries_str = ",".join(countries) if countries else ""
        
        # Check if user already has interests
        c.execute("SELECT id FROM user_interests WHERE user_id = ?", (user_id,))
        if c.fetchone():
            # Update existing
            c.execute("UPDATE user_interests SET topics = ?, countries = ? WHERE user_id = ?",
                     (topics_str, countries_str, user_id))
        else:
            # Insert new
            c.execute("INSERT INTO user_interests (user_id, topics, countries) VALUES (?, ?, ?)",
                     (user_id, topics_str, countries_str))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error updating user interests: {e}")
        return False

def get_news_by_categories(categories, countries=None):
    """Get news for specific categories and countries"""
    if not categories:
        return []
    
    # Default to USA if no countries specified
    if not countries:
        countries = ["USA"]
    
    # Convert user-friendly topics to API categories
    api_categories = [TOPIC_TO_CATEGORY.get(cat.lower(), "general") for cat in categories]
    
    all_articles = []
    
    # Get news for each country-category pair
    for country in countries:
        country_code = COUNTRY_OPTIONS.get(country, "us")
        
        for category in api_categories:
            try:
                # For "World" or "global", search for general news on the topic
                if country_code == "global":
                    url = f"https://newsapi.org/v2/everything?q={category}&pageSize=3&apiKey={NEWS_API_KEY}"
                else:
                    url = f"https://newsapi.org/v2/top-headlines?country={country_code}&category={category}&pageSize=3&apiKey={NEWS_API_KEY}"
                
                response = requests.get(url).json()
                
                if response.get("status") == "ok":
                    for article in response.get("articles", []):
                        all_articles.append({
                            "title": article.get("title", "No Title"),
                            "description": article.get("description", ""),
                            "url": article.get("url", "#"),
                            "source": article.get("source", {}).get("name", "Unknown"),
                            "category": category,
                            "country": country
                        })
            except Exception as e:
                print(f"Error fetching news for {country}/{category}: {e}")
    
    # Remove duplicates based on title
    unique_articles = []
    titles = set()
    for article in all_articles:
        if article["title"] not in titles:
            titles.add(article["title"])
            unique_articles.append(article)
    
    return unique_articles[:5]  # Return up to 5 articles

def get_related_news(article, max_results=4):
    """Get news related to a specific article based on keywords in its title and description"""
    if not article:
        return []
    
    # Extract keywords from article title and description
    title = article.get("title", "")
    description = article.get("description", "")
    
    # Remove common words and extract meaningful keywords
    import re
    from collections import Counter
    
    # Combine title and description
    text = f"{title} {description}"
    
    # Clean text - lowercase, remove punctuation, and split into words
    words = re.sub(r'[^\w\s]', '', text.lower()).split()
    
    # Common English stopwords to filter out
    stopwords = {'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
                'is', 'are', 'was', 'were', 'be', 'been', 'being', 'by', 'with', 
                'about', 'against', 'between', 'into', 'through', 'during', 'before', 
                'after', 'above', 'below', 'from', 'up', 'down', 'of', 'off', 'over', 
                'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 
                'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 
                'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 
                'same', 'so', 'than', 'too', 'very', 'can', 'will', 'just', 'should', 
                'now', 'this', 'that', 'these', 'those', 'what', 'which', 'who', 'whom'}
    
    # Filter out stopwords and short words
    filtered_words = [word for word in words if word not in stopwords and len(word) > 3]
    
    # Count word frequency
    word_counts = Counter(filtered_words)
    
    # Get the most common words as keywords (up to 5)
    keywords = [word for word, count in word_counts.most_common(5)]
    
    if not keywords:
        # Fallback to category if no significant keywords found
        return get_news_by_categories([article.get("category", "general")])
    
    # Build search query with the keywords
    search_query = " OR ".join(keywords)
    
    # Get country from article
    country = article.get("country", "World")
    country_code = COUNTRY_OPTIONS.get(country, "global")
    
    # Fetch related news using keywords
    try:
        # Use 'everything' endpoint for keyword search
        url = f"https://newsapi.org/v2/everything?q={search_query}&pageSize={max_results+1}&apiKey={NEWS_API_KEY}"
        response = requests.get(url).json()
        
        related_articles = []
        current_title = article.get("title", "")
        
        if response.get("status") == "ok":
            for related in response.get("articles", []):
                # Skip the current article
                if related.get("title") == current_title:
                    continue
                    
                related_articles.append({
                    "title": related.get("title", "No Title"),
                    "description": related.get("description", ""),
                    "url": related.get("url", "#"),
                    "source": related.get("source", {}).get("name", "Unknown"),
                    "category": article.get("category", "general"),
                    "country": country
                })
                
                # Stop once we have enough articles
                if len(related_articles) >= max_results:
                    break
        
        # If we didn't get enough related articles, supplement with category news
        if len(related_articles) < max_results:
            additional = get_news_by_categories([article.get("category", "general")], [country])
            
            # Add additional articles without duplicating titles
            existing_titles = {a["title"] for a in related_articles}
            for add_article in additional:
                if add_article["title"] not in existing_titles and add_article["title"] != current_title:
                    related_articles.append(add_article)
                    existing_titles.add(add_article["title"])
                    
                    if len(related_articles) >= max_results:
                        break
        
        return related_articles
    except Exception as e:
        print(f"Error fetching related news: {e}")
        # Fallback to category-based news if there's an error
        return get_news_by_categories([article.get("category", "general")], [country])

def search_long_form(query, max_results=5):
    """
    Search for news using a longer, more complex query and return relevant articles
    
    This function is optimized for handling longer search queries like questions,
    statements, or detailed topic descriptions.
    
    Args:
        query: The long search query (can be a question, statement, or detailed description)
        max_results: Maximum number of results to return
    
    Returns:
        List of relevant news articles
    """
    if not query or len(query.strip()) < 5:
        return []
    
    # Process the long query to extract meaningful search terms
    import re
    from collections import Counter
    
    # Clean and normalize the query
    query = query.strip()
    
    # For very long queries, extract key terms
    if len(query) > 80:
        # Split into sentences
        sentences = re.split(r'[.!?]', query)
        
        # Extract meaningful words (simple approach - could be improved with NLP)
        important_words = []
        for sentence in sentences:
            # Remove common words
            words = re.sub(r'[^\w\s]', '', sentence.lower()).split()
            
            # Filter out common stop words and short words
            stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
                        'is', 'are', 'was', 'were', 'be', 'been', 'being', 'by', 'with', 
                        'about', 'what', 'when', 'where', 'how', 'why', 'who', 'which', 'this', 
                        'that', 'these', 'those', 'they', 'them', 'their', 'have', 'has', 'had',
                        'not', 'don', 'all', 'any', 'very', 'will', 'should', 'can', 'could'}
            
            filtered_words = [word for word in words if word not in stopwords and len(word) > 3]
            important_words.extend(filtered_words)
        
        # Count word frequency
        word_counts = Counter(important_words)
        
        # Get most common words as search terms (up to 8)
        search_terms = [word for word, count in word_counts.most_common(8)]
        
        # Build search query using key terms with OR logic for broader results
        if len(search_terms) > 1:
            processed_query = " OR ".join(search_terms)
        else:
            # If insufficient terms extracted, use original but truncated
            processed_query = query[:150]
    else:
        # For shorter queries, use as-is
        processed_query = query
    
    # Attempt to fetch news using the processed query
    try:
        # Use 'everything' endpoint for better semantic matching
        url = f"https://newsapi.org/v2/everything?q={processed_query}&language=en&pageSize={max_results+3}&sortBy=relevancy&apiKey={NEWS_API_KEY}"
        response = requests.get(url).json()
        
        if response.get("status") == "ok":
            result_articles = []
            
            for article in response.get("articles", []):
                if article.get("title") and article.get("description"):
                    # Extract the primary category if possible
                    content = f"{article.get('title', '')} {article.get('description', '')}"
                    
                    # Simple keyword-based category extraction (could be improved with ML)
                    category = "general"
                    category_keywords = {
                        "business": ["business", "economy", "market", "stock", "finance", "trade", "economic"],
                        "technology": ["tech", "technology", "digital", "software", "hardware", "ai", "computing"],
                        "health": ["health", "medical", "medicine", "disease", "treatment", "doctor", "patient"],
                        "science": ["science", "scientific", "research", "study", "discovery"],
                        "sports": ["sport", "sports", "team", "player", "game", "match", "tournament"],
                        "politics": ["politics", "political", "government", "election", "policy", "minister", "president"],
                        "entertainment": ["entertainment", "movie", "film", "music", "celebrity", "actor", "actress"]
                    }
                    
                    content_lower = content.lower()
                    for cat, keywords in category_keywords.items():
                        if any(keyword in content_lower for keyword in keywords):
                            category = cat
                            break
                    
                    # Determine country from source or default to global
                    source_name = article.get("source", {}).get("name", "").lower()
                    country = "World"  # Default
                    
                    # Simple country detection based on domain or source name
                    country_indicators = {
                        "india": ["india", ".in", "indian", "times of india", "hindustan"],
                        "USA": ["usa", "us", "america", "american", ".com", "washington", "york"],
                        "UK": ["uk", "united kingdom", "british", ".co.uk", "bbc", "guardian"],
                        "Canada": ["canada", "canadian", ".ca"],
                        "Australia": ["australia", "australian", ".au"],
                        "Singapore": ["singapore", "singaporean", ".sg"]
                    }
                    
                    for c, indicators in country_indicators.items():
                        if any(ind in source_name for ind in indicators):
                            country = c
                            break
                    
                    result_articles.append({
                        "title": article.get("title", ""),
                        "description": article.get("description", ""),
                        "url": article.get("url", "#"),
                        "source": article.get("source", {}).get("name", "Unknown"),
                        "publishedAt": article.get("publishedAt", ""),
                        "category": category,
                        "country": country
                    })
                    
                    if len(result_articles) >= max_results:
                        break
            
            return result_articles
        else:
            print(f"Error from NewsAPI: {response.get('message', 'Unknown error')}")
            return []
    except Exception as e:
        print(f"Error in search_long_form: {e}")
        return []

# Function to fetch news based on interests
def get_news_feed(interests):
    """Get news based on user interests"""
    if not interests or not interests.get("topics"):
        return []
    
    topics = interests.get("topics", ["general"])
    countries = interests.get("countries", ["World"])
    
    # Convert user-friendly topics to API categories
    api_categories = [TOPIC_TO_CATEGORY.get(topic.lower(), "general") for topic in topics]
    
    all_articles = []
    
    # Get news for each country-category pair
    for country in countries:
        country_code = COUNTRY_OPTIONS.get(country, "us")
        
        for category in api_categories:
            if country_code == "global":
                url = f"https://newsapi.org/v2/everything?q={category}&pageSize=5&apiKey={NEWS_API_KEY}"
            else:
                url = f"https://newsapi.org/v2/top-headlines?country={country_code}&category={category}&pageSize=5&apiKey={NEWS_API_KEY}"

            try:
                response = requests.get(url).json()
                if response.get("status") == "ok":
                    for article in response.get("articles", []):
                        all_articles.append({
                            "title": article.get("title", "No Title"),
                            "description": article.get("description", ""),
                            "url": article.get("url", "#"),
                            "source": article.get("source", {}).get("name", "Unknown"),
                            "category": category,
                            "country": country
                        })
            except Exception as e:
                print(f"Error fetching news: {e}")
    
    # Remove duplicates
    unique_articles = []
    titles = set()
    for article in all_articles:
        if article["title"] not in titles:
            titles.add(article["title"])
            unique_articles.append(article)
    
    return unique_articles[:10]  # Return up to 10 articles

# Main Streamlit app interface
def main():
    st.title("News Feed App")

    # Assume the user is logged in, and we know the user_id (this can be dynamic based on session)
    user_id = 1  # This would be dynamic in a real app

    # Fetch the user's current interests
    interests = get_user_interests(user_id)

    # Display news feed based on interests
    get_news_feed(interests)

    # Section to edit interests (hidden by default)
    with st.expander("Edit Your Interests"):
        # Let users change topics and countries
        new_topics = st.multiselect("Select topics of interest", TOPIC_OPTIONS, interests["topics"])
        new_countries = st.multiselect("Select countries of interest", list(COUNTRY_OPTIONS.keys()), interests["countries"])

        if st.button("Save Interests"):
            # Save new interests to the database
            update_user_interests(user_id, new_topics, new_countries)
            st.success("Your interests have been updated!")

if __name__ == "__main__":
    main()
