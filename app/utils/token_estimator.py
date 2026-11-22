from config.settings import CHARS_PER_TOKEN_ESTIMATE


def estimate_tokens(text: str) -> int:
    """Estimate token count using a configurable character ratio."""

    # Reject non-string input to prevent invalid calculations.
    if not isinstance(text, str):
        raise TypeError("Text must be a string.")

    # Return zero when the input contains no characters.
    if not text:
        return 0

    # Estimate tokens and round up to avoid underestimating the count.
    return (
        len(text) + CHARS_PER_TOKEN_ESTIMATE - 1
    ) // CHARS_PER_TOKEN_ESTIMATE
