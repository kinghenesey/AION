# =============================================================
# AION AI Runtime — Google Gemini Provider
# =============================================================
# Uses the new google-genai SDK (replaces google-generativeai)
# Get a free API key at: https://aistudio.google.com

import os
from ai.providers.base import BaseProvider


class GeminiProvider(BaseProvider):
    """
    Connects AION to Google Gemini AI.
    Requires GEMINI_API_KEY environment variable.
    """

    MODEL = "gemini-2.5-flash"

    def __init__(self):
        self.api_key = os.environ.get("GEMINI_API_KEY", "")
        self._client = None

    def _get_client(self):
        """Lazy-load the Gemini client."""
        if self._client is None:
            try:
                from google import genai
                self._client = genai.Client(
                    api_key=self.api_key)
            except ImportError:
                raise RuntimeError(
                    "The 'google-genai' package "
                    "is not installed.\n"
                    "  Run: pip install google-genai"
                )
        return self._client

    @property
    def name(self) -> str:
        return "gemini"

    @property
    def is_available(self) -> bool:
        return bool(self.api_key)

    def ask(self, prompt: str) -> str:
        return self._complete(prompt)

    def summarize(self, text: str) -> str:
        prompt = (
            f"Summarize the following text clearly "
            f"and concisely in 2-3 sentences:\n\n{text}"
        )
        return self._complete(prompt)

    def generate(self, instruction: str) -> str:
        prompt = (
            f"Generate the following. "
            f"Be concise and direct:\n\n{instruction}"
        )
        return self._complete(prompt)

    def classify(self, text: str,
                 labels: list) -> str:
        labels_str = ", ".join(labels)
        prompt = (
            f"Classify the following text into exactly "
            f"one of these categories: {labels_str}\n\n"
            f"Text: {text}\n\n"
            f"Reply with only the category name."
        )
        result = self._complete(prompt)
        result = result.strip().lower()
        for label in labels:
            if label.lower() in result:
                return label
        return labels[0]

    def _complete(self, prompt: str) -> str:
        """Send a prompt to Gemini and return response."""
        if not self.is_available:
            raise RuntimeError(
                "No Gemini API key found.\n"
                "  Add GEMINI_API_KEY to your .env file.\n"
                "  Get a free key at: "
                "https://aistudio.google.com"
            )

        try:
            from google import genai
            client   = self._get_client()
            response = client.models.generate_content(
                model=self.MODEL,
                contents=prompt
            )
            return response.text

        except Exception as e:
            raise RuntimeError(
                f"Gemini API error: {str(e)}\n"
                f"  Check your API key and try again."
            )