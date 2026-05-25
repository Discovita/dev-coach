import { ComponentType } from "@/enums/componentType";

export interface ComponentAction {
  action: string;
  params: Record<string, unknown>;
}

export interface ComponentButton {
  label: string;
  actions?: ComponentAction[];
}

export interface ComponentText {
  text: string; // markdown
  location: "before" | "after";
  source: string;
}

export interface ComponentIdentity {
  id: string;
  name: string;
  category: string;
  i_am_statement?: string;
}

export interface ComponentConfig {
  component_type: ComponentType;
  texts?: ComponentText[];
  buttons?: ComponentButton[];
  identities?: ComponentIdentity[];
  /**
   * Coaching Phase Videos (PR 12 / PR 20): for SESSION_VIDEO components,
   * the registry key identifying which video the card represents (e.g.
   * `welcome_session_intro`). Set server-side at construction; never
   * editable from the FE. Used by the unacked-video composer-disable
   * rule (PR 18: `!shownVideos.includes(component.video_key)`).
   */
  video_key?: string;
  /**
   * Coaching Phase Videos (PR 20): human-readable display name embedded
   * by the server from `SESSION_VIDEOS`. Rendered as the card title.
   */
  video_name?: string;
  /**
   * Coaching Phase Videos (PR 20): full HTTPS URL the modal `<video>`
   * element streams from. Resolved server-side from the env's S3 bucket
   * + the registry's `s3_key`, then persisted on the ChatMessage row so
   * a refresh replays the same URL.
   */
  video_url?: string;
}
