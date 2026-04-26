"""
Multi-provider LLM abstraction layer.
Supports: Gemini (default, free tier), OpenAI, and Anthropic.
"""

import os
import time
import json
import re
from typing import Optional


class LLMProvider:
    """Unified interface for multiple LLM providers."""

    def __init__(self):
        self.provider = os.getenv("LLM_PROVIDER", "gemini").lower()
        self.api_key = os.getenv("LLM_API_KEY", "")
        self.client = None
        self.model_name = None
        self._init_provider()

    def _init_provider(self):
        """Initialize the configured LLM provider."""
        if self.provider == "gemini":
            self._init_gemini()
        elif self.provider == "openai":
            self._init_openai()
        elif self.provider == "anthropic":
            self._init_anthropic()
        else:
            print(f"Unknown provider '{self.provider}', falling back to gemini")
            self.provider = "gemini"
            self._init_gemini()

    def _init_gemini(self):
        try:
            from google import genai
            self.client = genai.Client(api_key=self.api_key)
            self.model_name = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
            print(f"✅ Gemini provider initialized (model: {self.model_name})")
        except ImportError:
            print("❌ google-genai not installed. Run: pip install google-genai")
            self.client = None
        except Exception as e:
            print(f"❌ Gemini init failed: {e}")
            self.client = None

    def _init_openai(self):
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=self.api_key)
            self.model_name = os.getenv("OPENAI_MODEL", "gpt-4o")
            print(f"✅ OpenAI provider initialized (model: {self.model_name})")
        except ImportError:
            print("❌ openai not installed. Run: pip install openai")
            self.client = None
        except Exception as e:
            print(f"❌ OpenAI init failed: {e}")
            self.client = None

    def _init_anthropic(self):
        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=self.api_key)
            self.model_name = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")
            print(f"✅ Anthropic provider initialized (model: {self.model_name})")
        except ImportError:
            print("❌ anthropic not installed. Run: pip install anthropic")
            self.client = None
        except Exception as e:
            print(f"❌ Anthropic init failed: {e}")
            self.client = None

    @property
    def is_available(self) -> bool:
        return self.client is not None

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> Optional[str]:
        """
        Generate text using the configured LLM provider.
        Returns the generated text or None on failure.
        Includes retry logic with exponential backoff.
        """
        if not self.is_available:
            return None

        last_error = None
        for attempt in range(3):
            try:
                if self.provider == "gemini":
                    return self._call_gemini(system_prompt, user_prompt, temperature, max_tokens)
                elif self.provider == "openai":
                    return self._call_openai(system_prompt, user_prompt, temperature, max_tokens)
                elif self.provider == "anthropic":
                    return self._call_anthropic(system_prompt, user_prompt, temperature, max_tokens)
            except Exception as e:
                last_error = e
                wait_time = (2 ** attempt) + 1
                print(f"  LLM attempt {attempt + 1} failed: {e}. Retrying in {wait_time}s...")
                time.sleep(wait_time)

        print(f"❌ All LLM attempts failed. Last error: {last_error}")
        return None

    def _call_gemini(self, system_prompt, user_prompt, temperature, max_tokens):
        from google.genai import types

        response = self.client.models.generate_content(
            model=self.model_name,
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=temperature,
                max_output_tokens=max_tokens,
            ),
        )
        return response.text.strip() if response.text else None

    def _call_openai(self, system_prompt, user_prompt, temperature, max_tokens):
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        content = response.choices[0].message.content
        return content.strip() if content else None

    def _call_anthropic(self, system_prompt, user_prompt, temperature, max_tokens):
        response = self.client.messages.create(
            model=self.model_name,
            max_tokens=max_tokens,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
        )
        content = response.content[0].text
        return content.strip() if content else None
