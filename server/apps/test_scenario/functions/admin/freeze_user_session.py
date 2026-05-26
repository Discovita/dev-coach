"""
freeze_user_session

Capture ("freeze") a live user session as a new test scenario.

See: apps/test_scenario/functions/__init__.py
"""

from django.contrib.auth import get_user_model

from apps.test_scenario.functions.admin.instantiate_test_scenario import (
    instantiate_test_scenario,
)
from apps.test_scenario.models import TestScenario
from apps.test_scenario.utils.build_scenario_template import build_scenario_template
from apps.test_scenario.utils.validate_scenario_template import (
    validate_scenario_template,
)
from services.logger import configure_logging

User = get_user_model()
log = configure_logging(__name__)


class FreezeSessionError(Exception):
    """Raised when freezing a session fails for a domain-level reason."""

    def __init__(self, detail: str, *, status_code: int = 400):
        self.detail = detail
        self.status_code = status_code
        super().__init__(detail)


def freeze_user_session(
    *,
    user_id: str,
    name: str,
    description: str = "",
    first_name: str = "",
    last_name: str = "",
    created_by=None,
) -> TestScenario:
    """
    Capture the current state of a user session as a new TestScenario.

    Steps:
        1. Validate inputs (user exists, name is unique).
        2. Build a scenario template from the user's current DB state.
        3. Validate the assembled template.
        4. Persist the TestScenario and instantiate all related objects.

    Args:
        user_id: PK of the user whose session to freeze.
        name: Unique name for the new scenario.
        description: Optional description.
        first_name: Override for the template user's first name.
        last_name: Override for the template user's last name.
        created_by: The admin user who is freezing the session.

    Returns:
        The newly created ``TestScenario`` instance.

    Raises:
        FreezeSessionError: On validation failures (missing user, duplicate
            name, template validation errors).
    """
    if not user_id or not name:
        raise FreezeSessionError("user_id and name are required.")

    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        raise FreezeSessionError("User not found.", status_code=404)

    if TestScenario.objects.filter(name=name).exists():
        raise FreezeSessionError("A scenario with this name already exists.")

    template = build_scenario_template(user, first_name=first_name, last_name=last_name)

    errors = validate_scenario_template(template)
    if errors:
        raise FreezeSessionError(f"Template validation failed: {errors}")

    scenario = TestScenario.objects.create(
        name=name,
        description=description,
        template=template,
        created_by=created_by,
    )
    instantiate_test_scenario(
        scenario,
        create_user=True,
        create_coach_state=True,
        create_identities=True,
        create_chat_messages=True,
        create_user_notes=True,
        create_actions=True,
        create_breaks=True,
    )
    return scenario
