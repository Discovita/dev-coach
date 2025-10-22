/**
 * Represents the different phases of coaching in the application.
 * This enum is used to track the current coaching phase for a user,
 * for example, in the `CoachState` interface in `client/src/types/coachState.ts`.
 */
export enum CoachingPhase {
  SYSTEM_CONTEXT = "system_context",
  INTRODUCTION = "introduction",
  GET_TO_KNOW_YOU = "get_to_know_you",
  IDENTITY_WARMUP = "identity_warm_up",
  IDENTITY_BRAINSTORMING = "identity_brainstorming",
  IDENTITY_REFINEMENT = "identity_refinement",
  I_AM_STATEMENT = "i_am_statement",
  IDENTITY_VISUALIZATION = "identity_visualization",
}

/**
 * Maps coaching phase values to their human-readable display names
 */
export const COACHING_PHASE_DISPLAY_NAMES: Record<CoachingPhase, string> = {
  [CoachingPhase.SYSTEM_CONTEXT]: "System Context",
  [CoachingPhase.INTRODUCTION]: "Introduction",
  [CoachingPhase.GET_TO_KNOW_YOU]: "Get To Know You",
  [CoachingPhase.IDENTITY_WARMUP]: "Identity Warmup",
  [CoachingPhase.IDENTITY_BRAINSTORMING]: "Identity Brainstorming",
  [CoachingPhase.IDENTITY_REFINEMENT]: "Identity Refinement",
  [CoachingPhase.I_AM_STATEMENT]: "I Am Statement",
  [CoachingPhase.IDENTITY_VISUALIZATION]: "Identity Visualization",
};

/**
 * Maps coaching phase values to their color classes
 */
export const COACHING_PHASE_COLORS: Record<CoachingPhase, string> = {
  [CoachingPhase.SYSTEM_CONTEXT]:
    "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200",
  [CoachingPhase.INTRODUCTION]:
    "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
  [CoachingPhase.GET_TO_KNOW_YOU]:
    "bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200",
  [CoachingPhase.IDENTITY_WARMUP]:
    "bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200",
  [CoachingPhase.IDENTITY_BRAINSTORMING]:
    "bg-pink-100 text-pink-800 dark:bg-pink-900 dark:text-pink-200",
  [CoachingPhase.IDENTITY_REFINEMENT]:
    "bg-indigo-100 text-indigo-800 dark:bg-indigo-900 dark:text-indigo-200",
  [CoachingPhase.I_AM_STATEMENT]:
    "bg-teal-100 text-teal-800 dark:bg-teal-900 dark:text-teal-200",
  [CoachingPhase.IDENTITY_VISUALIZATION]:
    "bg-cyan-100 text-cyan-800 dark:bg-cyan-900 dark:text-cyan-200",
};

/**
 * Helper function to get the display name for a coaching phase
 */
export const getCoachingPhaseDisplayName = (phase: CoachingPhase): string => {
  return COACHING_PHASE_DISPLAY_NAMES[phase] || phase;
};

/**
 * Helper function to get the color classes for a coaching phase
 */
export const getCoachingPhaseColor = (phase: CoachingPhase): string => {
  return (
    COACHING_PHASE_COLORS[phase] ||
    "bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200"
  );
};
