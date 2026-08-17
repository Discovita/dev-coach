import { deleteUser } from "@/api/adminUsers";
import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("@/utils/authFetch", () => ({
	authFetch: vi.fn(),
}));

vi.mock("@/constants/api", () => ({
	COACH_BASE_URL: "http://localhost:8000/api/v1",
}));

import { authFetch } from "@/utils/authFetch";

const BASE = "http://localhost:8000/api/v1/admin/test-user";

describe("adminUsers API", () => {
	beforeEach(() => vi.mocked(authFetch).mockReset());

	it("deleteUser issues a DELETE to the user's delete endpoint", async () => {
		vi.mocked(authFetch).mockResolvedValue({ ok: true } as Response);

		await deleteUser("u1");

		expect(authFetch).toHaveBeenCalledWith(`${BASE}/u1/delete`, {
			method: "DELETE",
		});
	});

	it("deleteUser surfaces the backend's detail message", async () => {
		vi.mocked(authFetch).mockResolvedValue({
			ok: false,
			json: () =>
				Promise.resolve({ detail: "You cannot delete your own account." }),
		} as Response);

		await expect(deleteUser("u1")).rejects.toThrow(
			"You cannot delete your own account.",
		);
	});

	it("deleteUser falls back to a generic message when there is no body", async () => {
		vi.mocked(authFetch).mockResolvedValue({
			ok: false,
			json: () => Promise.reject(new Error("not json")),
		} as unknown as Response);

		await expect(deleteUser("u1")).rejects.toThrow("Failed to delete user");
	});
});
