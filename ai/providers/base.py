# =============================================================
# AION AI Runtime — Base Provider
# =============================================================
# Every AI provider (Claude, GPT, Mock, Ollama) must inherit
# from this base class and implement these methods.
#
# This is called an "abstraction layer" — your AION code
# never knows which AI it's talking to. You can swap
# providers without changing a single line of AION code.

from abc import ABC, abstractmethod


class BaseProvider(ABC):
    """
    Abstract base class for all AION AI providers.

    To add a new AI provider:
        1. Create a new file in ai/providers/
        2. Inherit from BaseProvider
        3. Implement all abstract methods
        4. Register it in ai/providers/__init__.py
    """

    @abstractmethod
    def ask(self, prompt: str) -> str:
        """
        Send a prompt and get a response.
        Example:
            ask("What is the capital of Nigeria?")
            → "The capital of Nigeria is Abuja."
        """
        pass

    @abstractmethod
    def summarize(self, text: str) -> str:
        """
        Summarize a long piece of text.
        Example:
            summarize("AION is an AI-native language...")
            → "AION is a language with AI built in."
        """
        pass

    @abstractmethod
    def generate(self, instruction: str) -> str:
        """
        Generate content from an instruction.
        Example:
            generate("Write a poem about coding")
            → "In lines of code we build our dreams..."
        """
        pass

    @abstractmethod
    def classify(self, text: str, labels: list) -> str:
        """
        Classify text into one of the given labels.
        Example:
            classify("I love AION!", ["positive", "negative"])
            → "positive"
        """
        pass

    def stream(self, prompt: str) -> str:
        """
        Stream a response word by word.
        Falls back to ask() if not implemented.
        """
        return self.ask(prompt)

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the provider name e.g. 'claude', 'mock'."""
        pass

    @property
    @abstractmethod
    def is_available(self) -> bool:
        """Return True if this provider is ready to use."""
        pass