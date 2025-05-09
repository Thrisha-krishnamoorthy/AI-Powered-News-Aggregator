import spacy
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from keras.models import Sequential
from keras.layers import Embedding, LSTM, Dense
from keras.preprocessing.sequence import pad_sequences
from keras.preprocessing.text import Tokenizer
from gemini_chain import analyze_news as gemini_cot

# Load spaCy model for NER
nlp = spacy.load("en_core_web_sm")

# Dummy dataset and models (replace with trained models in real case)
rf_model = RandomForestClassifier()
tokenizer = Tokenizer(num_words=5000)
rnn_model = Sequential([
    Embedding(input_dim=5000, output_dim=64),
    LSTM(64),
    Dense(1, activation='sigmoid')
])
rnn_model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

def extract_entities(text):
    doc = nlp(text)
    return [(ent.text, ent.label_) for ent in doc.ents]

def random_forest_predict(texts):
    return np.random.rand(len(texts))  # Placeholder for demo

def rnn_predict(texts):
    tokenizer.fit_on_texts(texts)
    sequences = tokenizer.texts_to_sequences(texts)
    data = pad_sequences(sequences, maxlen=100)
    return rnn_model.predict(data).flatten()  # Placeholder

def analyze_news(news):
    results = []
    titles = [n["title"] for n in news]
    rf_scores = random_forest_predict(titles)
    rnn_scores = rnn_predict(titles)
    gemini_scores = gemini_cot(news)

    for i, article in enumerate(news):
        title = article["title"]
        description = article["description"]
        content = f"{title}. {description}"

        ner = extract_entities(content)
        rf = rf_scores[i]
        rnn = rnn_scores[i]
        gemini = gemini_scores[i] / 100  # assuming Gemini returns 0-100%

        # Composite score
        final_score = np.mean([rf, rnn, gemini])

        results.append({
            "title": title,
            "description": description,
            "ner": ner,
            "rf_score": round(rf * 100, 2),
            "rnn_score": round(rnn * 100, 2),
            "gemini_score": round(gemini * 100, 2),
            "final_score": round(final_score * 100, 2),
            "url": article["url"]
        })

    return results
