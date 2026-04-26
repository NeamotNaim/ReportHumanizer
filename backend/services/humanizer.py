"""
Multi-stage AI Text Humanizer Engine.

Pipeline:
  Stage 1 — Deep Analysis (LLM identifies AI patterns)
  Stage 2 — Humanize (LLM rewrites with anti-AI constraints)
  Stage 3 — Quality Gate (length check, entity preservation, cleanup)
  Stage 4 — Iterative Refinement (optional, re-humanize flagged sections)
"""

import os
import re
from typing import Dict, List, Tuple, Optional

import spacy

try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Downloading spacy model...")
    from spacy.cli import download

    download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

try:
    from .llm_provider import LLMProvider
    from .detector import AIDetector
except ImportError:
    from llm_provider import LLMProvider
    from detector import AIDetector


# ── Words that AI detectors look for ──────────────────────────────────────────
AI_WATERMARK_WORDS = {
    "delve", "tapestry", "landscape", "testament", "pivotal", "crucial",
    "foster", "leverage", "utilize", "underscore", "multifaceted",
    "comprehensive", "robust", "nuanced", "realm", "paradigm", "synergy",
    "holistic", "plethora", "myriad", "encompasses", "facilitates",
    "underpins", "navigating", "harnessing", "intricate", "Moreover",
    "Furthermore", "Consequently", "Nevertheless", "Notably",
    "It is worth noting", "It is important to note", "In conclusion",
    "In summary", "In the realm of", "This serves as a testament",
    "It should be noted", "In order to", "At the present time",
    "Due to the fact that", "For the purpose of", "With regard to",
}

# ── Tone-specific prompt fragments ────────────────────────────────────────────
TONE_INSTRUCTIONS = {
    "casual": (
        "Use contractions (don't, can't, it's). "
        "Write as if explaining to a friend over coffee. "
        "It's fine to start sentences with 'And' or 'But' occasionally. "
        "Keep vocabulary accessible."
    ),
    "academic": (
        "Maintain formal register suitable for a university essay. "
        "Preserve academic conventions (hedging, citations references, etc.). "
        "Use discipline-appropriate terminology but avoid pompous phrasing. "
        "It is acceptable to use passive voice sparingly where convention demands."
    ),
    "formal": (
        "Use professional, polished language suitable for a business report. "
        "Avoid contractions. Keep sentences crisp and authoritative."
    ),
    "creative": (
        "Use vivid, engaging language. Employ metaphors and analogies where natural. "
        "Vary rhythm dramatically — some very short sentences, some flowing ones."
    ),
}


class HumanizeEngine:
    """Multi-stage humanization engine powered by cloud LLMs."""

    def __init__(self):
        self.llm = LLMProvider()
        self.detector = AIDetector()
        self.max_refinement_loops = int(os.getenv("MAX_REFINEMENT_LOOPS", "3"))
        self.model_loaded = self.llm.is_available


    # ──────────────────────────────────────────────────────────────────────────
    # Public API
    # ──────────────────────────────────────────────────────────────────────────

    def humanize(
        self,
        text: str,
        tone: str = "casual",
        language: str = "en",
    ) -> Dict:
        """
        Run the full humanization pipeline.

        Returns dict with:
            humanized: str          — final rewritten text
            iterations: int         — how many refinement loops ran
            stage_log: list[str]    — status messages for each stage
        """
        if not text or not text.strip():
            return {"humanized": text, "iterations": 0, "stage_log": []}

        stage_log: List[str] = []
        original_word_count = len(text.split())

        # ── Extract entities to protect ──────────────────────────────────
        protected_text, entity_map = self._extract_entities(text)

        # ── Stage 1: Deep AI-pattern analysis ────────────────────────────
        stage_log.append("Stage 1: Analyzing AI patterns…")
        analysis = self._stage_1_analyze(protected_text, tone)
        stage_log.append(f"  Found {len(analysis.get('ai_phrases', []))} AI patterns")

        # ── Stage 2: Humanize ────────────────────────────────────────────
        stage_log.append("Stage 2: Rewriting with anti-AI constraints…")
        humanized = self._stage_2_humanize(
            protected_text, tone, language, analysis
        )

        # ── Stage 3: Quality gate ────────────────────────────────────────
        stage_log.append("Stage 3: Quality gate…")
        humanized, gate_passed, gate_notes = self._stage_3_quality_gate(
            original_text=protected_text,
            rewritten_text=humanized,
            entity_map=entity_map,
            original_word_count=original_word_count,
            tone=tone,
            language=language,
            analysis=analysis,
        )
        stage_log.extend(gate_notes)

        # ── Stage 4: Iterative refinement ────────────────────────────────
        iterations = 0
        detection = self.detector.detect(humanized)
        current_score = detection.get("ai_score", 0)

        while current_score > 35 and iterations < self.max_refinement_loops:
            iterations += 1
            stage_log.append(
                f"Stage 4: Refinement pass {iterations} (heuristic score: {current_score})…"
            )
            humanized = self._stage_4_refine(
                humanized, tone, language, detection
            )
            detection = self.detector.detect(humanized)
            current_score = detection.get("ai_score", 0)

        if iterations > 0:
            stage_log.append(f"  Refinement complete after {iterations} pass(es). Final score: {current_score}")
        else:
            stage_log.append(f"  Heuristic score {current_score} — no refinement needed")

        # ── Restore entities & clean ─────────────────────────────────────
        humanized = self._restore_entities(humanized, entity_map)
        humanized = self._clean_output(humanized)

        return {
            "humanized": humanized,
            "iterations": iterations,
            "stage_log": stage_log,
        }

    def analyze_text(self, text: str, tone: str = "casual") -> Dict[str, object]:
        """Heuristic structural analysis (used by the API for before/after comparison)."""
        doc = nlp(text)
        sentences = [sent.text.strip() for sent in doc.sents if sent.text.strip()]
        sentence_lengths = [len(sent.split()) for sent in sentences]
        avg_length = (
            round(sum(sentence_lengths) / len(sentence_lengths), 1)
            if sentence_lengths
            else 0
        )

        openings = [
            re.sub(r"[^a-z']", "", sent.split()[0].lower())
            for sent in sentences
            if sent.split()
        ]
        repeated_openers = sorted(
            {token for token in openings if token and openings.count(token) > 1}
        )
        contractions = len(re.findall(r"\b\w+'\w+\b", text))
        punctuation_density = len(re.findall(r"[,:;!?-]", text))
        paragraphs = [part for part in re.split(r"\n\s*\n", text) if part.strip()]

        issues: List[str] = []
        if sentence_lengths and max(sentence_lengths) - min(sentence_lengths) < 8:
            issues.append("sentence rhythm is too uniform")
        if avg_length > 24:
            issues.append("sentences run long and read as over-compressed")
        if repeated_openers:
            issues.append("several sentences start the same way")
        if contractions == 0 and tone == "casual":
            issues.append("voice sounds stiff for a casual tone")
        if punctuation_density < max(1, len(sentences) // 3):
            issues.append("cadence relies on plain statement-after-statement flow")
        if len(paragraphs) <= 1 and len(sentences) >= 6:
            issues.append("the structure would benefit from paragraph breaks")

        strengths: List[str] = []
        if avg_length and avg_length < 22:
            strengths.append("sentences are reasonably readable")
        if len(set(openings)) >= max(1, len(openings) // 2):
            strengths.append("sentence openings already have some variation")
        if paragraphs and len(paragraphs) > 1:
            strengths.append("the text already has visible paragraph structure")

        return {
            "tone": tone,
            "sentence_count": len(sentences),
            "average_sentence_length": avg_length,
            "repeated_openers": repeated_openers[:5],
            "issues": issues,
            "strengths": strengths,
        }

    # ──────────────────────────────────────────────────────────────────────────
    # Pipeline stages
    # ──────────────────────────────────────────────────────────────────────────

    def _stage_1_analyze(self, text: str, tone: str) -> Dict:
        """Use the LLM itself to identify AI-like patterns in the text."""
        system_prompt = (
            "You are an expert in identifying AI-generated text. "
            "Analyze the following text and return a JSON object with these keys:\n"
            '  "ai_phrases": list of specific phrases/sentences that sound AI-generated,\n'
            '  "structural_issues": list of structural problems (uniform sentence length, repetitive openers, etc.),\n'
            '  "tone_mismatches": list of phrases that don\'t match the target tone,\n'
            '  "suggestions": list of specific improvement suggestions\n'
            "Return ONLY valid JSON. No markdown, no explanation."
        )
        user_prompt = f"Target tone: {tone}\n\nText to analyze:\n{text}"

        result = self._call_llm(system_prompt, user_prompt, temperature=0.3)

        if result:
            try:
                # Try to extract JSON from the response
                json_match = re.search(r'\{[\s\S]*\}', result)
                if json_match:
                    return _safe_json_parse(json_match.group())
            except Exception:
                pass

        # Fallback: return basic heuristic analysis
        return {
            "ai_phrases": [w for w in AI_WATERMARK_WORDS if w.lower() in text.lower()],
            "structural_issues": [],
            "tone_mismatches": [],
            "suggestions": [],
        }

    def _stage_2_humanize(
        self,
        text: str,
        tone: str,
        language: str,
        analysis: Dict,
    ) -> str:
        """Core humanization: rewrite with deep anti-AI constraints."""
        tone_instruction = TONE_INSTRUCTIONS.get(tone, TONE_INSTRUCTIONS["casual"])

        # Build the banned-words list from analysis
        ai_phrases = analysis.get("ai_phrases", [])
        banned_list = ", ".join(f'"{p}"' for p in list(AI_WATERMARK_WORDS)[:25])

        system_prompt = (
            "You are a skilled human editor. Your job is to rewrite text so it reads "
            "like a real person wrote it — not a machine.\n\n"
            "ABSOLUTE RULES:\n"
            "1. Preserve EVERY fact, statistic, name, date, and citation. Do not invent new information.\n"
            "2. The rewritten text MUST be approximately the SAME LENGTH as the original "
            "(within ±15% word count). Do NOT summarize or condense.\n"
            "3. Output ONLY the rewritten text. No preambles, no 'Here is...', no explanations.\n"
            "4. Do NOT use any of these AI-signature words/phrases: " + banned_list + "\n"
            "5. Vary sentence lengths naturally. Mix short punchy sentences (5-8 words) "
            "with medium ones (12-18 words) and occasional longer ones (20-30 words).\n"
            "6. Use different sentence starters. Never start 3+ consecutive sentences the same way.\n"
            "7. Prefer active voice. Use passive only when the subject is genuinely unknown.\n"
            "8. Replace vague/inflated words with concrete, specific alternatives.\n"
            "9. Add natural hedging where appropriate ('seems', 'appears', 'tends to').\n"
            "10. Keep paragraph structure. If input has multiple paragraphs, output should too.\n\n"
            f"TONE: {tone_instruction}\n"
            f"LANGUAGE: {language}\n"
        )

        # Include analysis context for smarter rewriting
        issues_text = ""
        if ai_phrases:
            issues_text += f"\nAI patterns found in this text that MUST be eliminated:\n"
            for phrase in ai_phrases[:10]:
                issues_text += f"  - {phrase}\n"

        structural_issues = analysis.get("structural_issues", [])
        if structural_issues:
            issues_text += f"\nStructural issues to fix:\n"
            for issue in structural_issues[:5]:
                issues_text += f"  - {issue}\n"

        suggestions = analysis.get("suggestions", [])
        if suggestions:
            issues_text += f"\nSpecific suggestions:\n"
            for s in suggestions[:5]:
                issues_text += f"  - {s}\n"

        user_prompt = (
            f"Rewrite this text so it feels naturally authored and well-edited. "
            f"Keep the same length and all facts.\n"
            f"{issues_text}\n"
            f"TEXT TO REWRITE:\n{text}"
        )

        result = self._call_llm(
            system_prompt,
            user_prompt,
            temperature=0.75 if tone != "academic" else 0.55,
            max_tokens=max(4096, len(text.split()) * 3),
        )

        return result if result else self._fallback_rewrite(text, tone)

    def _stage_3_quality_gate(
        self,
        original_text: str,
        rewritten_text: str,
        entity_map: Dict[str, str],
        original_word_count: int,
        tone: str,
        language: str,
        analysis: Dict,
    ) -> Tuple[str, bool, List[str]]:
        """
        Validate quality of the rewrite.
        Returns (text, passed, notes).
        If failed, attempts one corrective rewrite.
        """
        notes: List[str] = []
        rewritten_word_count = len(rewritten_text.split())

        # Check 1: Length preservation
        length_ratio = rewritten_word_count / max(original_word_count, 1)
        length_ok = 0.80 <= length_ratio <= 1.20

        if not length_ok:
            pct = round((length_ratio - 1) * 100)
            direction = "shorter" if pct < 0 else "longer"
            notes.append(f"  ⚠ Length: {abs(pct)}% {direction} ({rewritten_word_count} vs {original_word_count} words)")
        else:
            notes.append(f"  ✓ Length preserved ({rewritten_word_count} vs {original_word_count} words)")

        # Check 2: Entity preservation
        missing_entities = []
        for placeholder, original_entity in entity_map.items():
            if placeholder not in rewritten_text and original_entity.lower() not in rewritten_text.lower():
                missing_entities.append(original_entity)

        entities_ok = len(missing_entities) == 0
        if not entities_ok:
            notes.append(f"  ⚠ Missing entities: {', '.join(missing_entities[:5])}")
        else:
            notes.append(f"  ✓ All {len(entity_map)} entities preserved")

        # Check 3: No preamble/meta-text
        preamble_ok = not bool(re.match(
            r"^(Here is|Sure|Certainly|Of course|I've|I have|The following|Below)",
            rewritten_text,
            re.IGNORECASE,
        ))
        if not preamble_ok:
            notes.append("  ⚠ Output starts with a preamble — stripping it")
            rewritten_text = re.sub(
                r"^(Here is|Sure|Certainly|Of course|I've|I have|The following|Below)[^\n]*\n+",
                "",
                rewritten_text,
                flags=re.IGNORECASE,
            )

        # Check 4: AI watermark words still present
        remaining_watermarks = [
            w for w in AI_WATERMARK_WORDS
            if re.search(rf'\b{re.escape(w)}\b', rewritten_text, re.IGNORECASE)
        ]
        watermarks_ok = len(remaining_watermarks) <= 2
        if not watermarks_ok:
            notes.append(f"  ⚠ AI watermarks still present: {', '.join(remaining_watermarks[:5])}")

        passed = length_ok and entities_ok and preamble_ok and watermarks_ok

        # If failed, try one corrective pass
        if not passed and self.llm.is_available:
            notes.append("  → Running corrective rewrite…")

            fix_instructions = []
            if not length_ok:
                if length_ratio < 0.85:
                    fix_instructions.append(
                        f"The rewrite is too short ({rewritten_word_count} words vs original {original_word_count}). "
                        f"Expand it back to approximately {original_word_count} words by adding detail and "
                        f"elaboration WITHOUT inventing new facts."
                    )
                else:
                    fix_instructions.append(
                        f"The rewrite is too long ({rewritten_word_count} words vs original {original_word_count}). "
                        f"Trim it to approximately {original_word_count} words."
                    )
            if not entities_ok:
                fix_instructions.append(
                    f"These entities were lost and MUST appear in the output: {', '.join(missing_entities)}"
                )
            if remaining_watermarks:
                fix_instructions.append(
                    f"Replace these AI-sounding words with natural alternatives: {', '.join(remaining_watermarks)}"
                )

            corrective_prompt = (
                "Fix the following issues with this rewritten text, "
                "but keep the overall quality and natural feel.\n\n"
                "ISSUES:\n" + "\n".join(f"- {i}" for i in fix_instructions) + "\n\n"
                "TEXT TO FIX:\n" + rewritten_text
            )

            fixed = self._call_llm(
                "You are a precise editor. Fix only what is asked. "
                "Output ONLY the corrected text, nothing else.",
                corrective_prompt,
                temperature=0.4,
                max_tokens=max(4096, original_word_count * 3),
            )
            if fixed:
                rewritten_text = fixed
                notes.append("  ✓ Corrective rewrite applied")

        return rewritten_text, passed, notes

    def _stage_4_refine(
        self,
        text: str,
        tone: str,
        language: str,
        detection: Dict,
    ) -> str:
        """Targeted refinement pass to reduce AI detection score."""
        patterns = detection.get("patterns", [])
        metrics = detection.get("metrics", {})

        refinement_instructions = []

        if patterns:
            refinement_instructions.append(
                f"Replace these AI-flagged phrases with natural alternatives: {', '.join(patterns[:8])}"
            )

        burstiness = metrics.get("burstiness_std_dev", 10)
        if burstiness < 5:
            refinement_instructions.append(
                "The sentences are too uniform in length. Break some long sentences into "
                "shorter ones. Combine some short sentences into longer, flowing ones."
            )

        entropy = metrics.get("entropy", 5)
        if entropy < 4.0:
            refinement_instructions.append(
                "The vocabulary is too repetitive. Use more varied word choices "
                "and avoid repeating the same terms."
            )

        if not refinement_instructions:
            refinement_instructions.append(
                "Make the text feel more naturally written. Add occasional informal "
                "touches, vary the rhythm, and use more specific/concrete language."
            )

        tone_instruction = TONE_INSTRUCTIONS.get(tone, TONE_INSTRUCTIONS["casual"])

        system_prompt = (
            "You are a text refinement specialist. Your goal is to make text sound "
            "like it was written by a real human, not generated by AI.\n"
            "Rules: preserve all facts, maintain the same length (±10%), "
            f"output ONLY the refined text.\nTone: {tone_instruction}"
        )

        user_prompt = (
            "Refine this text to address these specific issues:\n"
            + "\n".join(f"- {i}" for i in refinement_instructions)
            + f"\n\nTEXT:\n{text}"
        )

        result = self._call_llm(system_prompt, user_prompt, temperature=0.7)
        return result if result else text

    # ──────────────────────────────────────────────────────────────────────────
    # Helpers
    # ──────────────────────────────────────────────────────────────────────────

    def _call_llm(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> Optional[str]:
        """Call cloud LLM."""
        if self.llm.is_available:
            return self.llm.generate(system_prompt, user_prompt, temperature, max_tokens)

        return None


    def _split_paragraphs(self, text: str) -> List[str]:
        normalized = text.replace("\r\n", "\n").strip()
        return re.split(r"\n\s*\n", normalized)

    def _extract_entities(self, text: str) -> Tuple[str, Dict[str, str]]:
        doc = nlp(text)
        entity_map: Dict[str, str] = {}
        processed_text = text

        for i, ent in enumerate(doc.ents):
            if ent.label_ in ["PERSON", "ORG", "GPE", "PRODUCT", "LOC", "DATE"]:
                placeholder = f"[ENTITY_{i}]"
                entity_map[placeholder] = ent.text
                processed_text = processed_text.replace(ent.text, placeholder, 1)

        return processed_text, entity_map

    def _restore_entities(self, text: str, entity_map: Dict[str, str]) -> str:
        for placeholder, original in entity_map.items():
            match = re.search(r"\d+", placeholder)
            if match:
                idx = match.group()
                pattern = re.compile(rf"\[?ENTIT[Yy]?_{idx}\]?", re.IGNORECASE)
                text = pattern.sub(original, text)
            text = text.replace(placeholder, original)
        return text

    def _clean_output(self, text: str) -> str:
        # Remove common LLM preambles
        text = re.sub(r"^Here is .*?:\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(
            r"^(Rewrite|Rewritten|Edited|Humanized|Text|Sure|Certainly|Of course)[^\n]*:\s*",
            "",
            text,
            flags=re.IGNORECASE,
        )
        text = text.replace("```", "")
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()

    def _fallback_rewrite(self, text: str, tone: str) -> str:
        """Minimal rule-based rewrite when no LLM is available at all."""
        text = re.sub(r"\s+", " ", text).strip()
        if tone == "casual":
            text = re.sub(r"\bdo not\b", "don't", text, flags=re.IGNORECASE)
            text = re.sub(r"\bcannot\b", "can't", text, flags=re.IGNORECASE)
            text = re.sub(r"\bwill not\b", "won't", text, flags=re.IGNORECASE)
            text = re.sub(r"\bshould not\b", "shouldn't", text, flags=re.IGNORECASE)
        # Replace common AI watermarks
        replacements = {
            "Furthermore": "Also",
            "Moreover": "On top of that",
            "In conclusion": "To wrap up",
            "It is worth noting": "Worth mentioning",
            "Additionally": "Plus",
            "Consequently": "So",
            "Nevertheless": "Still",
            "utilize": "use",
            "leverage": "use",
            "facilitate": "help",
            "comprehensive": "thorough",
            "robust": "strong",
        }
        for old, new in replacements.items():
            text = re.sub(rf"\b{re.escape(old)}\b", new, text, flags=re.IGNORECASE)
        return text


def _safe_json_parse(text: str) -> Dict:
    """Parse JSON, stripping markdown fences if present."""
    import json as _json

    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    try:
        return _json.loads(text)
    except _json.JSONDecodeError:
        # Try to find a JSON object in the text
        match = re.search(r'\{[\s\S]*\}', text)
        if match:
            return _json.loads(match.group())
        return {"ai_phrases": [], "structural_issues": [], "tone_mismatches": [], "suggestions": []}
