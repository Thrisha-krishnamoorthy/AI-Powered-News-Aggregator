from collections import Counter

def recommend_categories(user_categories):
    if not user_categories:
        return ["technology", "world", "sports"]
    most_common = Counter(user_categories).most_common(2)
    return [item[0] for item in most_common]
