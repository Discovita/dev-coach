from apps.coach_states.models import CoachState


def get_asked_questions(coach_state: CoachState) -> str:
    """
    Get the list of questions that have been asked during the Get To Know You phase as a comma-separated string.
    """
    asked_questions = coach_state.asked_questions
    if not asked_questions:
        return "No questions have been asked yet in the Get To Know You phase."
    return ", ".join(asked_questions)
