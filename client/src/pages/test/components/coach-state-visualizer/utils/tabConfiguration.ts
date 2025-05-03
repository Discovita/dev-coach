import { TabName, ExpandedSectionsConfig } from '../types';

/**
 * Default configuration for expanded sections
 * All sections are expanded by default for better visibility
 */
export const getDefaultExpandedSections = (): ExpandedSectionsConfig => ({
  state: true,
  metadata: true,
  userProfile: true,
  identities: true,
  proposedIdentity: true,
  prompt: true,
  history: true,
  actionHistory: true,
  availableActions: true,
  currentActions: true,
});

/**
 * Tab configuration with labels
 */
interface TabConfig {
  name: TabName;
  label: string;
}

/**
 * Gets the configuration for all tabs
 */
export const getTabsConfig = (): TabConfig[] => [
  { name: TabName.STATE, label: 'State & Metadata' },
  { name: TabName.PROMPT, label: 'Prompt Info' },
  { name: TabName.ACTIONS, label: 'Actions' },
  { name: TabName.IDENTITIES, label: 'Identities' },
  { name: TabName.CONVERSATION, label: 'Conversation' },
];
