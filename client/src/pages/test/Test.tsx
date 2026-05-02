import { useState } from "react";
import TestChat from "@/pages/test/components/TestChat";
import {
  ModuleRegistry,
  ClientSideRowModelModule,
  ValidationModule,
} from "ag-grid-community";
import { useTestScenarios } from "@/hooks/test-scenario/use-test-scenarios";
import type { TestScenario } from "@/types/testScenario";
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

  const createMutation = useMutation({
    mutationFn: createTestScenario,
    onSuccess: () => {
      refetch();
      setShowEditor(false);
      setEditingScenario(null);
    },
    onError: () => {},
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<TestScenario> }) =>
      updateTestScenario(id, data),
    onSuccess: () => {
      refetch();
      setShowEditor(false);
      setEditingScenario(null);
    },
    onError: () => {},
  });

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

  const handleEditScenario = (scenario: TestScenario) => {
    const currentScenario = scenarios?.find(s => s.id === scenario.id);
    setEditingScenario(currentScenario || scenario);
    setShowEditor(true);
  };

  const handleCreateScenario = () => {
    setEditingScenario(null);
    setShowEditor(true);
  };

  const handleSaveScenario = async (fields: {
    name: string;
    description: string;
    template: TestScenario["template"];
    imageFiles?: Map<number, File>;
  }) => {
    if (editingScenario) {
      const toastId = toast.loading("Updating scenario...");
      try {
        const formData = new FormData();
        formData.append("name", fields.name);
        formData.append("description", fields.description);
        formData.append("template", JSON.stringify(fields.template));
        
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
      const toastId = toast.loading("Creating scenario...");
      try {
        const formData = new FormData();
        formData.append("name", fields.name);
        formData.append("description", fields.description);
        formData.append("template", JSON.stringify(fields.template));
        
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

  const handleDeleteScenario = (scenario: TestScenario) => {
    setScenarioToDelete(scenario);
    setDeleteDialogOpen(true);
  };

  const handleConfirmDelete = () => {
    if (!scenarioToDelete) return;
    setIsDeleting(true);
    const toastId = toast.loading("Deleting scenario...");
    deleteMutation.mutate(scenarioToDelete.id, {
      onSuccess: () => {
        toast.success("Test scenario deleted successfully!", { id: toastId });
        setDeleteDialogOpen(false);
        setScenarioToDelete(null);
        setShowEditor(false);
        setEditingScenario(null);
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

  const handleCancelDelete = () => {
    setDeleteDialogOpen(false);
    setScenarioToDelete(null);
    setIsDeleting(false);
  };

  const handleCancelEdit = () => {
    setShowEditor(false);
    setEditingScenario(null);
  };

  const handleStartScenario = (scenario: TestScenario) => {
    setSelectedScenario(scenario);
  };

  const handleStartFreshScenario = async (scenario: TestScenario) => {
    const toastId = toast.loading("Resetting scenario...");
    try {
      await resetTestScenario(scenario.id);
      toast.success("Scenario reset. Launching...", { id: toastId });
      await refetch();
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

  const handleResumeOwnSession = () => {
    setIsResumingOwnSession(true);
    setSelectedScenario(null);
  };

  const handleBackToTable = () => {
    setSelectedScenario(null);
    setIsResumingOwnSession(false);
  };

  if (selectedScenario) {
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
