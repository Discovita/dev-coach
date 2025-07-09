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
import { createTestScenario, updateTestScenario, resetTestScenario, deleteTestScenario } from "@/api/testScenarios";
import { toast } from "sonner";
import { DeleteTestScenarioDialog } from "./components/DeleteTestScenarioDialog";
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
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [scenarioToDelete, setScenarioToDelete] = useState<TestScenario | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  // Create mutation
  const createMutation = useMutation({
    mutationFn: createTestScenario,
    // Remove toast logic from here
    onSuccess: () => {
      refetch();
      setShowEditor(false);
      setEditingScenario(null);
    },
    onError: () => {},
  });

  // Update mutation
  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<TestScenario> }) =>
      updateTestScenario(id, data),
    // Remove toast logic from here
    onSuccess: () => {
      refetch();
      setShowEditor(false);
      setEditingScenario(null);
    },
    onError: () => {},
  });

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: (id: string) => deleteTestScenario(id),
    onSuccess: () => {
      toast.success("Test scenario deleted successfully!");
      refetch();
    },
    onError: (err) => {
      toast.error("Failed to delete test scenario", {
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
      const toastId = toast.loading("Updating scenario...");
      try {
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
        toast.success("Scenario updated. Resetting data...", { id: toastId });
        await resetTestScenario(editingScenario.id);
        toast.success("Scenario data reset successfully!", { id: toastId });
        refetch();
        setShowEditor(false);
        setEditingScenario(null);
      } catch (err) {
        toast.error("Failed to update or reset scenario", {
          id: toastId,
          description: err instanceof Error ? err.message : undefined,
        });
      }
    } else {
      // Create
      const toastId = toast.loading("Creating scenario...");
      try {
        await createMutation.mutateAsync({
          name: fields.name,
          description: fields.description,
          template: {
            user: fields.user,
          },
        });
        toast.success("Test scenario created successfully!", { id: toastId });
        refetch();
        setShowEditor(false);
        setEditingScenario(null);
      } catch (err) {
        toast.error("Failed to create test scenario", {
          id: toastId,
          description: err instanceof Error ? err.message : undefined,
        });
      }
    }
  };

  // Handler for deleting a scenario (open dialog)
  const handleDeleteScenario = (scenario: TestScenario) => {
    setScenarioToDelete(scenario);
    setDeleteDialogOpen(true);
  };

  // Handler for confirming deletion
  const handleConfirmDelete = () => {
    if (!scenarioToDelete) return;
    setIsDeleting(true);
    const toastId = toast.loading("Deleting scenario...");
    deleteMutation.mutate(scenarioToDelete.id, {
      onSuccess: () => {
        toast.success("Test scenario deleted successfully!", { id: toastId });
        setDeleteDialogOpen(false);
        setScenarioToDelete(null);
        setShowEditor(false); // Close the editor if open
        setEditingScenario(null); // Clear editing scenario
      },
      onError: (err) => {
        toast.error("Failed to delete test scenario", { id: toastId, description: err instanceof Error ? err.message : undefined });
      },
      onSettled: () => {
        setIsDeleting(false);
      },
    });
  };

  // Handler for canceling delete
  const handleCancelDelete = () => {
    setDeleteDialogOpen(false);
    setScenarioToDelete(null);
    setIsDeleting(false);
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
          onDelete={handleDeleteScenario}
        />
        <DeleteTestScenarioDialog
          isOpen={deleteDialogOpen}
          onClose={handleCancelDelete}
          onConfirm={handleConfirmDelete}
          scenario={scenarioToDelete}
          isDeleting={isDeleting}
        />
      </div>
      {showEditor && (
        <TestScenarioEditor
          scenario={editingScenario}
          onSave={handleSaveScenario}
          onCancel={handleCancelEdit}
          onDelete={editingScenario ? () => handleDeleteScenario(editingScenario) : undefined}
        />
      )}
    </div>
  );
}

export default Test;
