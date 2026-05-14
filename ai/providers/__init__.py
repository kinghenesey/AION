# =============================================================
# AION AI Runtime — Provider Registry
# =============================================================
# Priority order:
#   1. Gemini  (if GEMINI_API_KEY is set)
#   2. Claude  (if ANTHROPIC_API_KEY is set)
#   3. Mock    (always available as fallback)

from ai.providers.mock      import MockProvider
from ai.providers.anthropic import AnthropicProvider
from ai.providers.gemini    import GeminiProvider


PROVIDERS = [
    GeminiProvider,
    AnthropicProvider,
    MockProvider,
]


def get_provider():
    """
    Return the best available AI provider.
    Automatically picks Gemini if key exists,
    then Claude, then Mock.
    """
    for ProviderClass in PROVIDERS:
        provider = ProviderClass()
        if provider.is_available:
            return provider

    return MockProvider()


def get_provider_by_name(name: str):
    """Get a specific provider by name."""
    providers = {
        "mock":   MockProvider,
        "claude": AnthropicProvider,
        "gemini": GeminiProvider,
    }

    if name not in providers:
        available = ", ".join(providers.keys())
        raise ValueError(
            f"Unknown provider '{name}'.\n"
            f"  Available providers: {available}"
        )

    return providers[name]()