/**
 * Enum for the possible questions that can be asked during the Get To Know You phase.
 */
export enum GetToKnowYouQuestions {
  BACKGROUND_UPBRINGING = "background_upbringing",
  FAMILY_STRUCTURE = "family_structure",
  WORK_LIVING = "work_living",
  HOBBIES_INTERESTS = "hobbies_interests",
  WHY_HERE_HOPES = "why_here_hopes",
}

/**
 * Get the display name for a Get To Know You question.
 */
export function getGetToKnowYouQuestionDisplayName(question: GetToKnowYouQuestions): string {
  const displayNames: Record<GetToKnowYouQuestions, string> = {
    [GetToKnowYouQuestions.BACKGROUND_UPBRINGING]: "Background/upbringing",
    [GetToKnowYouQuestions.FAMILY_STRUCTURE]: "Family structure",
    [GetToKnowYouQuestions.WORK_LIVING]: "Work or what they do for a living",
    [GetToKnowYouQuestions.HOBBIES_INTERESTS]: "Hobbies or interests",
    [GetToKnowYouQuestions.WHY_HERE_HOPES]: "Why are you here?",
  };
  
  return displayNames[question];
}
