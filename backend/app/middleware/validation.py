"""
Input sanitization middleware - Prevents XSS and injection attacks
"""
import bleach
from typing import Any, Dict, List, Optional
import re


class InputSanitizer:
    """
    Sanitizes user input to prevent XSS and injection attacks
    """

    # Allowed HTML tags for rich text (keep safe formatting)
    ALLOWED_TAGS = [
        'p', 'br', 'strong', 'em', 'u', 'a', 'ul', 'ol', 'li',
        'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'blockquote', 'code', 'pre'
    ]

    # Allowed HTML attributes
    ALLOWED_ATTRIBUTES = {
        'a': ['href', 'title', 'target'],
        '*': ['class']  # Allow class on any element
    }

    # Allowed protocols for links
    ALLOWED_PROTOCOLS = ['http', 'https', 'mailto']

    @staticmethod
    def sanitize_html(text: Optional[str], strip_all: bool = False) -> Optional[str]:
        """
        Sanitize HTML content to prevent XSS attacks

        Args:
            text: The text to sanitize
            strip_all: If True, strip all HTML tags. If False, keep safe tags.

        Returns:
            Sanitized text or None if input is None
        """
        if text is None:
            return None

        if not isinstance(text, str):
            return str(text)

        if strip_all:
            # Strip all HTML tags
            return bleach.clean(text, tags=[], strip=True)
        else:
            # Keep safe HTML tags
            return bleach.clean(
                text,
                tags=InputSanitizer.ALLOWED_TAGS,
                attributes=InputSanitizer.ALLOWED_ATTRIBUTES,
                protocols=InputSanitizer.ALLOWED_PROTOCOLS,
                strip=True  # Strip disallowed tags instead of escaping
            )

    @staticmethod
    def sanitize_plain_text(text: Optional[str]) -> Optional[str]:
        """
        Sanitize plain text input (names, titles, etc.)
        Strips all HTML tags and dangerous characters

        Args:
            text: The text to sanitize

        Returns:
            Sanitized text or None if input is None
        """
        if text is None:
            return None

        if not isinstance(text, str):
            text = str(text)

        # Strip all HTML tags
        text = bleach.clean(text, tags=[], strip=True)

        # Remove null bytes
        text = text.replace('\x00', '')

        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text).strip()

        return text

    @staticmethod
    def sanitize_url(url: Optional[str]) -> Optional[str]:
        """
        Sanitize URL input to prevent javascript: and data: protocols

        Args:
            url: The URL to sanitize

        Returns:
            Sanitized URL or None if invalid
        """
        if url is None:
            return None

        if not isinstance(url, str):
            url = str(url)

        url = url.strip()

        # Block dangerous protocols
        dangerous_protocols = ['javascript:', 'data:', 'vbscript:', 'file:']
        url_lower = url.lower()

        for protocol in dangerous_protocols:
            if url_lower.startswith(protocol):
                return None

        # Only allow http, https, mailto
        if not (url_lower.startswith('http://') or
                url_lower.startswith('https://') or
                url_lower.startswith('mailto:') or
                url_lower.startswith('/')):  # Allow relative URLs
            return None

        return url

    @staticmethod
    def sanitize_dict(data: Dict[str, Any],
                     text_fields: List[str] = None,
                     html_fields: List[str] = None,
                     url_fields: List[str] = None) -> Dict[str, Any]:
        """
        Sanitize dictionary of inputs

        Args:
            data: Dictionary to sanitize
            text_fields: List of field names to sanitize as plain text
            html_fields: List of field names to sanitize as HTML (keep safe tags)
            url_fields: List of field names to sanitize as URLs

        Returns:
            Sanitized dictionary
        """
        sanitized = data.copy()

        # Sanitize plain text fields
        if text_fields:
            for field in text_fields:
                if field in sanitized:
                    sanitized[field] = InputSanitizer.sanitize_plain_text(sanitized[field])

        # Sanitize HTML fields
        if html_fields:
            for field in html_fields:
                if field in sanitized:
                    sanitized[field] = InputSanitizer.sanitize_html(sanitized[field])

        # Sanitize URL fields
        if url_fields:
            for field in url_fields:
                if field in sanitized:
                    sanitized[field] = InputSanitizer.sanitize_url(sanitized[field])

        return sanitized


class CoordinateValidator:
    """
    Validates geographic coordinates
    """

    @staticmethod
    def validate_latitude(lat: float) -> tuple[bool, Optional[str]]:
        """
        Validate latitude value

        Args:
            lat: Latitude value to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not isinstance(lat, (int, float)):
            return False, "Latitude must be a number"

        if lat < -90 or lat > 90:
            return False, f"Latitude must be between -90 and 90, got {lat}"

        return True, None

    @staticmethod
    def validate_longitude(lon: float) -> tuple[bool, Optional[str]]:
        """
        Validate longitude value

        Args:
            lon: Longitude value to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not isinstance(lon, (int, float)):
            return False, "Longitude must be a number"

        if lon < -180 or lon > 180:
            return False, f"Longitude must be between -180 and 180, got {lon}"

        return True, None

    @staticmethod
    def validate_coordinates(lat: float, lon: float) -> tuple[bool, Optional[str]]:
        """
        Validate both latitude and longitude

        Args:
            lat: Latitude value
            lon: Longitude value

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Validate latitude
        is_valid, error = CoordinateValidator.validate_latitude(lat)
        if not is_valid:
            return False, error

        # Validate longitude
        is_valid, error = CoordinateValidator.validate_longitude(lon)
        if not is_valid:
            return False, error

        return True, None


class RequestValidator:
    """
    Request-level validation
    """

    # Max request body size in bytes (10MB)
    MAX_BODY_SIZE = 10 * 1024 * 1024

    @staticmethod
    def validate_request_size(content_length: int) -> tuple[bool, Optional[str]]:
        """
        Validate request body size

        Args:
            content_length: Size of request body in bytes

        Returns:
            Tuple of (is_valid, error_message)
        """
        if content_length > RequestValidator.MAX_BODY_SIZE:
            return False, f"Request body too large: {content_length} bytes (max {RequestValidator.MAX_BODY_SIZE})"

        return True, None


# Convenience functions for common use cases

def sanitize_name(name: str) -> str:
    """Sanitize a name field (strip all HTML)"""
    return InputSanitizer.sanitize_plain_text(name) or ""


def sanitize_description(description: str) -> str:
    """Sanitize a description field (keep safe HTML formatting)"""
    return InputSanitizer.sanitize_html(description) or ""


def sanitize_story(story: str) -> str:
    """Sanitize a story/narrative field (keep safe HTML formatting)"""
    return InputSanitizer.sanitize_html(story) or ""


def validate_coords(lat: float, lon: float) -> None:
    """
    Validate coordinates and raise ValueError if invalid

    Args:
        lat: Latitude
        lon: Longitude

    Raises:
        ValueError: If coordinates are invalid
    """
    is_valid, error = CoordinateValidator.validate_coordinates(lat, lon)
    if not is_valid:
        raise ValueError(error)
