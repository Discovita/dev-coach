import { ComponentConfig } from "./componentConfig";

export interface CoachResponse {
  message: string;
  final_prompt?: string;
  component?: ComponentConfig;
}
