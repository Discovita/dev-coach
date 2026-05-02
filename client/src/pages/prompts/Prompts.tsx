import { NewPromptForm } from "./components/NewPromptForm";
import { useCoreEnums } from "@/hooks/use-core";
import { useState, useEffect, useMemo } from "react";
import { Tabs, TabsContent } from "@/components/ui/tabs";
import { usePrompts } from "@/hooks/use-prompts";
import {
  createPrompt,
  partialUpdatePrompt,
  softDeletePrompt,
} from "@/api/prompts";
import {
  Select,
  SelectTrigger,
  SelectContent,
  SelectItem,
  SelectValue,
  SelectGroup,
  SelectLabel,
} from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { MultiSelect } from "@/components/ui/multi-select";
import { Button } from "@/components/ui/button";
import { DeletePromptDialog } from "./components/DeletePromptDialog";
import { toast } from "sonner";
import { useRef } from "react";
import { useQueryClient } from "@tanstack/react-query";

const PROMPT_TYPE_TABS = ["image_generation", "sentinel"];

/**
 * PromptsTabs
 * Renders a tab for each coach state (from enums) plus prompt type tabs.
 * When a tab is selected, displays all prompt versions for that state.
 */
export function PromptsTabs() {
  const queryClient = useQueryClient();
  const { data: enums, isLoading: enumsLoading } = useCoreEnums();
  const {
    data: allPrompts,
    isLoading: promptsLoading,
    isError: promptsError,
    refetch: refetchPrompts,
  } = usePrompts();
  const [activeCoachState, setActiveCoachState] = useState<string | null>(null);
  const [selectedVersion, setSelectedVersion] = useState<number | null>(null);
  const prevActiveCoachStateRef = useRef<string | null>(null);

  const [editName, setEditName] = useState<string>("");
  const [editDescription, setEditDescription] = useState<string>("");
  const [editBody, setEditBody] = useState<string>("");
  const [editAllowedActions, setEditAllowedActions] = useState<string[]>([]);
  const [editContextKeys, setEditContextKeys] = useState<string[]>([]);
  const [editIsActive, setEditIsActive] = useState<boolean>(true);
  const [submittingEdit, setSubmittingEdit] = useState<boolean>(false);

  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

  useEffect(() => {
    if (enums?.coaching_phases && enums.coaching_phases.length > 0) {
      setActiveCoachState((prev) => prev ?? enums.coaching_phases[0].value);
    } else if (enums?.coaching_phases && enums.coaching_phases.length === 0) {
      setActiveCoachState("new");
    }
  }, [enums?.coaching_phases]);

  const prompts = useMemo(() => {
    if (!allPrompts || !activeCoachState || activeCoachState === "new") {
      return [];
    }
    if (PROMPT_TYPE_TABS.includes(activeCoachState)) {
      return allPrompts.filter((p) => p.prompt_type === activeCoachState);
    }
    return allPrompts.filter((p) => p.coaching_phase === activeCoachState);
  }, [allPrompts, activeCoachState]);

  const versions = Array.from(new Set(prompts.map((p) => p.version))).sort(
    (a, b) => b - a
  );
  const selectedPrompt =
    prompts.find((p) => p.version === selectedVersion) || null;

  useEffect(() => {
    if (prevActiveCoachStateRef.current !== activeCoachState) {
      if (versions.length > 0) {
        setSelectedVersion(versions[0]);
      } else {
        setSelectedVersion(null);
      }
    }
    prevActiveCoachStateRef.current = activeCoachState;
  }, [activeCoachState, versions]);

  useEffect(() => {
    if (activeCoachState && activeCoachState !== "new" && prompts.length > 0) {
      const availableVersions = Array.from(
        new Set(prompts.map((p) => p.version))
      ).sort((a, b) => b - a);
      if (availableVersions.length > 0) {
        const currentVersionExists = prompts.some(
          (p) => p.version === selectedVersion
        );
        if (selectedVersion === null || !currentVersionExists) {
          setSelectedVersion(availableVersions[0]);
        }
      }
    }
  }, [activeCoachState, prompts, selectedVersion]);

  function resetEditState() {
    if (selectedPrompt) {
      setEditName(selectedPrompt.name ?? "");
      setEditDescription(selectedPrompt.description ?? "");
      setEditBody(selectedPrompt.body ?? "");
      setEditAllowedActions(selectedPrompt.allowed_actions ?? []);
      setEditContextKeys(selectedPrompt.required_context_keys ?? []);
      setEditIsActive(selectedPrompt.is_active);
    }
  }

  useEffect(() => {
    resetEditState();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedPrompt]);

  const handleCreatePrompt = async (
    data: Parameters<typeof createPrompt>[0]
  ) => {
    try {
      await createPrompt(data);
      await refetchPrompts();
      toast.success("Prompt created successfully!");
    } catch (err) {
      toast.error("Failed to create prompt", {
        description: err instanceof Error ? err.message : undefined,
      });
      throw err;
    }
  };

  const handleEditSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedPrompt) return;
    setSubmittingEdit(true);
    try {
      await partialUpdatePrompt(selectedPrompt.id, {
        name: editName,
        description: editDescription,
        body: editBody,
        allowed_actions: editAllowedActions,
        required_context_keys: editContextKeys,
        is_active: editIsActive,
      });
      await refetchPrompts();
      toast.success("Prompt updated successfully!");
    } catch (err) {
      toast.error("Failed to update prompt", {
        description: err instanceof Error ? err.message : undefined,
      });
    } finally {
      setSubmittingEdit(false);
    }
  };

  const handleSaveAsNewVersion = async () => {
    if (!selectedPrompt) return;
    setSubmittingEdit(true);
    try {
      await createPrompt({
        coaching_phase: selectedPrompt.coaching_phase,
        prompt_type: selectedPrompt.prompt_type,
        name: editName,
        description: editDescription,
        body: editBody,
        allowed_actions: editAllowedActions,
        required_context_keys: editContextKeys,
        is_active: editIsActive,
      });
      await queryClient.invalidateQueries({ queryKey: ["prompts", "all"] });
      const refetchResult = await refetchPrompts();

      if (refetchResult.data) {
        const isPromptTypeTab = PROMPT_TYPE_TABS.includes(
          selectedPrompt.prompt_type
        );
        const updatedPrompts = isPromptTypeTab
          ? refetchResult.data.filter(
              (p) => p.prompt_type === selectedPrompt.prompt_type
            )
          : refetchResult.data.filter(
              (p) => p.coaching_phase === selectedPrompt.coaching_phase
            );
        const availableVersions = Array.from(
          new Set(updatedPrompts.map((p) => p.version))
        ).sort((a, b) => b - a);
        if (availableVersions.length > 0) {
          setSelectedVersion(availableVersions[0]);
        }
      }

      toast.success("Prompt saved as new version!");
    } catch (err) {
      toast.error("Failed to save as new version", {
        description: err instanceof Error ? err.message : undefined,
      });
    } finally {
      setSubmittingEdit(false);
    }
  };

  function hasUnsavedChanges() {
    if (!selectedPrompt) return false;
    return (
      editName !== (selectedPrompt.name ?? "") ||
      editDescription !== (selectedPrompt.description ?? "") ||
      editBody !== (selectedPrompt.body ?? "") ||
      editIsActive !== selectedPrompt.is_active ||
      JSON.stringify(editAllowedActions) !==
        JSON.stringify(selectedPrompt.allowed_actions ?? []) ||
      JSON.stringify(editContextKeys) !==
        JSON.stringify(selectedPrompt.required_context_keys ?? [])
    );
  }

  const handleOpenDeleteDialog = () => setDeleteDialogOpen(true);
  const handleCloseDeleteDialog = () => setDeleteDialogOpen(false);
  const handleConfirmDelete = async () => {
    if (!selectedPrompt) return;
    setIsDeleting(true);
    try {
      await softDeletePrompt(selectedPrompt.id);
      await refetchPrompts();
      const remainingPrompts = allPrompts
        ? allPrompts.filter((p) => !(p.id === selectedPrompt.id))
        : [];
      const sameStatePrompts = remainingPrompts.filter(
        (p) => p.coaching_phase === selectedPrompt.coaching_phase
      );
      if (sameStatePrompts.length > 0) {
        const nextVersion = Math.max(...sameStatePrompts.map((p) => p.version));
        setSelectedVersion(nextVersion);
      } else {
        setSelectedVersion(null);
      }
      setDeleteDialogOpen(false);
      toast.success("Prompt deleted (archived) successfully!");
    } catch (err) {
      toast.error("Failed to delete prompt", {
        description: err instanceof Error ? err.message : undefined,
      });
    } finally {
      setIsDeleting(false);
    }
  };

  if (enumsLoading || promptsLoading)
    return <div>Loading coach states and prompts...</div>;
  if (!enums?.coaching_phases) return <div>No coach states found.</div>;
  if (promptsError) return <div>Error loading prompts.</div>;

  const renderPromptEditor = () => {
    if (!selectedPrompt) {
      return (
        <div className="text-muted-foreground">
          No prompt found for this selection. Create one using the New Prompt tab.
        </div>
      );
    }

    return (
      <form
        onSubmit={handleEditSubmit}
        className="border rounded p-4 bg-background flex flex-col flex-1 min-h-0 h-full"
        style={{ height: "100%" }}
      >
        <input
          type="text"
          className="font-bold text-2xl mb-1 text-foreground bg-transparent border-b border-border focus:outline-none focus:border-primary"
          value={editName}
          onChange={(e) => setEditName(e.target.value)}
          placeholder="Prompt name (optional)"
        />
        <Textarea
          value={editDescription}
          onChange={(e) => setEditDescription(e.target.value)}
          placeholder="Prompt description (optional)"
        />
        <div className="items-center flex flex-wrap gap-4 text-xs text-muted-foreground border-b border-border py-2">
          <div className="flex items-center gap-2">
            <span className="font-semibold">Allowed Actions:</span>
            <div className="gap-2 flex flex-wrap">
              <MultiSelect
                options={enums?.allowed_actions || []}
                value={editAllowedActions}
                onValueChange={setEditAllowedActions}
                placeholder="Choose Allowed Actions"
              />
            </div>
          </div>
          <div className="flex items-center gap-2">
            <span className="font-semibold">Required Context Keys:</span>
            <div className="gap-2 flex flex-wrap">
              <MultiSelect
                options={enums?.context_keys || []}
                value={editContextKeys}
                onValueChange={setEditContextKeys}
                placeholder="Choose Context Keys"
              />
            </div>
          </div>
        </div>
        <div className="items-center flex flex-wrap gap-4 text-xs text-muted-foreground border-b border-border justify-between py-2">
          <div className="flex items-center gap-4">
            <div>
              <span className="font-semibold">Status:</span>{" "}
              <button
                type="button"
                className={`ml-2 px-2 py-1 rounded ${
                  editIsActive
                    ? "bg-green-600 text-white"
                    : "bg-red-600 text-white"
                }`}
                onClick={() => setEditIsActive((v) => !v)}
              >
                {editIsActive ? "Active" : "Inactive"}
              </button>
            </div>
            <div>
              <span className="font-semibold">Created:</span>{" "}
              {selectedPrompt.created_at}
            </div>
            <div>
              <span className="font-semibold">Updated:</span>{" "}
              {selectedPrompt.updated_at}
            </div>
          </div>
          <div className="flex items-center justify-end">
            <label htmlFor="version-select" className="font-bold mr-2">
              Version:
            </label>
            <Select
              value={
                selectedVersion !== null ? String(selectedVersion) : ""
              }
              onValueChange={(val) =>
                setSelectedVersion(val ? Number(val) : null)
              }
              name="version-select"
            >
              <SelectTrigger className="min-w-[120px] border rounded px-2 py-1">
                <SelectValue placeholder="Select version" />
              </SelectTrigger>
              <SelectContent>
                <SelectGroup>
                  <SelectLabel>Versions</SelectLabel>
                  {versions.map((v) => (
                    <SelectItem key={v} value={String(v)}>
                      Version {v}
                    </SelectItem>
                  ))}
                </SelectGroup>
              </SelectContent>
            </Select>
          </div>
        </div>
        <div className="flex-1 min-h-0 h-full flex flex-col mt-2">
          <Textarea
            value={editBody}
            onChange={(e) => setEditBody(e.target.value)}
            name="body"
            className="h-full flex-1 min-h-0 resize-none overflow-y-auto max-h-[10000]"
          />
        </div>
        <div className="flex justify-end gap-2 mt-4">
          <Button
            type="button"
            variant="secondary"
            onClick={handleSaveAsNewVersion}
            disabled={submittingEdit}
          >
            Save as New Version
          </Button>
          {hasUnsavedChanges() && (
            <Button
              type="button"
              variant="outline"
              onClick={resetEditState}
              disabled={submittingEdit}
            >
              Restore
            </Button>
          )}
          <Button
            type="button"
            variant="destructive"
            onClick={handleOpenDeleteDialog}
            disabled={submittingEdit}
          >
            Delete
          </Button>
          <Button type="submit" variant="default" disabled={submittingEdit}>
            {submittingEdit ? "Saving..." : "Save Changes"}
          </Button>
        </div>
      </form>
    );
  };

  return (
    <div className="flex-1 min-h-0 h-full flex flex-col">
      <Tabs
        value={activeCoachState ?? undefined}
        onValueChange={setActiveCoachState}
        className="flex flex-frow flex-col text-left flex-1 min-h-0 h-full"
      >
        <div className="w-full p-2 bg-muted border-b-2 border-border">
          <Select
            value={activeCoachState ?? undefined}
            onValueChange={(value) => setActiveCoachState(value)}
          >
            <SelectTrigger className="w-full bg-background">
              <SelectValue placeholder="Select prompt type..." />
            </SelectTrigger>
            <SelectContent>
              <SelectGroup>
                <SelectLabel>Prompt Types</SelectLabel>
                <SelectItem value="image_generation">Image Generation</SelectItem>
                <SelectItem value="sentinel">Sentinel</SelectItem>
              </SelectGroup>
              <SelectGroup>
                <SelectLabel>Coaching Phases</SelectLabel>
                {enums.coaching_phases.map((phase: { value: string; label: string }) => (
                  <SelectItem key={phase.value} value={phase.value}>
                    {phase.label}
                  </SelectItem>
                ))}
              </SelectGroup>
              <SelectGroup>
                <SelectLabel>Actions</SelectLabel>
                <SelectItem value="new">New Prompt</SelectItem>
              </SelectGroup>
            </SelectContent>
          </Select>
        </div>
        <TabsContent
          key="image_generation"
          value="image_generation"
          className="flex-1 flex flex-col min-h-0 h-full"
        >
          {renderPromptEditor()}
        </TabsContent>
        <TabsContent
          key="sentinel"
          value="sentinel"
          className="flex-1 flex flex-col min-h-0 h-full"
        >
          {renderPromptEditor()}
        </TabsContent>
        {enums.coaching_phases.map(
          (state: { value: string; label: string }) => (
            <TabsContent
              key={state.value}
              value={state.value}
              className="flex-1 flex flex-col min-h-0 h-full"
            >
              {renderPromptEditor()}
            </TabsContent>
          )
        )}
        <TabsContent key="new" value="new">
          <NewPromptForm onSubmit={handleCreatePrompt} />
        </TabsContent>
      </Tabs>
      <DeletePromptDialog
        isOpen={deleteDialogOpen}
        onClose={handleCloseDeleteDialog}
        onConfirm={handleConfirmDelete}
        prompt={selectedPrompt}
        isDeleting={isDeleting}
      />
    </div>
  );
}

function Prompts() {
  return (
    <div className="flex flex-col flex-1 min-h-0 h-full">
      <PromptsTabs />
    </div>
  );
}

export default Prompts;
