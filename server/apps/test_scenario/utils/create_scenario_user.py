"""
create_scenario_user

Delete any existing user for a test scenario and create a fresh one from
the template's ``user`` section.
"""

import hashlib
import uuid

from apps.users.models import User


def create_scenario_user(scenario, template: dict) -> tuple:
    """
    Delete any existing scenario user, then create a fresh one.

    The email is taken from the template if it is globally unique; otherwise
    a deterministic SHA-256-based email is generated to guarantee uniqueness.

    Args:
        scenario: The TestScenario instance this user belongs to.
        template: The full scenario template dict. Must contain a ``user`` key.

    Returns:
        A 2-tuple of ``(user, unique_email)`` where ``user`` is the newly
        created User instance and ``unique_email`` is the email assigned to it.

    Raises:
        ValueError: If the User cannot be created due to invalid template data.
    """
    User.objects.filter(test_scenario=scenario).delete()
    user_data = dict(template.get("user") or {})
    password = "Coach123!"

    base_email = user_data.get("email")
    if not base_email or User.objects.filter(email=base_email).exists():
        hash_input = f"{scenario.id}-{uuid.uuid4()}"
        unique_email = (
            f"test_user_{hashlib.sha256(hash_input.encode()).hexdigest()[:8]}"
            f"@testscenario.com"
        )
    else:
        unique_email = base_email

    user_data["email"] = unique_email

    # Strip fields that shouldn't reach the User constructor
    for key in (
        "password",
        "id",
        "user_id",
        "created_at",
        "updated_at",
        "last_login",
        "date_joined",
    ):
        user_data.pop(key, None)

    try:
        user = User(**user_data, test_scenario=scenario)
        user.set_password(password)
        user.save()
        return user, unique_email
    except Exception as e:
        raise ValueError(f"Failed to create user: {e}") from e
