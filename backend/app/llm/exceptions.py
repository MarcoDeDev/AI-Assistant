class LLMError(Exception):
    """
    Basisklasse für alle LLM-Fehler.
    """


class LLMAuthenticationError(LLMError):
    """
    Authentifizierung fehlgeschlagen.
    """


class LLMRateLimitError(LLMError):
    """
    Rate Limit oder Quota erreicht.
    """


class LLMConnectionError(LLMError):
    """
    Verbindung zum LLM fehlgeschlagen.
    """


class LLMUnknownError(LLMError):
    """
    Unbekannter LLM-Fehler.
    """