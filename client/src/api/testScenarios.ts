import { COACH_BASE_URL, TEST_SCENARIOS } from "@/constants/api";
import { TestScenario } from "@/types/testScenario";
import { authFetch } from "@/utils/authFetch";
import {
  FIXED_TEST_USER_EMAIL,
  FIXED_TEST_USER_PASSWORD,
} from "@/constants/api";
export async function fetchTestScenarios(): Promise<TestScenario[]> {
  const res = await authFetch(`${COACH_BASE_URL}${TEST_SCENARIOS}`);
  if (!res.ok) throw new Error("Failed to fetch test scenarios");
  return res.json();
}

export async function createTestScenario(
  data: Partial<TestScenario>
): Promise<TestScenario> {
  const template =
    typeof data.template === "object" && data.template !== null
      ? data.template
      : {};
  const user =
    typeof template.user === "object" && template.user !== null
      ? template.user
      : {};
  const payload = {
    ...data,
    template: {
      ...template,
      user: {
        ...user,
        email: FIXED_TEST_USER_EMAIL,
        password: FIXED_TEST_USER_PASSWORD,
      },
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
  data: Partial<TestScenario>
): Promise<TestScenario> {
  const template =
    typeof data.template === "object" && data.template !== null
      ? data.template
      : {};
  const user =
    typeof template.user === "object" && template.user !== null
      ? template.user
      : {};
  const payload = {
    ...data,
    template: {
      ...template,
      user: {
        ...user,
        email: FIXED_TEST_USER_EMAIL,
        password: FIXED_TEST_USER_PASSWORD,
      },
    },
  };
  const res = await authFetch(`${COACH_BASE_URL}${TEST_SCENARIOS}/${id}`, {
    method: "PUT",
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error("Failed to update test scenario");
  return res.json();
}
