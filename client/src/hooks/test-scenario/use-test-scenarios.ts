import { useQuery } from "@tanstack/react-query";
import { fetchTestScenarios } from "@/api/testScenarios";
import type { TestScenario } from "@/types/testScenario";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { resetTestScenario } from "@/api/testScenarios";

export function useTestScenarios() {
  return useQuery<TestScenario[]>({
    queryKey: ["test-scenarios", "all"],
    queryFn: fetchTestScenarios,
    staleTime: 1000 * 60 * 10,
    retry: false,
  });
}

export function useResetTestScenario() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (scenarioId: string) => resetTestScenario(scenarioId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["test-scenarios", "all"] });
    },
  });
}
