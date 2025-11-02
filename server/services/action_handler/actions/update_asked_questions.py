from apps.coach_states.models import CoachState
from apps.actions.models import Action
from apps.chat_messages.models import ChatMessage
from services.action_handler.models import UpdateAskedQuestionsParams
from enums.action_type import ActionType
from services.logger import configure_logging

log = configure_logging(__name__, log_level="INFO")


def update_asked_questions(
    coach_state: CoachState,
    params: UpdateAskedQuestionsParams,
    coach_message: ChatMessage,
) -> None:
    """
    Update the asked_questions attribute of the CoachState.
    This function tracks which questions have been asked during the Get To Know You phase
    to prevent asking the same question twice.
    Appends a single question to the existing list if it's not already present.
    """
    # Convert enum to its string value for storage
    question_value = params.asked_question.value

    # Get existing questions as a set for efficient lookup
    existing_questions = set(coach_state.asked_questions or [])

    # Only update if the question is not already in the list
    if question_value not in existing_questions:
        # Append the new question to the existing list
        updated_questions = list(existing_questions) + [question_value]
        coach_state.asked_questions = updated_questions
        coach_state.save()

        # Log the action with rich context
        Action.objects.create(
            user=coach_state.user,
            action_type=ActionType.UPDATE_ASKED_QUESTIONS.value,
            parameters=params.model_dump(),
            result_summary=f"Added question '{question_value}' to asked questions list",
            coach_message=coach_message,
            test_scenario=(
                coach_state.user.test_scenario
                if hasattr(coach_state.user, "test_scenario")
                else None
            ),
        )
        log.debug(f"Added question '{question_value}' to asked questions list")
    else:
        log.debug(
            f"Question '{question_value}' already in asked questions list, skipping update (idempotency protection)"
        )
