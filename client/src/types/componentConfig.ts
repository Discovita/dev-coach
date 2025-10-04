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
}

export interface ComponentConfig {
  texts?: ComponentText[];
  buttons?: ComponentButton[];
  identities?: ComponentIdentity[];
}
