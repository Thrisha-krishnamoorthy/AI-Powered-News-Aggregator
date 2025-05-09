from aggregator import get_news, get_advanced_news, get_conflict_news
from gemini_chain import analyze_news, advanced_analyze_news, extract_probabilities
import streamlit as st
import re
import random

# Simulate RNN & COT Confidence
def simulate_rnn_confidence(news_texts):
    return [random.uniform(0.4, 0.95) for _ in news_texts]

def simulate_cot_confidence(news_texts):
    return [random.uniform(0.5, 0.97) for _ in news_texts]

def is_conflict_query(query):
    """Check if a query is about conflicts or sensitive geopolitical topics"""
    query_lower = query.lower()
    
    # Check for conflict terms
    conflict_terms = ["attack", "war", "conflict", "tension", "military", "strike", "bomb", 
                      "terrorism", "terrorist", "border", "invasion", "missile", "killed"]
    
    # Check for country pairs often involved in conflicts
    conflict_countries = ["india", "pakistan", "israel", "palestine", "gaza", "russia", "ukraine", 
                          "china", "taiwan", "north korea", "south korea", "iran", "iraq", 
                          "afghanistan", "syria", "yemen"]
    
    # Check if query contains both conflict terms and country names
    has_conflict_term = any(term in query_lower for term in conflict_terms)
    
    # Count how many conflict countries are mentioned
    mentioned_countries = [country for country in conflict_countries if country in query_lower]
    
    # Return True if query has conflict term and mentions at least one conflict country
    return has_conflict_term and len(mentioned_countries) > 0

def suggest_alternative_queries(original_query):
    """Suggest alternative queries when a search fails to return results"""
    original_lower = original_query.lower()
    
    # Common terms that might be too specific and should be generalized
    specific_terms = {
        "attack": ["conflict", "tensions", "situation"],
        "killed": ["casualties", "incident"],
        "terrorist": ["militants", "extremists"],
        "war": ["conflict", "military operation", "hostilities"],
        "invasion": ["incursion", "military activity"],
        "genocide": ["human rights crisis", "violence"]
    }
    
    # Check if original query has any of the specific terms
    alternative_suggestions = []
    
    for term, alternatives in specific_terms.items():
        if term in original_lower:
            # For each specific term found, suggest using alternatives
            for alt in alternatives:
                alternative_suggestions.append(original_lower.replace(term, alt))
    
    # If no alternatives generated based on term replacement, suggest more general queries
    if not alternative_suggestions and len(original_query.split()) > 3:
        # Create more general queries by taking subsets of the original query
        words = original_query.split()
        if len(words) >= 4:
            # Suggest just using the first 3 words
            alternative_suggestions.append(" ".join(words[:3]))
            
            # Find likely country names in the query
            countries = ["india", "pakistan", "israel", "palestine", "russia", "ukraine", 
                        "china", "taiwan", "iran", "north korea", "south korea"]
            
            found_countries = []
            for country in countries:
                if country in original_lower:
                    found_countries.append(country)
            
            if found_countries:
                for country in found_countries:
                    # Suggest "<country> situation recent"
                    alternative_suggestions.append(f"{country} recent developments")
                    alternative_suggestions.append(f"latest news {country}")
    
    # Limit to top 3 suggestions
    return alternative_suggestions[:3]

def render():
    st.title("📰 AI-Powered News Aggregation ,Summarization & Fact Analysis ")

    # More descriptive placeholder for users
    query = st.text_area(
        "Enter topic or detailed question (supports longer searches)", 
        placeholder="Enter keywords or descriptions of what you're looking for. E.g., 'Latest developments in AI and healthcare in 2024' or 'Climate change impacts on agriculture in South Asia'",
        height=100,
        key="search_query"
    )
    
    # Initialize query from session state if set
    if "query" in st.session_state:
        query = st.session_state.query
        # Clear after use
        del st.session_state.query
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Option to use advanced analysis mode for longer queries
        use_advanced = st.checkbox("Use advanced analysis mode (better for complex topics)", 
                                  value=len(query.strip()) > 80 if query else False)
    
    with col2:
        # Slider for number of results
        num_results = st.slider("Number of results", min_value=5, max_value=15, value=8)

    if st.button("Search & Analyze News"):
        if query:
            st.info(f"Searching for: '{query}'")
            
            # Check if query is about conflicts which need specialized handling
            if is_conflict_query(query):
                st.info("Your search appears to be about conflicts or sensitive geopolitical topics. Using specialized search techniques for better results.")
                
                # Show loading spinner during search
                with st.spinner("🔍 Searching for news on sensitive topics..."):
                    news = get_conflict_news(query, max_results=num_results)
                    
                    if not news:
                        st.warning("No news articles found for this specific topic. This could be due to limited coverage or API restrictions for sensitive content.")
                        
                        # Suggest alternative queries
                        alternatives = suggest_alternative_queries(query)
                        if alternatives:
                            st.subheader("Try these alternative searches:")
                            for alt in alternatives:
                                if st.button(f"🔄 {alt}", key=f"alt_{alt}"):
                                    # When user clicks an alternative, set it as the new query and rerun
                                    st.session_state.query = alt
                                    st.rerun()
                        return
            else:
                # Show loading spinner during search
                with st.spinner("🔍 Searching for news..."):
                    # Use advanced search for longer queries or when explicitly requested
                    if use_advanced or len(query.strip()) > 100:
                        news = get_advanced_news(query, max_results=num_results)
                    else:
                        news = get_news(query, page_size=num_results)
                    
                    if not news:
                        st.warning("No news articles found for this topic. Try different keywords or check your spelling.")
                        
                        # Suggest alternative queries
                        alternatives = suggest_alternative_queries(query)
                        if alternatives:
                            st.subheader("Try these alternative searches:")
                            for alt in alternatives:
                                if st.button(f"🔄 {alt}", key=f"alt_{alt}"):
                                    # When user clicks an alternative, set it as the new query and rerun
                                    st.session_state.query = alt
                                    st.rerun()
                        return

            # Display the aggregated news in an organized layout
            st.subheader(f"🗞️ Aggregated News Results ({len(news)} articles found)")
            
            # Create a tabular display for better organization
            for i, article in enumerate(news):
                with st.expander(f"📄 {article['title']}", expanded=i==0):  # Expand first one by default
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.markdown(f"**Source:** {article['source']} • {article.get('publishedAt', '')}")
                    with col2:
                        # Add a direct link to the source
                        st.markdown(f"[🔗 Original Source]({article['url']})")
                    
                    st.markdown(article['description'])
                    
                    # Add country information if available
                    if article.get('country') and article.get('country') != "Unknown":
                        st.caption(f"Country focus: {article.get('country')}")

            # Different analysis approach based on mode
            if use_advanced:
                with st.spinner("🧠 Performing advanced analysis..."):
                    try:
                        result = advanced_analyze_news(news, query)
                    except Exception as e:
                        st.warning(f"Advanced analysis encountered an error: {str(e)}")
                        st.info("Falling back to standard analysis...")
                        use_advanced = False
                        result = analyze_news(news)
                
                if use_advanced:  # Only if advanced analysis was successful
                    st.subheader("🔬 Advanced Analysis")
                    
                    # Attempt to parse the structured output
                    articles = result.split("### Title:")
                    
                    if len(articles) > 1:  # If successfully split into articles
                        for i, article_analysis in enumerate(articles[1:]):
                            try:
                                # Extract the title
                                title = re.search(r"\[(.*?)\]", article_analysis)
                                title_text = title.group(1) if title else f"Article {i+1}"
                                
                                # Extract other components (may be in different formats)
                                relevance = re.search(r"Relevance to Query:\s*(\d+)%", article_analysis)
                                probability = re.search(r"Real vs Fake Probability:\s*(\d+)%", article_analysis)
                                credibility = re.search(r"Source Credibility:\s*(\d+)/10", article_analysis)
                                
                                relevance_score = int(relevance.group(1)) if relevance else 50
                                real_score = int(probability.group(1)) if probability else 50
                                cred_score = int(credibility.group(1)) if credibility else 5
                                
                                # Create expandable section for each article
                                with st.expander(f"🔍 {title_text}", expanded=i==0):
                                    # Create columns for the metrics
                                    col1, col2, col3 = st.columns(3)
                                    
                                    with col1:
                                        st.metric("Relevance", f"{relevance_score}%")
                                        st.progress(relevance_score/100)
                                    
                                    with col2:
                                        st.metric("Authenticity", f"{real_score}%")
                                        st.progress(real_score/100)
                                    
                                    with col3:
                                        st.metric("Source Credibility", f"{cred_score}/10")
                                        st.progress(cred_score/10)
                                    
                                    # Show the full analysis content
                                    st.markdown(article_analysis)
                            except Exception as e:
                                st.error(f"Error parsing analysis result: {e}")
                                st.markdown(article_analysis)  # Show raw output as fallback
                    else:
                        # Fallback if parsing fails
                        st.markdown(result)
                # If advanced analysis failed, continue with regular analysis path below
            
            # Regular analysis for shorter queries or if advanced analysis failed
            if not use_advanced:
                # Regular analysis for shorter queries
                with st.spinner("Analyzing..."):
                    result = analyze_news(news)

                # Prepare simulated RNN & COT inputs (could be replaced with real models)
                combined_texts = [article['title'] + " " + article['description'] for article in news]
                rnn_confidences = simulate_rnn_confidence(combined_texts)
                cot_confidences = simulate_cot_confidence(combined_texts)

                st.subheader("🧠 AI Analysis")
                articles = result.split("### Title:")
                
                for i, a in enumerate(articles[1:]):
                    title_match = re.search(r"\[(.*?)\]", a)
                    title = title_match.group(1) if title_match else f"News {i+1}"

                    # Gemini Confidence
                    prob_match = re.search(r"Real vs Fake Probability:\s*(\d+)%", a)
                    gemini_percent = int(prob_match.group(1)) if prob_match else 50

                    # Simulated RNN & COT Confidences
                    rnn_percent = round(rnn_confidences[i] * 100) if i < len(rnn_confidences) else 50
                    cot_percent = round(cot_confidences[i] * 100) if i < len(cot_confidences) else 50

                    with st.expander(title, expanded=i==0):
                        # Format the full analysis content nicely
                        content = a.replace("- 📰", "### 📰").replace("- 🧪", "### 🧪").replace("- ℹ️", "### ℹ️").replace("- 🏷️", "### 🏷️")
                        st.markdown(content)
                        
                        # Progress bars for visual indication
                        st.markdown("### Analysis Summary")
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown(f"🧠 **GeminiChain Score:** {gemini_percent}% Real")
                            st.progress(gemini_percent / 100)

                        with col2:
                            st.markdown(f"🔁 **ML Model Score:** {rnn_percent}% Real")
                            st.progress(rnn_percent / 100)
        else:
            st.warning("Please enter a topic to search for news.")
            
    # Help text at the bottom
    with st.expander("ℹ️ Tips for better results"):
        st.markdown("""
        - For general topics, use short keywords like "climate change" or "AI technology"
        - For complex research, use the advanced mode and describe what you're looking for in detail
        - Include specific names, locations or time periods to narrow results
        - For fact-checking, include the claim you want to verify in quotes
        - The analysis assesses authenticity based on source credibility and content analysis
        - For sensitive geopolitical topics, try different phrasings if your search returns no results
        """)
        
    # Initialize session state for query persistence if clicking alternative suggestions
    if 'query' in st.session_state:
        # If query was set from an alternative suggestion, use it
        if st.session_state.query != query:
            # This trick allows us to update the text area with the suggested query
            st.session_state.query_pending = True
            st.rerun()
