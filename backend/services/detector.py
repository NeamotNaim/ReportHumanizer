import re
import nltk
from nltk.tokenize import sent_tokenize

# Ensure NLTK data is available
try:
    nltk.data.find('tokenizers/punkt')
except (LookupError, OSError):
    nltk.download('punkt', quiet=True)

try:
    nltk.download('punkt_tab', quiet=True)
except Exception:
    pass  # punkt_tab not available in older NLTK versions


class AIDetector:
    def __init__(self):
        """Initialize AI detector with patterns"""
        self.ai_patterns = {
            "In conclusion": 5,
            "Furthermore": 5,
            "It is worth noting": 8,
            "The implementation of": 5,
            "Additionally": 4,
            "Notably": 4,
            "However": 3,
            "Therefore": 4,
            "In summary": 6,
            "It is important to note": 8,
            "To elaborate": 4,
            "In the realm of": 6,
            "As a matter of fact": 6,
            "It should be noted": 5,
            "In order to": 3,
            "Due to the fact that": 5,
            "At the present time": 4,
            "With regard to": 4,
            "For the purpose of": 4,
        }

    def detect(self, text):
        """
        Detect AI patterns in text

        Returns:
        {
            'ai_score': 0-100,
            'patterns': [list of detected patterns],
            'metrics': {...}
        }
        """
        if not text or not text.strip():
            return {'ai_score': 0, 'patterns': [], 'metrics': {}}

        score = 0
        patterns = []

        # Count patterns
        for pattern, weight in self.ai_patterns.items():
            count = len(re.findall(rf'\b{re.escape(pattern)}\b', text, re.IGNORECASE))
            if count > 0:
                score += count * weight
                patterns.append({'pattern': pattern, 'count': count})

        # Analyze sentence structure
        try:
            sentences = sent_tokenize(text)
        except Exception:
            sentences = text.split('. ')

        word_count = len(text.split())
        avg_length = word_count / len(sentences) if sentences else 0

        # AI texts tend to have longer sentences
        if avg_length > 20:
            score += 10

        # Low word variety indicates AI
        unique_words = len(set(word.lower() for word in text.split()))
        word_variety_ratio = unique_words / word_count if word_count > 0 else 0
        if word_variety_ratio < 0.6:
            score += 15

        # Cap at 100
        score = min(score, 100)

        return {
            'ai_score': score,
            'patterns': [p['pattern'] for p in patterns],
            'metrics': {
                'avg_sentence_length': round(avg_length, 1),
                'total_sentences': len(sentences),
                'word_variety_ratio': round(word_variety_ratio, 3)
            }
        }
