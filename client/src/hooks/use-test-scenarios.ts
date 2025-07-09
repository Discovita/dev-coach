import { useQuery } from "@tanstack/react-query";
import { fetchTestScenarios } from "@/api/testScenarios";
import { TestScenario } from "@/types/testScenario";

export function useTestScenarios() {
  return useQuery<TestScenario[]>({
    queryKey: ["test-scenarios", "all"],
    queryFn: fetchTestScenarios,
    staleTime: 1000 * 60 * 10, // 10 minutes
    retry: false,
  });
} 