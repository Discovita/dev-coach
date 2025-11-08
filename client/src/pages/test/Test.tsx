import { useState, useEffect } from "react";
import TestChat from "@/pages/test/components/TestChat";
import {
  ModuleRegistry,
  ClientSideRowModelModule,
  ValidationModule,
} from "ag-grid-community";
import { useTestScenarios } from "@/hooks/test-scenario/use-test-scenarios";
import { TestScenario } from "@/types/testScenario";
import TestScenarioPageHeader from "@/pages/test/components/TestScenarioPageHeader";
import TestScenarioTable from "@/pages/test/components/TestScenarioTable";
import TestScenarioEditor from "@/pages/test/components/TestScenarioEditor";
import { useMutation } from "@tanstack/react-query";
import {
  createTestScenario,
  updateTestScenario,
  resetTestScenario,
  deleteTestScenario,
} from "@/api/testScenarios";
import { toast } from "sonner";
import { DeleteTestScenarioDialog } from "@/pages/test/components/DeleteTestScenarioDialog";
import { Button } from "@/components/ui/button";

// Register AG Grid modules
ModuleRegistry.registerModules([ClientSideRowModelModule, ValidationModule]);

function Test() {
  const [selectedScenario, setSelectedScenario] = useState<TestScenario | null>(
    null
  );
  const [isResumingOwnSession, setIsResumingOwnSession] = useState(false);
  const { data: scenarios, isLoading, isError, refetch } = useTestScenarios();
  const [editingScenario, setEditingScenario] = useState<TestScenario | null>(
    null
  );
  const [showEditor, setShowEditor] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [scenarioToDelete, setScenarioToDelete] = useState<TestScenario | null>(
    null
  );
  const [isDeleting, setIsDeleting] = useState(false);

  useEffect(() => {
    if (scenarios) {
      console.log("[Test] scenarios loaded:", scenarios.length);
    }
  }, [scenarios]);

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
    // Find the scenario from the current scenarios array to ensure we have the latest data
    const currentScenario = scenarios?.find(s => s.id === scenario.id);
    setEditingScenario(currentScenario || scenario);
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
    template: TestScenario["template"];
    imageFiles?: Map<number, File>;
  }) => {
    if (editingScenario) {
      // Update
      const toastId = toast.loading("Updating scenario...");
      try {
        // Always use FormData (backend only accepts multipart/form-data)
        const formData = new FormData();
        formData.append("name", fields.name);
        formData.append("description", fields.description);
        formData.append("template", JSON.stringify(fields.template));
        
        // Add image files if any
        if (fields.imageFiles && fields.imageFiles.size > 0) {
          fields.imageFiles.forEach((file, index) => {
            formData.append(`identity_${index}_image`, file);
          });
        }
        
        await updateMutation.mutateAsync({
          id: editingScenario.id,
          data: formData as unknown as Partial<TestScenario>,
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
        // Always use FormData (backend only accepts multipart/form-data)
        const formData = new FormData();
        formData.append("name", fields.name);
        formData.append("description", fields.description);
        formData.append("template", JSON.stringify(fields.template));
        
        // Add image files if any
        if (fields.imageFiles && fields.imageFiles.size > 0) {
          fields.imageFiles.forEach((file, index) => {
            formData.append(`identity_${index}_image`, file);
          });
        }
        
        await createMutation.mutateAsync(formData as unknown as Partial<TestScenario>);
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
        toast.error("Failed to delete test scenario", {
          id: toastId,
          description: err instanceof Error ? err.message : undefined,
        });
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

  // Handler for starting a scenario (continue from current state)
  const handleStartScenario = (scenario: TestScenario) => {
    // Step 1: Set the selected scenario to launch chat
    setSelectedScenario(scenario);
  };

  // Handler for starting a scenario fresh (reset to template)
  const handleStartFreshScenario = async (scenario: TestScenario) => {
    // Step 1: Reset the scenario on the backend
    const toastId = toast.loading("Resetting scenario...");
    try {
      await resetTestScenario(scenario.id);
      toast.success("Scenario reset. Launching...", { id: toastId });
      // Step 2: Refetch scenarios to get the updated state
      await refetch();
      // Step 3: Find the updated scenario and set as selected
      const updated = scenarios?.find((s) => s.id === scenario.id);
      if (updated) {
        setSelectedScenario(updated);
      } else {
        toast.error("Could not find updated scenario", { id: toastId });
      }
    } catch (err) {
      toast.error("Failed to reset scenario", {
        id: toastId,
        description: err instanceof Error ? err.message : undefined,
      });
    }
  };

  // Handler for resuming admin's own chat
  const handleResumeOwnSession = () => {
    setIsResumingOwnSession(true);
    setSelectedScenario(null);
  };

  // Handler for returning to the scenario table
  const handleBackToTable = () => {
    setSelectedScenario(null);
    setIsResumingOwnSession(false);
  };

  if (selectedScenario) {
    console.log("[Test] selectedScenario: ", selectedScenario);
    return (
      <TestChat
        scenario={selectedScenario}
        setHasStarted={handleBackToTable}
        testUserId={
          selectedScenario.template.user?.id
            ? String(selectedScenario.template.user.id)
            : undefined
        }
      />
    );
  }

  if (isResumingOwnSession) {
    // Provide a dummy scenario object for admin session
    const adminScenario = { name: "My Chat Session" } as TestScenario;
    return (
      <TestChat scenario={adminScenario} setHasStarted={handleBackToTable} />
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
          onStart={handleStartScenario}
          onStartFresh={handleStartFreshScenario}
        />
        <DeleteTestScenarioDialog
          isOpen={deleteDialogOpen}
          onClose={handleCancelDelete}
          onConfirm={handleConfirmDelete}
          scenario={scenarioToDelete}
          isDeleting={isDeleting}
        />
      </div>
      <div className="w-full max-w-5xl my-4 flex justify-end">
        <Button variant="default" onClick={handleResumeOwnSession}>
          Resume My Session
        </Button>
      </div>
      {showEditor && (
        <TestScenarioEditor
          scenario={editingScenario}
          onSave={handleSaveScenario}
          onCancel={handleCancelEdit}
          onDelete={
            editingScenario
              ? () => handleDeleteScenario(editingScenario)
              : undefined
          }
        />
      )}
    </div>
  );
}

export default Test;
