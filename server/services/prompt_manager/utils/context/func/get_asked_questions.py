from apps.coach_states.models import CoachState
from enums.get_to_know_you_questions import GetToKnowYouQuestions


def get_asked_questions(coach_state: CoachState) -> str:
    """
    Get the list of questions that have been asked during the Get To Know You phase as a comma-separated string.
    Returns the human-readable labels of the questions.
    """
    asked_questions = coach_state.asked_questions
    if not asked_questions:
        return "No questions have been asked yet in the Get To Know You phase."
    
    # Convert enum values to human-readable labels
    question_labels = []
    for question_value in asked_questions:
        try:
            question_enum = GetToKnowYouQuestions(question_value)
            question_labels.append(question_enum.label)
        except ValueError:
            # Fallback to the raw value if it's not a valid enum
            question_labels.append(question_value)
    
    return ", ".join(question_labels)
