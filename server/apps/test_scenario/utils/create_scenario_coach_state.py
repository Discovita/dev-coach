"""
create_scenario_coach_state

Update the auto-created CoachState for a test scenario user with template data.
"""

from apps.coach_states.models import CoachState
from apps.identities.models import Identity
from services.logger import configure_logging

log = configure_logging(__name__)


def create_scenario_coach_state(scenario, template: dict, user, created_identities: dict):
    """
    Apply template ``coach_state`` data to the auto-created CoachState.

    The CoachState is created automatically by a signal when the User is saved.
    This utility fetches that CoachState and populates it from the template.

    Args:
        scenario: The TestScenario instance this coach state belongs to.
        template: The full scenario template dict. Must contain a ``coach_state``
            key.
        user: The User instance whose CoachState to update.
        created_identities: A name → Identity mapping produced by
            ``create_scenario_identities``, used to resolve the
            ``current_identity`` reference.

    Returns:
        The updated CoachState instance.
    """
    coach_state_data = template["coach_state"].copy()
    allowed_fields = {f.name for f in CoachState._meta.get_fields()}

    current_identity_name = coach_state_data.pop("current_identity", None)
    coach_state_data.pop("proposed_identity", None)
    coach_state_data["test_scenario"] = scenario

    coach_state = CoachState.objects.get(user=user)
    for key, value in coach_state_data.items():
        if key in allowed_fields:
            setattr(coach_state, key, value)

    if current_identity_name:
        if current_identity_name in created_identities:
            coach_state.current_identity = created_identities[current_identity_name]
        else:
            try:
                coach_state.current_identity = Identity.objects.get(
                    user=user, test_scenario=scenario, name=current_identity_name
                )
            except Identity.DoesNotExist:
                log.warning(
                    f"Current identity '{current_identity_name}' not found "
                    f"for user {user.id}"
                )

    coach_state.save()
    return coach_state
