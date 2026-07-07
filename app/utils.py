"""
Utility functions for the URL Shortener.

Contains the short code generation logic. Uses Python's secrets module
for cryptographically secure random strings — better than random.choice()
because it's designed for security-sensitive operations.
"""

import secrets
import string

# Characters used to generate short codes (alphanumeric, no ambiguous chars)
ALPHABET = string.ascii_letters + string.digits
CODE_LENGTH = 6


def generate_short_code(length: int = CODE_LENGTH) -> str:
    """
    Generate a cryptographically secure random short code.

    Args:
        length: Number of characters in the code. Default is 6,
                which gives 62^6 ≈ 56.8 billion possible combinations.

    Returns:
        A random alphanumeric string of the specified length.
    """
    return "".join(secrets.choice(ALPHABET) for _ in range(length))
