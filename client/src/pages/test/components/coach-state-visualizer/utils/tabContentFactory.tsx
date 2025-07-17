import React from "react";
import { TabName, ExpandedSectionsConfig } from "../types";
import {
  renderJsonSection,
  renderEmptyState,
  renderActionsSection,
  renderFinalPrompt,
} from "./renderUtils";
import { getCurrentStateInfo } from "./dataUtils";
import { useCoachState } from "@/hooks/use-coach-state";
import { useFinalPrompt } from "@/hooks/use-final-prompt";
import { useActions } from "@/hooks/use-actions";
import { useIdentities } from "@/hooks/use-identities";
import { useChatMessages } from "@/hooks/use-chat-messages";
import { useTestScenarioUserCoachState } from "@/hooks/test-scenario/use-test-scenario-user-coach-state";
import { useTestScenarioUserFinalPrompt } from "@/hooks/test-scenario/use-test-scenario-user-final-prompt";
import { useTestScenarioUserActions } from "@/hooks/test-scenario/use-test-scenario-user-actions";
import { useTestScenarioUserIdentities } from "@/hooks/test-scenario/use-test-scenario-user-identities";
import { useTestScenarioUserChatMessages } from "@/hooks/test-scenario/use-test-scenario-user-chat-messages";
import { Action } from "@/types/action";

/**
 * TabContent component
 * Renders the content for each tab in the CoachStateVisualizer.
 * Fetches all required data using hooks directly.
 * Only UI state (expandedSections, toggleSection) is passed as props.
 */
export const TabContent: React.FC<{
  tabName: TabName;
  expandedSections: ExpandedSectionsConfig;
  toggleSection: (section: string) => void;
}> = ({ tabName, expandedSections, toggleSection }) => {
  // Fetch all required data using hooks
  const { coachState } = useCoachState();
  const finalPrompt = useFinalPrompt();
  const actions: Action[] = useActions();
  const { identities } = useIdentities();
  const { chatMessages } = useChatMessages();

  switch (tabName) {
    case TabName.STATE:
      return (
        <>
          {renderJsonSection(
            "Current State",
            getCurrentStateInfo(coachState),
            "state",
            expandedSections["state"],
            toggleSection
          )}
        </>
      );

    case TabName.PROMPT:
      return (
        <>
          {/* Render the final prompt using renderFinalPrompt for consistent UI */}
          {finalPrompt &&
            renderFinalPrompt(
              finalPrompt,
              expandedSections["prompt"],
              toggleSection
            )}

          {!finalPrompt &&
            renderEmptyState(
              "No prompt information available yet.",
              "Send a message to see the prompt used to generate a response."
            )}
        </>
      );

    case TabName.ACTIONS:
      return (
        <>
          {/* Render the running list of actions from the cache using the new renderer */}
          {actions &&
            actions.length > 0 &&
            renderActionsSection(
              "Actions History",
              actions,
              "actionHistory",
              expandedSections["actionHistory"] ?? true, // Default to expanded
              toggleSection
            )}

          {/* Available Actions is a string[]; render as JSON, not as actions */}
          {renderJsonSection(
            "Available Actions",
            undefined, // You can fetch available actions from coachState if needed
            "availableActions",
            expandedSections["availableActions"],
            toggleSection
          )}

          {(!actions || actions.length === 0) &&
            renderEmptyState(
              "No action information available yet.",
              "Actions will appear here when the coach performs them or lists available ones."
            )}
        </>
      );

    case TabName.IDENTITIES:
      return (
        <>
          {renderJsonSection(
            "Confirmed Identities",
            identities || [],
            "identities",
            expandedSections["identities"],
            toggleSection
          )}

          {renderJsonSection(
            "Proposed Identity",
            coachState?.proposed_identity
              ? (coachState.proposed_identity as unknown as Record<
                  string,
                  unknown
                >)
              : null,
            "proposedIdentity",
            expandedSections["proposedIdentity"],
            toggleSection
          )}

          {(!identities || identities.length === 0) &&
            !coachState?.proposed_identity &&
            renderEmptyState("No identities created yet.")}
        </>
      );

    case TabName.CONVERSATION:
      return (
        <>
          {renderJsonSection(
            "Conversation History",
            chatMessages || [],
            "history",
            expandedSections["history"],
            toggleSection
          )}

          {(!chatMessages || chatMessages.length === 0) &&
            renderEmptyState("No conversation history available.")}
        </>
      );

    default:
      return <div>Select a tab to view details</div>;
  }
};

/**
 * TestScenarioTabContent component
 * Renders the content for each tab in the TestScenarioCoachStateVisualizer.
 * Fetches all required data using test-scenario hooks directly.
 * Only UI state (expandedSections, toggleSection) is passed as props.
 * Requires a testUserId prop.
 */
export const TestScenarioTabContent: React.FC<{
  tabName: TabName;
  expandedSections: ExpandedSectionsConfig;
  toggleSection: (section: string) => void;
  testUserId: string;
}> = ({ tabName, expandedSections, toggleSection, testUserId }) => {
  // Fetch all required data using test-scenario hooks
  const { coachState } = useTestScenarioUserCoachState(testUserId);
  const finalPrompt = useTestScenarioUserFinalPrompt(testUserId);
  const actions: Action[] = useTestScenarioUserActions(testUserId);
  useTestScenarioUserIdentities(testUserId); // Not used directly, but ensures cache is up to date
  const { chatMessages } = useTestScenarioUserChatMessages(testUserId);

  switch (tabName) {
    case TabName.STATE:
      return (
        <>
          {renderJsonSection(
            "Current State",
            getCurrentStateInfo(coachState),
            "state",
            expandedSections["state"],
            toggleSection
          )}
        </>
      );

    case TabName.PROMPT:
      return (
        <>
          {/* Render the final prompt using renderFinalPrompt for consistent UI */}
          {finalPrompt &&
            renderFinalPrompt(
              finalPrompt,
              expandedSections["prompt"],
              toggleSection
            )}

          {!finalPrompt &&
            renderEmptyState(
              "No prompt information available yet.",
              "Send a message to see the prompt used to generate a response."
            )}
        </>
      );

    case TabName.ACTIONS:
      return (
        <>
          {/* Render the running list of actions from the cache using the new renderer */}
          {actions &&
            actions.length > 0 &&
            renderActionsSection(
              "Actions History",
              actions,
              "actionHistory",
              expandedSections["actionHistory"] ?? true, // Default to expanded
              toggleSection
            )}

          {/* Available Actions is a string[]; render as JSON, not as actions */}
          {renderJsonSection(
            "Available Actions",
            undefined, // You can fetch available actions from coachState if needed
            "availableActions",
            expandedSections["availableActions"],
            toggleSection
          )}

          {(!actions || actions.length === 0) &&
            renderEmptyState(
              "No action information available yet.",
              "Actions will appear here when the coach performs them or lists available ones."
            )}
        </>
      );

    case TabName.IDENTITIES:
      return (
        <>
          {renderJsonSection(
            "Confirmed Identities",
            [], // Not fetched directly, but could be added if needed
            "identities",
            expandedSections["identities"],
            toggleSection
          )}

          {renderJsonSection(
            "Proposed Identity",
            coachState?.proposed_identity
              ? (coachState.proposed_identity as unknown as Record<
                  string,
                  unknown
                >)
              : null,
            "proposedIdentity",
            expandedSections["proposedIdentity"],
            toggleSection
          )}

          {(!coachState?.proposed_identity) &&
            renderEmptyState("No identities created yet.")}
        </>
      );

    case TabName.CONVERSATION:
      return (
        <>
          {renderJsonSection(
            "Conversation History",
            chatMessages || [],
            "history",
            expandedSections["history"],
            toggleSection
          )}

          {(!chatMessages || chatMessages.length === 0) &&
            renderEmptyState("No conversation history available.")}
        </>
      );

    default:
      return <div>Select a tab to view details</div>;
  }
};
