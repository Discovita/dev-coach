import { useState } from "react";
import { testStates } from "@/tests/testStates";
import TestChat from "@/pages/test/components/TestChat";
import {
  ModuleRegistry,
  ClientSideRowModelModule,
  ValidationModule,
} from "ag-grid-community";
import { useTestScenarios } from "@/hooks/use-test-scenarios";
import { TestScenario } from "@/types/testScenario";
import TestScenarioPageHeader from "./components/TestScenarioPageHeader";
import TestScenarioTable from "./components/TestScenarioTable";
import TestScenarioEditor from "./components/TestScenarioEditor";
import { useMutation } from "@tanstack/react-query";
import { createTestScenario, updateTestScenario } from "@/api/testScenarios";
import { toast } from "sonner";
// If you see a type error for ag-grid-react, ensure @types/ag-grid-react is installed or use a type override.

// Register AG Grid modules
ModuleRegistry.registerModules([ClientSideRowModelModule, ValidationModule]);

function Test() {
  const [selectedState] = useState("");
  const [hasStarted, setHasStarted] = useState(false);
  const { data: scenarios, isLoading, isError, refetch } = useTestScenarios();
  const [editingScenario, setEditingScenario] = useState<TestScenario | null>(
    null
  );
  const [showEditor, setShowEditor] = useState(false);

  // Create mutation
  const createMutation = useMutation({
    mutationFn: createTestScenario,
    onSuccess: () => {
      refetch();
      setShowEditor(false);
      setEditingScenario(null);
      toast.success("Test scenario created successfully!");
    },
    onError: (err) => {
      toast.error("Failed to create test scenario", {
        description: err instanceof Error ? err.message : undefined,
      });
    },
  });

  // Update mutation
  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<TestScenario> }) =>
      updateTestScenario(id, data),
    onSuccess: () => {
      refetch();
      setShowEditor(false);
      setEditingScenario(null);
      toast.success("Test scenario updated successfully!");
    },
    onError: (err) => {
      toast.error("Failed to update test scenario", {
        description: err instanceof Error ? err.message : undefined,
      });
    },
  });

  // Handler for editing a scenario
  const handleEditScenario = (scenario: TestScenario) => {
    setEditingScenario(scenario);
    setShowEditor(true);
  };

  // Handler for creating a new scenario
  const handleCreateScenario = () => {
    setEditingScenario(null);
    setShowEditor(true);
  };

  // Handler for saving a scenario
  const handleSaveScenario = async (fields: {
    name: string;
    description: string;
    user: { first_name: string; last_name: string };
  }) => {
    if (editingScenario) {
      // Update
      await updateMutation.mutateAsync({
        id: editingScenario.id,
        data: {
          ...editingScenario,
          name: fields.name,
          description: fields.description,
          template: {
            ...editingScenario.template,
            user: {
              ...((editingScenario.template as Record<string, unknown>).user ||
                {}),
              ...fields.user,
            },
          },
        },
      });
    } else {
      // Create
      await createMutation.mutateAsync({
        name: fields.name,
        description: fields.description,
        template: {
          user: fields.user,
        },
      });
    }
  };

  // Handler for canceling edit/create
  const handleCancelEdit = () => {
    setShowEditor(false);
    setEditingScenario(null);
  };

  if (hasStarted) {
    return (
      // TODO: Fix the selected state that gets passed in here
      // May have to convert this to read test scenarios directly
      <TestChat
        selectedState={selectedState}
        setHasStarted={setHasStarted}
        testStates={testStates}
      />
    );
  }

  return (
    <div className="_Test flex flex-col items-center w-full h-full p-4">
      <div className="w-full max-w-5xl my-8">
        <TestScenarioPageHeader onCreate={handleCreateScenario} />
        <TestScenarioTable
          scenarios={scenarios}
          isLoading={isLoading}
          isError={isError}
          onEdit={handleEditScenario}
        />
      </div>
      {showEditor && (
        <TestScenarioEditor
          scenario={editingScenario}
          onSave={handleSaveScenario}
          onCancel={handleCancelEdit}
        />
      )}
    </div>
  );
}

export default Test;
