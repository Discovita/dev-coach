import React from "react";
import { TabName, ExpandedSectionsConfig } from "../types";
import {
  renderJsonSection,
  renderEmptyState,
  renderActionsSection,
  renderFinalPrompt,
  renderCoachStateSection,
  renderIdentitiesSection,
} from "./renderUtils";

import { useCoachState } from "@/hooks/use-coach-state";
import { useFinalPrompt } from "@/hooks/use-final-prompt";
import { useActions } from "@/hooks/use-actions";
import { useIdentities } from "@/hooks/use-identities";
import { useChatMessages } from "@/hooks/use-chat-messages";
import IdentityItem from "./IdentityItem";

/**
 * TabContent component
 * Renders the content for each tab in the CoachStateVisualizer.
 * Fetches all required data using context-aware hooks directly.
 * Only UI state (expandedSections, toggleSection) is passed as props.
 *
 * Works in both regular and impersonating mode — hooks read from
 * UserTargetContext internally to determine data source.
 */
export const TabContent: React.FC<{
  tabName: TabName;
  expandedSections: ExpandedSectionsConfig;
  toggleSection: (section: string) => void;
}> = ({ tabName, expandedSections, toggleSection }) => {
  const { coachState } = useCoachState();
  const finalPrompt = useFinalPrompt();
  const { actions } = useActions();
  const { identities } = useIdentities();
  const { chatMessages } = useChatMessages();

  switch (tabName) {
    case TabName.STATE:
      return (
        <>
          {renderCoachStateSection(
            coachState,
            "state",
            expandedSections["state"],
            toggleSection
          )}
        </>
      );

    case TabName.PROMPT:
      return (
        <>
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
          {actions &&
            actions.length > 0 &&
            renderActionsSection(
              "Actions History",
              actions,
              "actionHistory",
              expandedSections["actionHistory"] ?? true,
              toggleSection
            )}

          {renderJsonSection(
            "Available Actions",
            undefined,
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
          {renderIdentitiesSection(
            "Confirmed Identities",
            identities || [],
            "identities",
            expandedSections["identities"] ?? true,
            toggleSection
          )}

          {coachState?.proposed_identity && (
            <div className="mb-4">
              <h3 className="text-base font-semibold text-gold-800 dark:text-gold-200 mb-3">
                Proposed Identity
              </h3>
              <IdentityItem identity={coachState.proposed_identity} />
            </div>
          )}

          {(!identities || identities.length === 0) &&
            !coachState?.proposed_identity &&
            renderEmptyState(
              "No identities created yet.",
              "Identities will appear here as they are created during the coaching process."
            )}
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
