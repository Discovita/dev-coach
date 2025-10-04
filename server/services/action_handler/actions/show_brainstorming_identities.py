from apps.coach_states.models import CoachState
from apps.chat_messages.models import ChatMessage
from apps.actions.models import Action
from apps.identities.models import Identity
from enums.action_type import ActionType
from services.action_handler.models.params import (
    ShowBrainstormingIdentitiesParams,
)
from models.components.ComponentConfig import ComponentConfig, ComponentIdentity
from services.logger import configure_logging

log = configure_logging(__name__, log_level="DEBUG")


def show_brainstorming_identities(
    coach_state: CoachState,
    params: ShowBrainstormingIdentitiesParams,
    coach_message: ChatMessage,
):
    """
    Show a brainstorming identities component that displays all of the user's current identities.
    
    This builds a ComponentConfig with identity data sourced from the user's
    identities to provide context during brainstorming sessions.
    """

    if not params.enabled:
        log.info(
            "Brainstorming identities component disabled by params; returning empty config"
        )
        return ComponentConfig(buttons=[])

    log.info(f"Building brainstorming identities for user {coach_state.user.id}")

    # Get all identities for the user
    identities = Identity.objects.filter(user=coach_state.user).order_by('category', 'name')
    
    if not identities.exists():
        log.info("No identities found for user, returning empty config")
        return ComponentConfig(buttons=[])

    # Convert identities to ComponentIdentity objects
    component_identities = []
    for identity in identities:
        component_identity = ComponentIdentity(
            id=str(identity.id),
            name=identity.name,
            category=identity.category
        )
        component_identities.append(component_identity)

    component = ComponentConfig(
        identities=component_identities,
        buttons=[],
    )

    # Log the action
    Action.objects.create(
        user=coach_state.user,
        action_type=ActionType.SHOW_BRAINSTORMING_IDENTITIES.value,
        parameters=params.model_dump(),
        result_summary=f"Showed brainstorming identities component",
        coach_message=coach_message,
        test_scenario=(
            coach_state.user.test_scenario
            if hasattr(coach_state.user, "test_scenario")
            else None
        ),
    )

    log.info(f"Successfully built brainstorming identities component with {len(component_identities)} identities")

    return component
