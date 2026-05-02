import { createContext, useContext } from "react";

/**
 * UserTargetContext
 *
 * Provides subtree-scoped configuration for "who are we acting as?"
 * When no UserTargetProvider wraps the tree, hooks default to the
 * logged-in user's endpoints and query keys (["user", ...]).
 *
 * When wrapped in <UserTargetProvider targetUserId={id} scenarioId={sid}>,
 * hooks automatically switch to admin/test-user endpoints and scoped
 * query keys (["testScenarioUser", userId, ...]).
 *
 * Used by: use-chat-messages, use-coach-state, use-identities, use-actions,
 *          use-final-prompt, ConversationResetter, ChatControls, ChatInterface
 *
 * Ported from: dev-coach/client/src/context/UserTargetContext.ts
 */
export interface UserTargetContextValue {
  /** Whether we are impersonating a test scenario user */
  isImpersonating: boolean;
  /** The ID of the user we're acting as (null = logged-in user) */
  targetUserId: string | null;
  /** The ID of the test scenario (null = no scenario context) */
  scenarioId: string | null;
  /** Query key prefix: ["user"] or ["testScenarioUser", userId] */
  queryKeyPrefix: readonly string[];
}

const defaultValue: UserTargetContextValue = {
  isImpersonating: false,
  targetUserId: null,
  scenarioId: null,
  queryKeyPrefix: ["user"],
};

export const UserTargetContext =
  createContext<UserTargetContextValue>(defaultValue);

/**
 * Hook to consume the UserTargetContext.
 * Safe to call outside a provider — returns default (non-impersonating) value.
 */
export function useUserTarget(): UserTargetContextValue {
  return useContext(UserTargetContext);
}
