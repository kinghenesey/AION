# =============================================================
# AION AI Runtime — Provider Registry
# =============================================================
# This is the central registry for all AI providers.
# It decides which provider to use based on availability.
#
# Priority order:
#   1. Claude (if ANTHROPIC_API_KEY is set)
#   2. Mock   (always available as fallback)
#
# To add a new provider in the future:
#   1. Create the provider file in ai/providers/
#   2. Import it here
#   3. Add it to the PROVIDERS list

from ai.providers.mock       import MockProvider
from ai.providers.anthropic  import AnthropicProvider


# ── Provider registry ─────────────────────────────────────────
# Ordered by preference — first available one wins

PROVIDERS = [
    AnthropicProvider,
    MockProvider,
]


def get_provider():
    """
    Return the best available AI provider.
    Automatically picks Claude if API key exists,
    otherwise falls back to Mock.
    """
    for ProviderClass in PROVIDERS:
        provider = ProviderClass()
        if provider.is_available:
            return provider

    # Should never reach here since Mock is always available
    return MockProvider()


def get_provider_by_name(name: str):
    """
    Get a specific provider by name.
    Useful for testing or forcing a specific provider.
    """
    providers = {
        "mock":   MockProvider,
        "claude": AnthropicProvider,
    }

    if name not in providers:
        available = ", ".join(providers.keys())
        raise ValueError(
            f"Unknown provider '{name}'.\n"
            f"  Available providers: {available}"
        )

    return providers[name]()