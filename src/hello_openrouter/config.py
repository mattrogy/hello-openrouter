"""All settings for hello-openrouter, kept in one place.

To compare different models, change the IDs in MODELS. The full list of
available IDs is at https://openrouter.ai/models
"""

# OpenRouter speaks the same API as OpenAI, so the OpenAI SDK works with this URL.
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# The two models to compare. IDs checked against OpenRouter's live models list on 2026-10-19.
MODELS = [
    "anthropic/claude-sonnet-5.5",
    "mistralai/mistral-large-4-0",
]

# Used when no question is given on the command line.
DEFAULT_QUESTION = (
    "In three sentences, what should a company check before deploying an AI assistant to its customers?"
)
