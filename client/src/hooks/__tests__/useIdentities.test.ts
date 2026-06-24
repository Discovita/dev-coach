import { useIdentities } from "@/hooks/use-identities";
import { createQueryWrapper } from "@/tests/query-wrapper";
import { renderHook, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("@/api/user", () => ({
	fetchIdentities: vi.fn(),
}));

vi.mock("@/api/testScenarioUser", () => ({
	fetchTestScenarioUserIdentities: vi.fn(),
}));

vi.mock("@/context/UserTargetContext", () => ({
	useUserTarget: vi.fn().mockReturnValue({
		isImpersonating: false,
		targetUserId: null,
		scenarioId: null,
		queryKeyPrefix: ["user"],
	}),
}));

import { fetchTestScenarioUserIdentities } from "@/api/testScenarioUser";
import { fetchIdentities } from "@/api/user";
import { useUserTarget } from "@/context/UserTargetContext";

describe("useIdentities", () => {
	beforeEach(() => {
		vi.mocked(fetchIdentities).mockReset();
		vi.mocked(fetchTestScenarioUserIdentities).mockReset();
		vi.mocked(useUserTarget).mockReturnValue({
			isImpersonating: false,
			targetUserId: null,
			scenarioId: null,
			queryKeyPrefix: ["user"],
		});
	});

	it("fetches identities for the logged-in user", async () => {
		const mockIdentities = [
			{ id: "1", name: "Explorer", category: "passions_and_talents" },
		];
		vi.mocked(fetchIdentities).mockResolvedValue(mockIdentities);
		const { wrapper } = createQueryWrapper();

		const { result } = renderHook(() => useIdentities(), { wrapper });

		await waitFor(() => {
			expect(result.current.isLoading).toBe(false);
		});

		expect(result.current.identities).toEqual(mockIdentities);
		expect(fetchIdentities).toHaveBeenCalledTimes(1);
	});

	it("fetches from admin endpoint when impersonating", async () => {
		vi.mocked(useUserTarget).mockReturnValue({
			isImpersonating: true,
			targetUserId: "target-user-1",
			scenarioId: "scenario-1",
			queryKeyPrefix: ["testScenarioUser", "target-user-1"],
		});
		const mockIdentities = [{ id: "2", name: "Creator" }];
		vi.mocked(fetchTestScenarioUserIdentities).mockResolvedValue(
			mockIdentities,
		);
		const { wrapper } = createQueryWrapper();

		const { result } = renderHook(() => useIdentities(), { wrapper });

		await waitFor(() => {
			expect(result.current.isLoading).toBe(false);
		});

		expect(result.current.identities).toEqual(mockIdentities);
		expect(fetchTestScenarioUserIdentities).toHaveBeenCalledWith(
			"target-user-1",
		);
		expect(fetchIdentities).not.toHaveBeenCalled();
	});

	it("handles fetch errors", async () => {
		vi.mocked(fetchIdentities).mockRejectedValue(new Error("Network error"));
		const { wrapper } = createQueryWrapper();

		const { result } = renderHook(() => useIdentities(), { wrapper });

		await waitFor(() => {
			expect(result.current.isError).toBe(true);
		});

		expect(result.current.identities).toBeUndefined();
	});

	it("is disabled when impersonating with no targetUserId", async () => {
		vi.mocked(useUserTarget).mockReturnValue({
			isImpersonating: true,
			targetUserId: null,
			scenarioId: null,
			queryKeyPrefix: ["testScenarioUser"],
		});
		const { wrapper } = createQueryWrapper();

		const { result } = renderHook(() => useIdentities(), { wrapper });

		expect(result.current.isLoading).toBe(false);
		expect(fetchIdentities).not.toHaveBeenCalled();
		expect(fetchTestScenarioUserIdentities).not.toHaveBeenCalled();
	});
});
