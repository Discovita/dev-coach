---
sidebar_position: 15
---

# Asked Questions

The `asked_questions` context key provides the list of questions that have been asked during the Get To Know You phase.

## Context Key Details

**Key Name**: `asked_questions`  
**Enum Value**: `ContextKey.ASKED_QUESTIONS`  
**Data Source**: CoachState  
**Return Type**: `str`

## What Data It Provides

Returns the human-readable labels of questions that have been asked as a comma-separated string, or a message indicating no questions have been asked yet.

## How It Gets the Data

The function retrieves the `asked_questions` list from the coach state, converts enum values to human-readable labels, and joins them with commas.

## Example Data

```python
# Example return values
"What is your biggest challenge right now?, What would success look like for you?, What are your core values?"  # Multiple questions
"What is your biggest challenge right now?"  # Single question
"No questions have been asked yet..."       # No questions asked
```

## Implementation

```python
def get_asked_questions(coach_state: CoachState) -> str:
    """
    Get the list of questions that have been asked during the Get To Know You phase as a comma-separated string.
    Returns the human-readable labels of the questions.
    """
    asked_questions = coach_state.asked_questions
    if not asked_questions:
        return "No questions have been asked yet..."
    
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
```
