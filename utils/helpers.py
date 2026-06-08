"""
Utility functions and helpers.
"""
import uuid
import hashlib
from django.utils.text import slugify


def generate_unique_id():
    """Generate a unique ID."""
    return str(uuid.uuid4())


def generate_slug(text):
    """Generate a URL-friendly slug."""
    return slugify(text)


def hash_string(text):
    """Generate SHA256 hash of a string."""
    return hashlib.sha256(text.encode()).hexdigest()


def calculate_platform_fee(amount, percentage=15):
    """Calculate platform fee."""
    return round(amount * (percentage / 100), 2)


def format_currency(amount, currency=None):
    """Format amount with platform currency (default NPR)."""
    from django.conf import settings

    currency = currency or getattr(settings, 'DEFAULT_CURRENCY', 'NPR')
    try:
        value = float(amount)
    except (TypeError, ValueError):
        value = 0.0

    if value == int(value):
        formatted = f"{int(value):,}"
    else:
        formatted = f"{value:,.2f}".rstrip('0').rstrip('.')

    return f"{currency} {formatted}"
