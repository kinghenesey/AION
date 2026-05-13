# =============================================================
# AION AI Runtime — Anthropic Claude Provider
# =============================================================
# This provider connects AION to Anthropic's Claude API.
#
# To activate:
#   1. Get an API key from https://console.anthropic.com
#   2. Create a .env file in your AION root folder
#   3. Add this line:  ANTHROPIC_API_KEY=sk-ant-your-key-here
#   4. Change provider to "claude" in ai/__init__.py
#
# The rest of your AION code stays exactly the same.

import os
from ai.providers.base import BaseProvider


class AnthropicProvider(BaseProvider):
    """
    Connects AION to Anthropic's Claude AI model.
    Requires ANTHROPIC_API_KEY environment variable.
    """

    MODEL   = "claude-haiku-4-5-20251001"  # Fast and affordable
    MAX_TOKENS = 1024

    def __init__(self):
        self.api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        self._client = None

    def _get_client(self):
        """Lazy-load the Anthropic client."""
        if self._client is None:
            try:
                import anthropic
                self._client = anthropic.Anthropic(
                    api_key=self.api_key
                )
            except ImportError:
                raise RuntimeError(
                    "The 'anthropic' package is not installed.\n"
                    "  Run:  pip install anthropic"
                )
        return self._client

    @property
    def name(self) -> str:
        return "claude"

    @property
    def is_available(self) -> bool:
        return bool(self.api_key)

    def ask(self, prompt: str) -> str:
        """Send a question to Claude and return the answer."""
        return self._complete(prompt)

    def summarize(self, text: str) -> str:
        """Ask Claude to summarize a piece of text."""
        prompt = (
            f"Please summarize the following text clearly "
            f"and concisely in 2-3 sentences:\n\n{text}"
        )
        return self._complete(prompt)

    def generate(self, instruction: str) -> str:
        """Ask Claude to generate content from an instruction."""
        prompt = (
            f"Please generate the following. "
            f"Be concise and direct:\n\n{instruction}"
        )
        return self._complete(prompt)

    def classify(self, text: str, labels: list) -> str:
        """Ask Claude to classify text into one of the labels."""
        labels_str = ", ".join(labels)
        prompt = (
            f"Classify the following text into exactly one "
            f"of these categories: {labels_str}\n\n"
            f"Text: {text}\n\n"
            f"Reply with only the category name, nothing else."
        )
        result = self._complete(prompt)
        # Clean up response
        result = result.strip().lower()
        # Make sure it matches one of our labels
        for label in labels:
            if label.lower() in result:
                return label
        return labels[0]

    def _complete(self, prompt: str) -> str:
        """
        Core method — sends a prompt to Claude and
        returns the text response.
        """
        if not self.is_available:
            raise RuntimeError(
                "No Anthropic API key found.\n"
                "  Add ANTHROPIC_API_KEY to your .env file.\n"
                "  Get a key at: https://console.anthropic.com"
            )

        try:
            client  = self._get_client()
            message = client.messages.create(
                model=self.MODEL,
                max_tokens=self.MAX_TOKENS,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return message.content[0].text

        except Exception as e:
            raise RuntimeError(
                f"Claude API error: {str(e)}\n"
                f"  Check your API key and internet connection."
            )