import { COACH_BASE_URL, TEST_SCENARIOS } from "@/constants/api";
import type { TestScenario } from "@/types/testScenario";
import type { TestScenarioTemplate } from "@/types/testScenario";
import { authFetch } from "@/utils/authFetch";

export async function fetchTestScenarios(): Promise<TestScenario[]> {
	const res = await authFetch(`${COACH_BASE_URL}${TEST_SCENARIOS}`);
	if (!res.ok) throw new Error("Failed to fetch test scenarios");
	return res.json();
}

export async function createTestScenario(
	data: Partial<TestScenario> | FormData,
): Promise<TestScenario> {
	if (data instanceof FormData) {
		const res = await authFetch(`${COACH_BASE_URL}${TEST_SCENARIOS}`, {
			method: "POST",
			body: data,
		});
		if (!res.ok) throw new Error("Failed to create test scenario");
		return res.json();
	}

	const template =
		typeof data.template === "object" && data.template !== null
			? data.template
			: {};
	const user =
		typeof (template as Partial<TestScenarioTemplate>).user === "object" &&
		(template as Partial<TestScenarioTemplate>).user !== null
			? (template as Partial<TestScenarioTemplate>).user
			: {};
	const payload = {
		...data,
		template: {
			...template,
			user: { ...user },
		},
	};
	const res = await authFetch(`${COACH_BASE_URL}${TEST_SCENARIOS}`, {
		method: "POST",
		body: JSON.stringify(payload),
	});
	if (!res.ok) throw new Error("Failed to create test scenario");
	return res.json();
}

export async function updateTestScenario(
	id: string,
	data: Partial<TestScenario> | FormData,
): Promise<TestScenario> {
	if (data instanceof FormData) {
		const res = await authFetch(`${COACH_BASE_URL}${TEST_SCENARIOS}/${id}`, {
			method: "PUT",
			body: data,
		});
		if (!res.ok) throw new Error("Failed to update test scenario");
		return res.json();
	}

	const template =
		typeof data.template === "object" && data.template !== null
			? data.template
			: {};
	const t = template as Partial<TestScenarioTemplate>;
	const user = typeof t.user === "object" && t.user !== null ? t.user : {};
	const payload = {
		...data,
		template: {
			...template,
			user: { ...user },
		},
	};
	const res = await authFetch(`${COACH_BASE_URL}${TEST_SCENARIOS}/${id}`, {
		method: "PUT",
		body: JSON.stringify(payload),
	});
	if (!res.ok) throw new Error("Failed to update test scenario");
	return res.json();
}

/**
 * Reset a test scenario to its template state.
 * Calls /api/v1/test-scenarios/{id}/reset (POST)
 * Returns the backend response (should indicate success or error).
 */
export async function resetTestScenario(
	id: string,
): Promise<{ success: boolean; message?: string }> {
	const res = await authFetch(
		`${COACH_BASE_URL}${TEST_SCENARIOS}/${id}/reset`,
		{
			method: "POST",
		},
	);
	if (!res.ok) throw new Error("Failed to reset test scenario");
	return res.json();
}

export async function deleteTestScenario(
	id: string,
): Promise<{ success: boolean; message?: string }> {
	const res = await authFetch(`${COACH_BASE_URL}${TEST_SCENARIOS}/${id}`, {
		method: "DELETE",
	});
	if (!res.ok) throw new Error("Failed to delete test scenario");
	return res.json();
}
