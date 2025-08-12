from apps.coach_states.models import CoachState
from apps.actions.models import Action
from apps.chat_messages.models import ChatMessage
from services.action_handler.models import UpdateAskedQuestionsParams
from enums.action_type import ActionType
from enums.get_to_know_you_questions import GetToKnowYouQuestions
from services.logger import configure_logging

log = configure_logging(__name__, log_level="INFO")

def update_asked_questions(
    coach_state: CoachState, params: UpdateAskedQuestionsParams, coach_message: ChatMessage
) -> None:
    """
    Update the asked_questions attribute of the CoachState.
    This function tracks which questions have been asked during the Get To Know You phase
    to prevent asking the same question twice.
    """
    # Convert enum objects to their string values for storage
    question_values = [question.value for question in params.asked_questions]
    coach_state.asked_questions = question_values
    coach_state.save()
    
    # Log the action with rich context
    Action.objects.create(
        user=coach_state.user,
        action_type=ActionType.UPDATE_ASKED_QUESTIONS.value,
        parameters=params.model_dump(),
        result_summary=f"Updated asked questions list with {len(params.asked_questions)} questions",
        coach_message=coach_message,
        test_scenario=coach_state.user.test_scenario if hasattr(coach_state.user, 'test_scenario') else None
    )
