import { useQuery } from "@tanstack/react-query";
import { fetchTestScenarios } from "@/api/testScenarios";
import { TestScenario } from "@/types/testScenario";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { resetTestScenario } from "@/api/testScenarios";

export function useTestScenarios() {
  return useQuery<TestScenario[]>({
    queryKey: ["test-scenarios", "all"],
    queryFn: fetchTestScenarios,
    staleTime: 1000 * 60 * 10, // 10 minutes
    retry: false,
  });
} 

export function useResetTestScenario() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (scenarioId: string) => resetTestScenario(scenarioId),
    onSuccess: () => {
      // Invalidate or refetch relevant queries
      queryClient.invalidateQueries({ queryKey: ["test-scenarios", "all"] });
      // Add more invalidations if needed (e.g., scenario details)
    },
  });
}