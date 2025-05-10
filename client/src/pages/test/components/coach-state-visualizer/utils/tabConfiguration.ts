import { TabName, ExpandedSectionsConfig } from "../types";

/**
 * Default configuration for expanded sections
 * All sections are expanded by default for better visibility.
 * 'userProfile' removed as it is not used in the new model.
 * Ensure all keys match the actual sections rendered in the visualizer.
 */
export const getDefaultExpandedSections = (): ExpandedSectionsConfig => ({
  state: true,
  metadata: true,
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
  { name: TabName.STATE, label: "Coach State" },
  { name: TabName.PROMPT, label: "Prompt Info" },
  { name: TabName.ACTIONS, label: "Actions" },
  { name: TabName.IDENTITIES, label: "Identities" },
  { name: TabName.CONVERSATION, label: "Conversation" },
];
