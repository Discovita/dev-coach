import { COACH_BASE_URL, TEST_SCENARIOS } from "@/constants/api";
import { TestScenario } from "@/types/testScenario";
import { authFetch } from "@/utils/authFetch";

export async function fetchTestScenarios(): Promise<TestScenario[]> {
  const res = await authFetch(`${COACH_BASE_URL}${TEST_SCENARIOS}`);
  if (!res.ok) throw new Error("Failed to fetch test scenarios");
  return res.json();
}
  