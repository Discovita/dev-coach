import { ComponentConfig } from "@/types/componentConfig";

/**
 * Converts a ComponentConfig to display-only by removing interactive buttons.
 * Used for optimistic updates to preserve component UI after user interaction.
 */
export function makeComponentDisplayOnly(config: ComponentConfig | null | undefined): ComponentConfig | null {
  if (!config) return null;
  
  return {
    ...config,
    buttons: undefined, // Remove buttons to make display-only
  };
}
