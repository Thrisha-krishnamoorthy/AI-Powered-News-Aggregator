from langchain_google_genai import ChatGoogleGenerativeAI
from google.genai import types

# Initialize Gemini model with Google Search grounding enabled
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",  # Or "gemini-2.0-flash" if preferred
    temperature=0.4,
    tools=[types.Tool(google_search=types.GoogleSearch())]
)

def format_response(response) -> str:
    # Extract the content from the response
    content = response.content if hasattr(response, 'content') else str(response)
    
    # Now format the content
    lines = content.strip().split("\n")
    formatted = "\n".join([
        line.replace("*", "🔹").strip() if line.strip().startswith("*") else f"\n📰 {line.strip()}"
        for line in lines
    ])
    return formatted

def chat_with_gemini(user_input):
    print("Prompt:", user_input)
    
    # Get the response from Gemini (this will be an AIMessage object)
    response = llm.invoke(user_input)
    
    # Format the response text
    pretty_output = format_response(response)
    
    return pretty_output
