import { TabName } from "../types";
import type { ExpandedSectionsConfig } from "../types";

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

interface TabConfig {
  name: TabName;
  label: string;
}

export const getTabsConfig = (): TabConfig[] => [
  { name: TabName.STATE, label: "Coach State" },
  { name: TabName.PROMPT, label: "Prompt Info" },
  { name: TabName.ACTIONS, label: "Actions" },
  { name: TabName.IDENTITIES, label: "Identities" },
  { name: TabName.CONVERSATION, label: "Conversation" },
];
