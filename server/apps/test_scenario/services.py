from apps.users.models import User
from apps.coach_states.models import CoachState


def instantiate_test_scenario(
    scenario,
    create_user=True,
    create_chat_messages=False,
    create_identities=False,
    create_coach_state=False,
    create_user_notes=False,
):
    """
    Instantiates a test scenario from its template.
    For now, only handles user creation (incremental step).
    Deletes any existing user(s) for this scenario, then creates a new one.
    Now also handles coach state creation if requested.
    """
    template = scenario.template
    created_user = None
    created_coach_state = None
    if create_user:
        # Delete any existing user(s) for this scenario
        User.objects.filter(test_scenario=scenario).delete()
        user_data = template.get("user")
        if user_data:
            # Remove password from user_data to set it properly
            password = user_data.pop("password", None)
            user = User(**user_data, test_scenario=scenario)
            if password:
                user.set_password(password)
            user.save()
            created_user = user

    # Handle coach_state creation
    if create_coach_state and template.get("coach_state") and created_user:
        coach_state_data = template["coach_state"].copy()
        # Remove any fields that are not in the model (defensive, in case template changes)
        allowed_fields = {f.name for f in CoachState._meta.get_fields()}
        # Remove foreign key fields that require objects, not IDs (current_identity, proposed_identity)
        coach_state_data.pop("current_identity", None)
        coach_state_data.pop("proposed_identity", None)
        # Set required fields
        coach_state_data["test_scenario"] = scenario
        # Update the existing CoachState (created automatically by signal upon user creation)
        coach_state = CoachState.objects.get(user=created_user)
        for key, value in coach_state_data.items():
            if key in allowed_fields:
                setattr(coach_state, key, value)
        coach_state.save()
        created_coach_state = coach_state
    return {"user": created_user, "coach_state": created_coach_state}
