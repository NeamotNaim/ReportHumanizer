import re
import spacy
from collections import Counter
import math

try:
    nlp = spacy.load('en_core_web_sm')
except OSError:
    from spacy.cli import download
    download('en_core_web_sm')
    nlp = spacy.load('en_core_web_sm')

class AIDetector:
    def __init__(self):
        """Initialize AI detector with patterns"""
        self.ai_patterns = {
            "In conclusion": 5, "Furthermore": 5, "It is worth noting": 8,
            "The implementation of": 5, "Additionally": 4, "Notably": 4,
            "However": 3, "Therefore": 4, "In summary": 6,
            "It is important to note": 8, "To elaborate": 4,
            "In the realm of": 6, "As a matter of fact": 6,
            "It should be noted": 5, "In order to": 3,
            "Due to the fact that": 5, "At the present time": 4,
            "With regard to": 4, "For the purpose of": 4,
        }

    def detect(self, text):
        """
        Detect AI patterns in text using advanced structural metrics
        """
        if not text or not text.strip():
            return {'ai_score': 0, 'patterns': [], 'metrics': {}}

        score = 0
        patterns = []

        # 1. Simple known AI string matching
        for pattern, weight in self.ai_patterns.items():
            count = len(re.findall(rf'\b{re.escape(pattern)}\b', text, re.IGNORECASE))
            if count > 0:
                score += count * weight
                patterns.append({'pattern': pattern, 'count': count})

        # 2. Structural parsing with spaCy
        doc = nlp(text)
        sentences = list(doc.sents)
        num_sentences = len(sentences)
        word_count = len(doc)
        
        # Variance calculation (burstiness)
        sentence_lengths = [len(s) for s in sentences]
        avg_length = sum(sentence_lengths) / num_sentences if num_sentences > 0 else 0
        
        std_dev = 0
        if num_sentences > 1:
            variance = sum((l - avg_length) ** 2 for l in sentence_lengths) / num_sentences
            std_dev = math.sqrt(variance)
            # Low variance (uniform sentence length) indicates AI
            if std_dev < 5:
                score += 15
        elif avg_length > 20: 
            score += 10
            
        # 3. Vocabulary entropy (pseudo-perplexity computation)
        words = [token.text.lower() for token in doc if token.is_alpha]
        entropy = 0
        if words:
            word_freqs = Counter(words)
            entropy = -sum((count/len(words)) * math.log2(count/len(words)) for count in word_freqs.values())
            # Lower entropy = less diverse vocabulary usually seen in AI
            if entropy < 4.0:
                score += 10

        unique_words = len(set(words))
        word_variety_ratio = unique_words / len(words) if words else 0
        if word_variety_ratio < 0.5:
            score += 10

        score = min(score, 100)

        return {
            'ai_score': int(score),
            'patterns': [p['pattern'] for p in patterns],
            'metrics': {
                'avg_sentence_length': round(avg_length, 1),
                'total_sentences': num_sentences,
                'word_variety_ratio': round(word_variety_ratio, 3),
                'burstiness_std_dev': round(std_dev, 2),
                'entropy': round(entropy, 2)
            }
        }
