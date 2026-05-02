import { describe, it, expect } from "vitest";
import { makeComponentDisplayOnly } from "@/utils/componentConfig";
import { ComponentType } from "@/enums/componentType";
import type { ComponentConfig } from "@/types/componentConfig";

describe("makeComponentDisplayOnly", () => {
  it("returns null for null input", () => {
    expect(makeComponentDisplayOnly(null)).toBeNull();
  });

  it("returns null for undefined input", () => {
    expect(makeComponentDisplayOnly(undefined)).toBeNull();
  });

  it("removes buttons from a config", () => {
    const config: ComponentConfig = {
      component_type: ComponentType.INTRO_CANNED_RESPONSE,
      buttons: [{ label: "Click me" }],
      texts: [{ text: "Hello", location: "before", source: "coach" }],
    };
    const result = makeComponentDisplayOnly(config);
    expect(result).not.toBeNull();
    expect(result!.buttons).toBeUndefined();
    expect(result!.texts).toEqual(config.texts);
    expect(result!.component_type).toBe(ComponentType.INTRO_CANNED_RESPONSE);
  });

  it("preserves config without buttons", () => {
    const config: ComponentConfig = {
      component_type: ComponentType.SUGGEST_I_AM_STATEMENT,
      identities: [{ id: "1", name: "Explorer", category: "passions_and_talents" }],
    };
    const result = makeComponentDisplayOnly(config);
    expect(result).not.toBeNull();
    expect(result!.identities).toEqual(config.identities);
  });

  it("does not mutate the original config", () => {
    const config: ComponentConfig = {
      component_type: ComponentType.INTRO_CANNED_RESPONSE,
      buttons: [{ label: "Click me" }],
    };
    makeComponentDisplayOnly(config);
    expect(config.buttons).toBeDefined();
    expect(config.buttons).toHaveLength(1);
  });
});
