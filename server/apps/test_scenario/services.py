from apps.users.models import User

def instantiate_test_scenario(scenario, create_user=True, create_chat_messages=False, create_identities=False, create_coach_state=False, create_user_notes=False):
    """
    Instantiates a test scenario from its template.
    For now, only handles user creation (incremental step).
    Deletes any existing user(s) for this scenario, then creates a new one.
    """
    template = scenario.template
    created_user = None
    if create_user:
        # Delete any existing user(s) for this scenario
        User.objects.filter(test_scenario=scenario).delete()
        user_data = template.get('user')
        if user_data:
            # Remove password from user_data to set it properly
            password = user_data.pop('password', None)
            user = User(**user_data, test_scenario=scenario)
            if password:
                user.set_password(password)
            user.save()
            created_user = user
    return {'user': created_user}
