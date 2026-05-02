import type { CoachResponse } from "@/types/coachResponse";
import type { CoachState } from "@/types/coachState";
import type { Action } from "@/types/action";

export interface CoachStateVisualizerProps {
  coachState: CoachState;
  lastResponse?: CoachResponse;
}

export interface ExtractedActions {
  availableActions?: string[];
  actionsTaken?: Action[];
}

export enum TabName {
  STATE = "state",
  PROMPT = "prompt",
  ACTIONS = "actions",
  IDENTITIES = "identities",
  CONVERSATION = "conversation",
}

export interface ExpandedSectionsConfig {
  [key: string]: boolean;
}

export type TabUpdateStatus = {
  [key in TabName]?: boolean;
};

export interface TabConfig {
  name: TabName;
  label: string;
}
