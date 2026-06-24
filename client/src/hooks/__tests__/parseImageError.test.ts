import { parseImageError } from "@/hooks/use-image-generation";
import { ImageGenerationError } from "@/types/imageGeneration";
import { describe, expect, it } from "vitest";

describe("parseImageError", () => {
	it("returns null for null input", () => {
		expect(parseImageError(null)).toBeNull();
	});

	it("parses an ImageGenerationError with retryable code", () => {
		const error = new ImageGenerationError({
			error: "Model is overloaded",
			error_code: "MODEL_OVERLOADED",
			details: "Try again later",
		});
		const result = parseImageError(error);

		expect(result).not.toBeNull();
		expect(result?.message).toBe("Model is overloaded");
		expect(result?.errorCode).toBe("MODEL_OVERLOADED");
		expect(result?.details).toBe("Try again later");
		expect(result?.isRetryable).toBe(true);
	});

	it("parses RATE_LIMITED as retryable", () => {
		const error = new ImageGenerationError({
			error: "Rate limited",
			error_code: "RATE_LIMITED",
			details: null,
		});
		expect(parseImageError(error)?.isRetryable).toBe(true);
	});

	it("parses EMPTY_RESPONSE as retryable", () => {
		const error = new ImageGenerationError({
			error: "Empty response",
			error_code: "EMPTY_RESPONSE",
			details: null,
		});
		expect(parseImageError(error)?.isRetryable).toBe(true);
	});

	it("parses BLOCKED_PROMPT as non-retryable", () => {
		const error = new ImageGenerationError({
			error: "Prompt blocked",
			error_code: "BLOCKED_PROMPT",
			details: "Content policy violation",
		});
		const result = parseImageError(error);

		expect(result?.isRetryable).toBe(false);
		expect(result?.errorCode).toBe("BLOCKED_PROMPT");
	});

	it("parses SAFETY_BLOCK as non-retryable", () => {
		const error = new ImageGenerationError({
			error: "Safety blocked",
			error_code: "SAFETY_BLOCK",
			details: null,
		});
		expect(parseImageError(error)?.isRetryable).toBe(false);
	});

	it("parses a generic Error as retryable with UNKNOWN code", () => {
		const error = new Error("Something broke");
		const result = parseImageError(error);

		expect(result).not.toBeNull();
		expect(result?.message).toBe("Something broke");
		expect(result?.errorCode).toBe("UNKNOWN");
		expect(result?.details).toBeNull();
		expect(result?.isRetryable).toBe(true);
	});

	it("provides default message for error without message", () => {
		const error = new Error();
		error.message = "";
		const result = parseImageError(error);

		expect(result?.message).toBe(
			"An unexpected error occurred. Please try again.",
		);
	});
});
