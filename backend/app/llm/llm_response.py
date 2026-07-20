from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class LLMResponse:
    """
    Standardisierte Antwort eines LLM.
    """

    text: str

    model: str

    prompt_tokens: int

    completion_tokens: int

    total_tokens: int

    finish_reason: str