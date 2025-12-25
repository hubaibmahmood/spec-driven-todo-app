"""Gemini API key validation service."""

import asyncio
from typing import Tuple, Optional

try:
    from google import genai
    from google.genai import types
    from google.api_core.exceptions import Unauthenticated, ResourceExhausted
except ImportError:
    # Allow importing even if google-genai is not installed (for testing)
    genai = None
    types = None
    Unauthenticated = Exception
    ResourceExhausted = Exception


class GeminiValidator:
    """Validates Gemini API keys via format and connectivity tests."""

    @staticmethod
    def validate_format(api_key: str) -> Tuple[bool, Optional[str]]:
        """
        Check if API key has valid Gemini format.

        Gemini API keys typically start with 'AIza' and are 39 characters long.

        Args:
            api_key: The API key to validate

        Returns:
            Tuple of (is_valid, error_message)
            - (True, None) if valid
            - (False, error_message) if invalid
        """
        if not api_key or not isinstance(api_key, str):
            return False, "API key cannot be empty"

        api_key = api_key.strip()

        if len(api_key) < 20:
            return False, "API key is too short (minimum 20 characters)"

        if not api_key.startswith('AIza'):
            return False, "Invalid format. Gemini API keys typically start with 'AIza'"

        return True, None

    @staticmethod
    async def validate_key(api_key: str) -> Tuple[bool, Optional[str]]:
        """
        Test API key by making a minimal request to Gemini API.

        Makes a lightweight generateContent request with a 1-word prompt
        to verify the key is valid and has access to the Gemini API.

        Args:
            api_key: The API key to test

        Returns:
            Tuple of (is_valid, error_message)
            - (True, None) if key is valid and working
            - (False, error_message) if key is invalid or failed
        """
        if genai is None:
            return False, "google-genai library not installed"

        # Format check first
        valid, error = GeminiValidator.validate_format(api_key)
        if not valid:
            return False, error

        try:
            # Create Gemini client with user's API key (new API)
            client = genai.Client(api_key=api_key.strip())

            # Run in thread pool to avoid blocking async event loop
            response = await asyncio.wait_for(
                asyncio.to_thread(
                    lambda: client.models.generate_content(
                        model='gemini-1.5-flash',
                        contents='hi'
                    )
                ),
                timeout=10.0  # 10-second timeout requirement
            )

            # Verify response is valid
            if response and response.text:
                return True, None

            return False, "Invalid response from Gemini API"

        except asyncio.TimeoutError:
            return False, "Request timeout after 10 seconds"
        except Unauthenticated:
            return False, "API key is invalid or expired"
        except ResourceExhausted:
            return False, "API key quota exceeded"
        except Exception as e:
            error_str = str(e).lower()
            if "network" in error_str or "connection" in error_str:
                return False, "Network error. Check your connection."
            if "quota" in error_str or "rate" in error_str:
                return False, "API quota or rate limit exceeded"
            return False, f"Validation failed: {str(e)[:100]}"
