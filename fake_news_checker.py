from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import torch.nn.functional as F

# Use a known public model
model_name = "mariagrandury/bert-fake-news-detection"


def check_fake_news(text):
    # Tokenize input
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    
    # Run model
    with torch.no_grad():
        outputs = model(**inputs)

    # Get softmax probabilities
    probs = F.softmax(outputs.logits, dim=1)

    # Just for demo: Return probability of class 1
    # You can customize this logic after checking labels
    return probs[0][1].item()
