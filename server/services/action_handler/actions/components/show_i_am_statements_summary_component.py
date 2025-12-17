from typing import List
from apps.coach_states.models import CoachState
from apps.chat_messages.models import ChatMessage
from apps.actions.models import Action
from apps.identities.models import Identity
from enums.action_type import ActionType
from enums.identity_state import IdentityState
from services.action_handler.models.params import (
    ShowIAmStatementsSummaryComponentParams,
)
from models.components.ComponentConfig import (
    ComponentConfig,
    ComponentButton,
    ComponentAction,
    ComponentIdentity,
)
from enums.component_type import ComponentType
from services.logger import configure_logging

log = configure_logging(__name__, log_level="DEBUG")


def show_i_am_statements_summary_component(
    coach_state: CoachState,
    params: ShowIAmStatementsSummaryComponentParams,
    coach_message: ChatMessage,
):
    """
    Show the I Am Statements Summary component to the user.

    Displays all completed identities with their "I Am" statements in a
    celebratory summary view. This component is shown at the end of the
    I Am Statement phase before transitioning to visualization.
    """
    log.info(
        f"Showing I Am Statements Summary component for user {coach_state.user.id}"
    )

    # Fetch all identities that have completed their I Am statements
    identities = Identity.objects.filter(
        user=coach_state.user,
        state=IdentityState.I_AM_COMPLETE,
    ).exclude(
        state=IdentityState.ARCHIVED
    ).order_by("created_at")

    component_identities: List[ComponentIdentity] = []
    for identity in identities:
        component_identities.append(
            ComponentIdentity(
                id=str(identity.id),
                name=identity.name,
                category=identity.category,
                i_am_statement=identity.i_am_statement,
            )
        )

    persist_action_params = {
        "coach_message_id": str(coach_message.id),
    }

    buttons = [
        ComponentButton(
            label="Continue",
            actions=[
                ComponentAction(
                    action=ActionType.PERSIST_I_AM_STATEMENTS_SUMMARY_COMPONENT.value,
                    params=persist_action_params,
                ),
            ],
        ),
    ]

    component = ComponentConfig(
        component_type=ComponentType.I_AM_STATEMENTS_SUMMARY.value,
        identities=component_identities if component_identities else None,
        buttons=buttons,
    )

    Action.objects.create(
        user=coach_state.user,
        action_type=ActionType.SHOW_I_AM_STATEMENTS_SUMMARY_COMPONENT.value,
        parameters=params.model_dump(),
        result_summary="Showed I Am Statements Summary component",
        coach_message=coach_message,
        test_scenario=(
            coach_state.user.test_scenario
            if hasattr(coach_state.user, "test_scenario")
            else None
        ),
    )

    log.info("Successfully built I Am Statements Summary component")

    return component
