import { CoachResponse, CoachState } from '@/types/apiTypes';
import { TabName, ExpandedSectionsConfig, ExtractedActions } from '../types';
import {
  renderJsonSection,
  renderFinalPrompt,
  renderEmptyState,
  renderActionsSection,
} from './renderUtils';
import { getCurrentStateInfo } from './dataUtils';

export const renderTabContent = (
  tabName: TabName,
  coachState: CoachState,
  lastResponse: CoachResponse | undefined,
  expandedSections: ExpandedSectionsConfig,
  toggleSection: (section: string) => void,
  extractedActions: ExtractedActions
): JSX.Element => {
  const { availableActions, actionsTaken } = extractedActions;

  // Filter actions for history - exclude current response actions
  const currentResponseActions = lastResponse?.actions || [];
  const currentResponseActionStrings = currentResponseActions.map(a => JSON.stringify(a));

  // Only show actions in history that aren't in the current response
  const actionHistory = (actionsTaken || []).filter(
    action => !currentResponseActionStrings.includes(JSON.stringify(action))
  );

  switch (tabName) {
    case TabName.STATE:
      return (
        <>
          {renderJsonSection(
            'Current State',
            getCurrentStateInfo(coachState),
            'state',
            expandedSections['state'],
            toggleSection
          )}

          {renderJsonSection(
            'User Profile',
            coachState.user_profile,
            'userProfile',
            expandedSections['userProfile'],
            toggleSection
          )}

          {renderJsonSection(
            'Metadata',
            coachState.metadata,
            'metadata',
            expandedSections['metadata'],
            toggleSection
          )}
        </>
      );

    case TabName.PROMPT:
      return (
        <>
          {renderFinalPrompt(lastResponse, expandedSections['prompt'], toggleSection)}

          {!lastResponse?.final_prompt &&
            renderEmptyState(
              'No prompt information available yet.',
              'Send a message to see the prompt used to generate a response.'
            )}
        </>
      );

    case TabName.ACTIONS:
      return (
        <>
          {lastResponse?.actions &&
            lastResponse.actions.length > 0 &&
            renderActionsSection(
              'Current Response Actions',
              lastResponse.actions,
              'currentActions',
              expandedSections['currentActions'] ?? true, // Default to expanded
              toggleSection
            )}

          {actionHistory &&
            actionHistory.length > 0 &&
            renderActionsSection(
              'Action History',
              actionHistory,
              'actionHistory',
              expandedSections['actionHistory'] ?? true, // Default to expanded
              toggleSection
            )}

          {renderJsonSection(
            'Available Actions',
            availableActions,
            'availableActions',
            expandedSections['availableActions'],
            toggleSection
          )}

          {(!actionHistory || actionHistory.length === 0) &&
            (!availableActions || availableActions.length === 0) &&
            (!lastResponse?.actions || lastResponse.actions.length === 0) &&
            renderEmptyState(
              'No action information available yet.',
              'Actions will appear here when the coach performs them or lists available ones.'
            )}
        </>
      );

    case TabName.IDENTITIES:
      return (
        <>
          {renderJsonSection(
            'Confirmed Identities',
            coachState.identities,
            'identities',
            expandedSections['identities'],
            toggleSection
          )}

          {renderJsonSection(
            'Proposed Identity',
            coachState.proposed_identity,
            'proposedIdentity',
            expandedSections['proposedIdentity'],
            toggleSection
          )}

          {(!coachState.identities || coachState.identities.length === 0) &&
            !coachState.proposed_identity &&
            renderEmptyState('No identities created yet.')}
        </>
      );

    case TabName.CONVERSATION:
      return (
        <>
          {renderJsonSection(
            'Conversation History',
            coachState.conversation_history,
            'history',
            expandedSections['history'],
            toggleSection
          )}

          {(!coachState.conversation_history || coachState.conversation_history.length === 0) &&
            renderEmptyState('No conversation history available.')}
        </>
      );

    default:
      return <div>Select a tab to view details</div>;
  }
};
