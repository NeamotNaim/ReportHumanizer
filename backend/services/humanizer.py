import re
import random
import spacy
from functools import lru_cache

try:
    nlp = spacy.load('en_core_web_sm')
except OSError:
    print("Downloading spacy model...")
    from spacy.cli import download
    download('en_core_web_sm')
    nlp = spacy.load('en_core_web_sm')

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
            self.model = None
            self.tokenizer = None
            self.model_loaded = False

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
            }
        }
        
    def humanize(self, text, tone='casual', language='en'):
        if not text.strip():
            return text
            
        doc = nlp(text)
        humanized_sentences = []
        
        for sent_obj in doc.sents:
            sent = sent_obj.text.strip()
            if not sent: continue
            
            # Step 1: Remove Patterns
            sent = self._remove_patterns(sent, language)
            
            # Step 2: Extract Entities to protect them
            sent, entity_map = self._extract_entities(sent)
            
            # Step 3: T5 Paraphrasing (with Cache)
            if self.model_loaded:
                sent = self._cached_paraphrase(sent, tone)
            
            # Step 4: Restore Entities
            sent = self._restore_entities(sent, entity_map)
            
            humanized_sentences.append(sent)

        # Step 5: Join
        text = ' '.join(humanized_sentences)
        text = self._inject_variation(text, tone)
        text = self._refine(text)
        
        return text

    def _extract_entities(self, text):
        doc = nlp(text)
        entity_map = {}
        processed_text = text
        
        # Extract and replace recognized Named Entities
        for i, ent in enumerate(doc.ents):
            if ent.label_ in ['PERSON', 'ORG', 'GPE', 'PRODUCT', 'LOC']:
                placeholder = f" ENTITY{i} "
                entity_map[placeholder.strip()] = ent.text
                processed_text = processed_text.replace(ent.text, placeholder, 1)
        return processed_text, entity_map

    def _restore_entities(self, text, entity_map):
        for placeholder, original in entity_map.items():
            # T5 sometimes misspells the placeholder or changes casing/spacing
            match = re.search(r'\d+', placeholder)
            if match:
                idx = match.group()
                # Catch variations like ENTIT1, Entity 1, entity1, ENTITY1
                pattern = re.compile(rf'\bENTIT[Yy]?\s*{idx}\b', re.IGNORECASE)
                text = pattern.sub(original, text)
                
            text = text.replace(placeholder, original)
            text = text.replace(placeholder.lower(), original)
            text = text.replace(placeholder.replace(" ", ""), original)
        return text

    def _remove_patterns(self, text, language='en'):
        phrases = self.ai_phrases.get(language, self.ai_phrases['en'])
        for ai_phrase, human_phrase in phrases.items():
            text = re.sub(rf'\b{re.escape(ai_phrase)}\b', human_phrase, text, flags=re.IGNORECASE)
        return text

    def _cached_paraphrase(self, text, tone):
        return _paraphrase_global(self, text, tone)

    def _inject_variation(self, text, tone='casual'):
        doc = nlp(text)
        varied_sentences = []
        for i, sent_obj in enumerate(doc.sents):
            sent = sent_obj.text
            # More intelligent varied sentence breaking using clauses
            if i % 3 == 0 and len(sent_obj) > 15:
                split_point = -1
                for token in sent_obj:
                    if (token.pos_ == "CCONJ" or token.pos_ == "SCONJ") and token.i > sent_obj.start + 2:
                        split_point = token.i - sent_obj.start
                        break
                if split_point > 0 and split_point < len(sent_obj) - 1:
                    part1 = sent_obj[:split_point].text
                    part2 = sent_obj[split_point:].text.capitalize()
                    sent = f"{part1}. {part2}"
            varied_sentences.append(sent)

        text = ' '.join(varied_sentences)
        if tone == 'casual':
            casual_markers = ['Look,', "Here's the thing,", 'You know,', 'So basically,']
            if random.random() < 0.3:
                text = casual_markers[hash(text) % len(casual_markers)] + ' ' + text
        return text

    def _refine(self, text):
        # Remove any lingering prompt tokens that might have escaped word-level checks
        text = re.sub(r'\b(rewrite|paraphrase)\s+(casual|formal|academic|creative)\b', '', text, flags=re.IGNORECASE)
        
        words = text.split()
        refined_words = []
        for i, word in enumerate(words):
            if i == 0 or word.lower() != words[i - 1].lower():
                refined_words.append(word)
        return ' '.join(refined_words).strip()

@lru_cache(maxsize=1000)
def _paraphrase_global(engine, text, tone):
    try:
        text = text.strip()
        if not text: return ""

        prompt_prefix = f"rewrite {tone}: "
        input_text = f"{prompt_prefix}{text}"
        input_ids = engine.tokenizer.encode(input_text, return_tensors="pt", max_length=512, truncation=True)
        
        input_words = len(text.split())
        min_len = max(5, int(input_words * 0.9 * 1.3))
        max_len = max(min_len + 15, int(input_words * 2.5 * 1.3))

        outputs = engine.model.generate(
            input_ids,
            max_length=max_len,
            min_length=min_len,
            num_beams=2,
            temperature=0.8,
            top_p=0.9,
            repetition_penalty=1.1,
            do_sample=True,
            no_repeat_ngram_size=3
        )
        
        result = engine.tokenizer.decode(outputs[0], skip_special_tokens=True)
        # Aggressively strip multiple nested prefixes or prompt echoes
        prefix_pattern = r'\b(paraphrase|rewrite|reword|humanize|translate|casual|formal|academic|creative)\s*(\b\w+\b)?\s*[:\-]\s*'
        result = re.sub(prefix_pattern, '', result, flags=re.IGNORECASE)
        # Handle cases where the prefix is not followed by a colon
        result = re.sub(r'\b(rewrite|paraphrase)\s+(casual|formal|academic|creative)\b', '', result, flags=re.IGNORECASE)
        
        junk_patterns = [
            r'^(True|False|Neutral)\s*[:\-\.)_]\s*', # Catch starting markers like "False.)"
            r'\b(True|False|Neutral)\s*[:\-\.)_]\s*', # Catch markers inside text
            r'False\s*[:\-]?\s*(a\s*)?rewrite.*',
            r'False\s*_(entailment|inference|contradiction).*',
            r'Intended\s*for\s*(True|False).*',
            r'neutral\s*_(entailment|inference).*',
            r'\[[^\]]+\]', 
            r'\{[^\}]+\}'  
        ]
        for pattern in junk_patterns:
            result = re.sub(pattern, '', result, flags=re.IGNORECASE)

        junk_keywords = ['entailment', 'inference', 'contradiction', 'neutral']
        is_junk = any(kw in result.lower() for kw in junk_keywords)

        # Reject generations that hallucinate "True" or "False"
        if 'true' in result.lower() and 'true' not in text.lower():
            is_junk = True
        if 'false' in result.lower() and 'false' not in text.lower():
            is_junk = True
            
        # Clean up stray colons at the start
        result = re.sub(r'^[\s:]+', '', result)
        
        if not result.strip() or len(result.split()) < input_words * 0.4 or is_junk:
            return text
            
        return result.strip()
    except Exception as e:
        print(f"T5 paraphrasing failed for sentence: {e}")
        return text
