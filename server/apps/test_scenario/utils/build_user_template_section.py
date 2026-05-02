"""
build_user_template_section

Build the ``user`` section of a scenario template from a User model instance.
"""


def build_user_template_section(
    user,
    first_name: str = "",
    last_name: str = "",
) -> dict:
    """
    Build the user section dict for a scenario template.

    Uses the provided override names first, falling back to the user's
    existing names, then to "Test" / "User" as defaults.

    Args:
        user: The User model instance to extract data from.
        first_name: Override for the template user's first name.
        last_name: Override for the template user's last name.

    Returns:
        Dict with ``email``, ``first_name``, and ``last_name`` keys.

    Example:
        >>> build_user_template_section(user, first_name="Alice")
        {"email": "alice@example.com", "first_name": "Alice", "last_name": "Smith"}
    """
    return {
        "email": user.email,
        "first_name": first_name.strip() or user.first_name or "Test",
        "last_name": last_name.strip() or user.last_name or "User",
    }
