export interface ComponentAction {
  action: string;
  params: Record<string, unknown>;
}

export interface ComponentButton {
  label: string;
  actions: ComponentAction[];
}

export interface ComponentConfig {
  buttons: ComponentButton[];
}
