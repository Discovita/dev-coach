import { describe, it, expect } from "vitest";
import { ImageGenerationError } from "@/types/imageGeneration";

describe("ImageGenerationError", () => {
  it("extends Error", () => {
    const err = new ImageGenerationError({
      error: "Test error",
      error_code: "UNKNOWN",
      details: null,
    });
    expect(err).toBeInstanceOf(Error);
    expect(err).toBeInstanceOf(ImageGenerationError);
  });

  it("sets the correct name", () => {
    const err = new ImageGenerationError({
      error: "Test",
      error_code: "BLOCKED_PROMPT",
      details: null,
    });
    expect(err.name).toBe("ImageGenerationError");
  });

  it("sets message from the response error field", () => {
    const err = new ImageGenerationError({
      error: "Prompt was blocked by safety filters",
      error_code: "BLOCKED_PROMPT",
      details: "Content policy violation",
    });
    expect(err.message).toBe("Prompt was blocked by safety filters");
  });

  it("stores error_code and details", () => {
    const err = new ImageGenerationError({
      error: "Rate limited",
      error_code: "RATE_LIMITED",
      details: "Try again in 60 seconds",
    });
    expect(err.error_code).toBe("RATE_LIMITED");
    expect(err.details).toBe("Try again in 60 seconds");
  });

  it("handles null details", () => {
    const err = new ImageGenerationError({
      error: "Unknown error",
      error_code: "UNKNOWN",
      details: null,
    });
    expect(err.details).toBeNull();
  });
});
