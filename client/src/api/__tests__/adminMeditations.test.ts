import {
	createMeditationForUser,
	fetchMeditations,
	generatePart,
	setActiveAsset,
	updateSegment,
} from "@/api/adminMeditations";
import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("@/utils/authFetch", () => ({
	authFetch: vi.fn(),
}));

vi.mock("@/constants/api", () => ({
	COACH_BASE_URL: "http://localhost:8000/api/v1",
}));

import { authFetch } from "@/utils/authFetch";

const BASE = "http://localhost:8000/api/v1/admin/meditations";

function ok(data: unknown) {
	return { ok: true, json: () => Promise.resolve(data) } as Response;
}

describe("adminMeditations API", () => {
	beforeEach(() => vi.mocked(authFetch).mockReset());

	it("fetchMeditations appends the status filter", async () => {
		vi.mocked(authFetch).mockResolvedValue(ok([]));
		await fetchMeditations("COMPLETE");
		expect(authFetch).toHaveBeenCalledWith(`${BASE}?status=COMPLETE`);
	});

	it("fetchMeditations omits the query when no status", async () => {
		vi.mocked(authFetch).mockResolvedValue(ok([]));
		await fetchMeditations();
		expect(authFetch).toHaveBeenCalledWith(BASE);
	});

	it("createMeditationForUser posts the user_id", async () => {
		vi.mocked(authFetch).mockResolvedValue(ok({ id: "m1" }));
		await createMeditationForUser("u1");
		expect(authFetch).toHaveBeenCalledWith(
			`${BASE}/create-for-user`,
			expect.objectContaining({
				method: "POST",
				body: JSON.stringify({ user_id: "u1" }),
			}),
		);
	});

	it("generatePart posts segment_id + kind", async () => {
		vi.mocked(authFetch).mockResolvedValue(ok({}));
		await generatePart("s1", "VIDEO");
		expect(authFetch).toHaveBeenCalledWith(
			`${BASE}/generate-part`,
			expect.objectContaining({
				method: "POST",
				body: JSON.stringify({ segment_id: "s1", kind: "VIDEO" }),
			}),
		);
	});

	it("setActiveAsset posts asset_id", async () => {
		vi.mocked(authFetch).mockResolvedValue(ok({ id: "m1" }));
		await setActiveAsset("a1");
		expect(authFetch).toHaveBeenCalledWith(
			`${BASE}/set-active`,
			expect.objectContaining({
				method: "POST",
				body: JSON.stringify({ asset_id: "a1" }),
			}),
		);
	});

	it("updateSegment patches the given fields", async () => {
		vi.mocked(authFetch).mockResolvedValue(ok({ id: "m1" }));
		await updateSegment("s1", { video_prompt: "new" });
		expect(authFetch).toHaveBeenCalledWith(
			`${BASE}/update-segment`,
			expect.objectContaining({
				method: "PATCH",
				body: JSON.stringify({ segment_id: "s1", video_prompt: "new" }),
			}),
		);
	});

	it("throws on a non-ok response", async () => {
		vi.mocked(authFetch).mockResolvedValue({ ok: false } as Response);
		await expect(fetchMeditations()).rejects.toThrow();
	});
});
