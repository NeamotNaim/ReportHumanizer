import re
import random
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


class HumanizeEngine:
    def __init__(self):
        """Initialize T5 model and tokenizer"""
        try:
            from transformers import T5ForConditionalGeneration, T5Tokenizer
            self.model = T5ForConditionalGeneration.from_pretrained('t5-base')
            self.tokenizer = T5Tokenizer.from_pretrained('t5-base')
            self.model_loaded = True
        except Exception as e:
            print(f"Warning: Could not load T5 model: {e}")
            print("Falling back to rule-based humanization.")
            self.model = None
            self.tokenizer = None
            self.model_loaded = False

        # AI phrase replacements
        self.ai_phrases = {
            'en': {
                "In conclusion": "So",
                "Furthermore": "Also",
                "It is worth noting that": "Keep in mind",
                "The implementation of": "Using",
                "Additionally": "Plus",
                "Notably": "Interestingly",
                "However": "But",
                "Therefore": "That's why",
                "In summary": "To sum up",
                "It is important to note": "Remember",
                "In the realm of": "In",
                "As a matter of fact": "Actually",
                "To elaborate": "Basically",
                "It should be noted that": "Note that",
                "In order to": "To",
                "Due to the fact that": "Because",
                "At the present time": "Now",
                "In light of": "Given",
                "With regard to": "About",
                "For the purpose of": "To",
            },
            'es': {
                "En conclusión": "Entonces",
                "Además": "También",
                "Vale la pena señalar": "Recuerda",
            },
            'fr': {
                "En conclusion": "Donc",
                "De plus": "Aussi",
                "Il est important de noter": "N'oubliez pas",
            },
            'de': {
                "Zusammenfassend": "Also",
                "Darüber hinaus": "Auch",
                "Es ist wichtig zu beachten": "Denken Sie daran",
            },
            'pt': {
                "Em conclusão": "Então",
                "Além disso": "Também",
                "É importante notar": "Lembre-se",
            },
        }

    def humanize(self, text, tone='casual', language='en'):
        """
        Main humanization pipeline - Sentence level processing
        
        Steps:
        1. Tokenize into sentences
        2. Process each sentence (pattern removal + T5)
        3. Inject variation and join
        """
        try:
            sentences = sent_tokenize(text)
        except Exception:
            sentences = text.split('. ')

        humanized_sentences = []
        
        for sent in sentences:
            if not sent.strip():
                continue
                
            # Step 1: Remove AI patterns
            sent = self._remove_patterns(sent, language)

            # Step 2: T5 paraphrasing (on single sentence)
            if self.model_loaded:
                sent = self._paraphrase_t5(sent)

            humanized_sentences.append(sent)

        # Step 3: Join and inject variation across the whole text
        text = ' '.join(humanized_sentences)
        text = self._inject_variation(text, tone)
        
        # Step 4: Final Refine
        text = self._refine(text)

        return text

    def _remove_patterns(self, text, language='en'):
        """Remove AI-specific phrases"""
        phrases = self.ai_phrases.get(language, self.ai_phrases['en'])
        for ai_phrase, human_phrase in phrases.items():
            # Use regex for word boundaries to avoid partial matches
            text = re.sub(rf'\b{re.escape(ai_phrase)}\b', human_phrase, text, flags=re.IGNORECASE)
        return text

    def _paraphrase_t5(self, text):
        """Use T5 for paraphrasing a single sentence with fine-tuned length preservation"""
        try:
            # Clean input to ensure no weird chars
            text = text.strip()
            if not text: return ""

            # Use "rewrite:" instead of "paraphrase:" to avoid triggering NLI tasks
            input_text = f"rewrite: {text}"
            input_ids = self.tokenizer.encode(input_text, return_tensors="pt", max_length=512, truncation=True)
            
            # Calculate dynamic length constraints
            input_words = len(text.split())
            
            # target roughly 90% to 150% of original word count
            min_len = max(5, int(input_words * 0.9 * 1.3))
            max_len = max(min_len + 15, int(input_words * 2.5 * 1.3))

            outputs = self.model.generate(
                input_ids,
                max_length=max_len,
                min_length=min_len,
                num_beams=2, # Lower beams for less 'logical' search
                temperature=0.8,
                top_p=0.9,
                repetition_penalty=1.1,
                do_sample=True,
                no_repeat_ngram_size=3
            )
            
            result = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # 1. Strip T5 prompt artifacts
            result = re.sub(r'^(paraphrase|rewrite|reword|humanize|translate):\s*', '', result, flags=re.IGNORECASE)
            
            # 2. Junk Filter: Remove NLI / Logical artifacts
            junk_patterns = [
                r'False\s*_(entailment|inference|contradiction).*',
                r'Intended\s*for\s*(True|False).*',
                r'neutral\s*_(entailment|inference).*',
                r'\[[^\]]+\]', # Remove anything in brackets
                r'\{[^\}]+\}'  # Remove anything in braces
            ]
            for pattern in junk_patterns:
                result = re.sub(pattern, '', result, flags=re.IGNORECASE)

            # 3. Final quality check
            # If the result is way too short, contains junk keywords, or is identical to input
            junk_keywords = ['entailment', 'inference', 'contradiction', 'neutral']
            is_junk = any(kw in result.lower() for kw in junk_keywords)
            
            if not result.strip() or len(result.split()) < input_words * 0.4 or is_junk:
                return text
                
            return result.strip()
        except Exception as e:
            print(f"T5 paraphrasing failed for sentence: {e}")
            return text

    def _inject_variation(self, text, tone='casual'):
        """Inject natural variation based on tone"""
        try:
            sentences = sent_tokenize(text)
        except Exception:
            sentences = text.split('. ')

        # Vary sentence length and structure
        varied_sentences = []
        for i, sent in enumerate(sentences):
            if i % 3 == 0 and len(sent.split()) > 10:
                # Break long sentences
                words = sent.split()
                split_point = len(words) // 2
                sent = ' '.join(words[:split_point]) + '. ' + ' '.join(words[split_point:])

            varied_sentences.append(sent)

        text = ' '.join(varied_sentences)

        # Add casual markers based on tone
        if tone == 'casual':
            casual_markers = ['Look,', "Here's the thing,", 'You know,', 'So basically,']
            if random.random() < 0.3:
                text = casual_markers[hash(text) % len(casual_markers)] + ' ' + text

        return text

    def _refine(self, text):
        """Final refinement"""
        # Remove duplicate words
        words = text.split()
        refined_words = []
        for i, word in enumerate(words):
            if i == 0 or word.lower() != words[i - 1].lower():
                refined_words.append(word)

        return ' '.join(refined_words)
