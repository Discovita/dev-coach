import {
	adminSaveGeneratedImage,
	continueImageChat,
	generateIdentityImage,
	startImageChat,
} from "@/api/imageGeneration";
import { ImageGenerationError } from "@/types/imageGeneration";
import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("@/utils/authFetch", () => ({
	authFetch: vi.fn(),
}));

vi.mock("@/constants/api", () => ({
	COACH_BASE_URL: "http://localhost:8000/api/v1",
}));

vi.mock("@/lib/logger", () => ({
	createLogger: () => ({
		debug: vi.fn(),
		info: vi.fn(),
		warn: vi.fn(),
		error: vi.fn(),
	}),
	LogLevel: { DEBUG: 0 },
}));

import { authFetch } from "@/utils/authFetch";

describe("generateIdentityImage", () => {
	beforeEach(() => {
		vi.mocked(authFetch).mockReset();
	});

	it("calls the admin generate endpoint", async () => {
		const mockData = { success: true, image_base64: "abc" };
		vi.mocked(authFetch).mockResolvedValue({
			ok: true,
			json: () => Promise.resolve(mockData),
		} as Response);

		const result = await generateIdentityImage({
			identity_id: "id-1",
			user_id: "user-1",
		});
		expect(result).toEqual(mockData);
		expect(authFetch).toHaveBeenCalledWith(
			"http://localhost:8000/api/v1/admin/identities/generate-image",
			expect.objectContaining({ method: "POST" }),
		);
	});

	it("throws on non-ok response", async () => {
		vi.mocked(authFetch).mockResolvedValue({
			ok: false,
			json: () => Promise.resolve({ error: "Generation failed" }),
		} as Response);

		await expect(
			generateIdentityImage({ identity_id: "id-1", user_id: "user-1" }),
		).rejects.toThrow("Generation failed");
	});

	it("uses fallback error message when response is not JSON", async () => {
		vi.mocked(authFetch).mockResolvedValue({
			ok: false,
			json: () => Promise.reject(new Error("Not JSON")),
		} as Response);

		await expect(
			generateIdentityImage({ identity_id: "id-1", user_id: "user-1" }),
		).rejects.toThrow("Failed to generate image");
	});
});

describe("startImageChat", () => {
	beforeEach(() => {
		vi.mocked(authFetch).mockReset();
	});

	it("uses public endpoint when no user_id", async () => {
		const mockData = {
			image_base64: "abc",
			identity_id: "id-1",
			identity_name: "Explorer",
		};
		vi.mocked(authFetch).mockResolvedValue({
			ok: true,
			json: () => Promise.resolve(mockData),
		} as Response);

		await startImageChat({ identity_id: "id-1" });
		expect(authFetch).toHaveBeenCalledWith(
			"http://localhost:8000/api/v1/identity-image-chat/start",
			expect.any(Object),
		);
	});

	it("uses admin endpoint when user_id is provided", async () => {
		const mockData = {
			image_base64: "abc",
			identity_id: "id-1",
			identity_name: "Explorer",
		};
		vi.mocked(authFetch).mockResolvedValue({
			ok: true,
			json: () => Promise.resolve(mockData),
		} as Response);

		await startImageChat({ identity_id: "id-1", user_id: "user-1" });
		expect(authFetch).toHaveBeenCalledWith(
			"http://localhost:8000/api/v1/admin/identity-image-chat/start",
			expect.any(Object),
		);
	});

	it("throws ImageGenerationError on non-ok response", async () => {
		vi.mocked(authFetch).mockResolvedValue({
			ok: false,
			json: () =>
				Promise.resolve({
					error: "Blocked by safety",
					error_code: "SAFETY_BLOCK",
					details: null,
				}),
		} as Response);

		await expect(startImageChat({ identity_id: "id-1" })).rejects.toThrow(
			ImageGenerationError,
		);
	});
});

describe("continueImageChat", () => {
	beforeEach(() => {
		vi.mocked(authFetch).mockReset();
	});

	it("uses public endpoint when no user_id", async () => {
		vi.mocked(authFetch).mockResolvedValue({
			ok: true,
			json: () =>
				Promise.resolve({
					image_base64: "abc",
					identity_id: "id-1",
					identity_name: "X",
				}),
		} as Response);

		await continueImageChat({ edit_prompt: "Make it blue" });
		expect(authFetch).toHaveBeenCalledWith(
			"http://localhost:8000/api/v1/identity-image-chat/continue",
			expect.any(Object),
		);
	});

	it("uses admin endpoint when user_id is provided", async () => {
		vi.mocked(authFetch).mockResolvedValue({
			ok: true,
			json: () =>
				Promise.resolve({
					image_base64: "abc",
					identity_id: "id-1",
					identity_name: "X",
				}),
		} as Response);

		await continueImageChat({ edit_prompt: "Make it blue", user_id: "user-1" });
		expect(authFetch).toHaveBeenCalledWith(
			"http://localhost:8000/api/v1/admin/identity-image-chat/continue",
			expect.any(Object),
		);
	});

	it("throws ImageGenerationError on failure", async () => {
		vi.mocked(authFetch).mockResolvedValue({
			ok: false,
			json: () =>
				Promise.resolve({
					error: "Empty response",
					error_code: "EMPTY_RESPONSE",
					details: null,
				}),
		} as Response);

		await expect(continueImageChat({ edit_prompt: "test" })).rejects.toThrow(
			ImageGenerationError,
		);
	});
});

describe("adminSaveGeneratedImage", () => {
	beforeEach(() => {
		vi.mocked(authFetch).mockReset();
	});

	it("calls the admin save endpoint", async () => {
		const mockData = { success: true, identity: { id: "id-1" } };
		vi.mocked(authFetch).mockResolvedValue({
			ok: true,
			json: () => Promise.resolve(mockData),
		} as Response);

		const result = await adminSaveGeneratedImage({
			identity_id: "id-1",
			image_base64: "data:image/png;base64,abc",
		});
		expect(result).toEqual(mockData);
		expect(authFetch).toHaveBeenCalledWith(
			"http://localhost:8000/api/v1/admin/identities/save-generated-image",
			expect.objectContaining({ method: "POST" }),
		);
	});

	it("throws on non-ok response", async () => {
		vi.mocked(authFetch).mockResolvedValue({
			ok: false,
			json: () => Promise.resolve({ error: "Save failed" }),
		} as Response);

		await expect(
			adminSaveGeneratedImage({ identity_id: "id-1", image_base64: "abc" }),
		).rejects.toThrow("Save failed");
	});
});
