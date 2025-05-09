import google.generativeai as genai

# 🔐 Replace with your API key
genai.configure(api_key="AIzaSyD_MzbcVf7HlCHzJRQJoByKAgf9w9x-HBo")

# Fetch and list all available models
models = genai.list_models()

print("📦 Available Models:")
for model in models:
    print(f"- {model.name} | Input Type: {model.input_token_limit} tokens")
