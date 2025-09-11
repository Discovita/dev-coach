export interface ComponentButton {
  label: string;
  action?: string;
  params?: Record<string, unknown>;
}

export interface ComponentConfig {
  buttons: ComponentButton[];
}

export interface CoachResponse {
  message: string;
  final_prompt?: string;
  component?: ComponentConfig;
}
