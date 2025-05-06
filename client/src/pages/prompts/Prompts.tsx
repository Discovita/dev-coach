import { NewPromptForm } from "./components/NewPromptForm";
import { useCoreEnums } from "@/hooks/use-core";
import { useState, useEffect } from "react";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { usePrompts } from "@/hooks/use-prompts";
import { createPrompt, partialUpdatePrompt } from "@/api/prompts";
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

/**
 * PromptsTabs
 * -------------
 * 1. Renders a tab for each coach state (from enums).
 * 2. When a tab is selected, fetches all prompts for that coach state.
 * 3. Shows a version dropdown for all prompt versions for that state.
 * 4. Displays the selected prompt's details (name, description, body, etc.).
 * 5. Used above the NewPromptForm in the Prompts page.
 */
export function PromptsTabs() {
  // Fetch enums for coach states
  const { data: enums, isLoading: enumsLoading } = useCoreEnums();
  // Fetch all prompts (cached)
  const {
    data: allPrompts,
    isLoading: promptsLoading,
    isError: promptsError,
  } = usePrompts();
  // Track the active coach state tab (default to first coach state or 'new')
  const [activeCoachState, setActiveCoachState] = useState<string | null>(null);
  // Track the selected version
  const [selectedVersion, setSelectedVersion] = useState<number | null>(null);

  /**
   * State for editing the selected prompt.
   * These are initialized from the selected prompt when it changes.
   * - name, description, body, allowed_actions, required_context_keys, is_active
   * - Uses the same controls as NewPromptForm for consistency.
   */
  const [editName, setEditName] = useState<string>("");
  const [editDescription, setEditDescription] = useState<string>("");
  const [editBody, setEditBody] = useState<string>("");
  const [editAllowedActions, setEditAllowedActions] = useState<string[]>([]);
  const [editContextKeys, setEditContextKeys] = useState<string[]>([]);
  const [editIsActive, setEditIsActive] = useState<boolean>(true);
  // Track if we are submitting changes
  const [submittingEdit, setSubmittingEdit] = useState<boolean>(false);

  // Set default tab to first coach state (or 'new') when enums load
  useEffect(() => {
    if (enums?.coach_states && enums.coach_states.length > 0) {
      setActiveCoachState((prev) => prev ?? enums.coach_states[0].value);
    } else if (enums?.coach_states && enums.coach_states.length === 0) {
      setActiveCoachState("new");
    }
  }, [enums?.coach_states]);

  // Filter prompts for the selected coach state (in memory)
  const prompts =
    allPrompts && activeCoachState && activeCoachState !== "new"
      ? allPrompts.filter((p) => p.coach_state === activeCoachState)
      : [];

  // Extract available versions for the dropdown
  const versions = Array.from(new Set(prompts.map((p) => p.version))).sort(
    (a, b) => b - a
  );
  // Find the selected prompt
  const selectedPrompt =
    prompts.find((p) => p.version === selectedVersion) || null;

  // Automatically select the most recent version (highest number) when switching tabs or when versions change
  useEffect(() => {
    if (versions.length > 0) {
      // If no version is selected or the selected version is not in the list, select the highest
      if (selectedVersion === null || !versions.includes(selectedVersion)) {
        setSelectedVersion(versions[0]); // versions is sorted descending
      }
    } else {
      setSelectedVersion(null);
    }
    // Only run when activeCoachState, versions, or selectedVersion change
    // (safe: setSelectedVersion is a no-op if already correct)
  }, [activeCoachState, versions, selectedVersion]);

  // When selectedPrompt changes, initialize edit state
  useEffect(() => {
    if (selectedPrompt) {
      setEditName(selectedPrompt.name ?? "");
      setEditDescription(selectedPrompt.description ?? "");
      setEditBody(selectedPrompt.body ?? "");
      setEditAllowedActions(selectedPrompt.allowed_actions ?? []);
      setEditContextKeys(selectedPrompt.required_context_keys ?? []);
      setEditIsActive(selectedPrompt.is_active);
    }
  }, [selectedPrompt]);

  // Handler to adapt createPrompt (which returns Promise<Prompt>) to Promise<void> for NewPromptForm
  const handleCreatePrompt = async (
    data: Parameters<typeof createPrompt>[0]
  ) => {
    await createPrompt(data);
  };

  /**
   * Handler for saving prompt edits.
   * 1. Calls partialUpdatePrompt API with new values.
   * 2. Shows success/error feedback.
   * 3. Optionally refetches prompts.
   */
  const handleEditSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedPrompt) return;
    setSubmittingEdit(true);
    try {
      // Use PATCH (partialUpdatePrompt) to update only the editable fields of the prompt.
      await partialUpdatePrompt(selectedPrompt.id, {
        name: editName,
        description: editDescription,
        body: editBody,
        allowed_actions: editAllowedActions,
        required_context_keys: editContextKeys,
        is_active: editIsActive,
        // coach_state is not editable here, so we do not send it unless required by backend
      });
      // Optionally show a toast or refetch prompts
      // toast.success("Prompt updated successfully!");
    } catch {
      // toast.error("Failed to update prompt");
    } finally {
      setSubmittingEdit(false);
    }
  };

  if (enumsLoading || promptsLoading)
    return <div>Loading coach states and prompts...</div>;
  if (!enums?.coach_states) return <div>No coach states found.</div>;
  if (promptsError) return <div>Error loading prompts.</div>;

  // Add a special tab for creating a new prompt
  const allTabs = [
    ...enums.coach_states.map((state: { value: string; label: string }) => ({
      value: state.value,
      label: state.label,
    })),
    { value: "new", label: "New Prompt" },
  ];

  return (
    // Wrapper ensures height propagation for flex children (Textarea fill fix)
    <div className="flex-1 min-h-0 h-full flex flex-col">
      <Tabs
        value={activeCoachState ?? undefined}
        onValueChange={setActiveCoachState}
        className="flex flex-frow flex-col text-left flex-1 min-h-0 h-full"
      >
        <TabsList className="border-b-2 bg-gold-200 border-gold-500 flex gap-2 w-full dark:text-gold-50">
          {allTabs.map((tab) => (
            <TabsTrigger key={tab.value} value={tab.value}>
              {tab.label}
            </TabsTrigger>
          ))}
        </TabsList>
        {/* Render a tab panel for each coach state */}
        {enums.coach_states.map((state: { value: string; label: string }) => (
          <TabsContent
            key={state.value}
            value={state.value}
            className="flex-1 flex flex-col min-h-0 h-full"
          >
            {" "}
            {/* Show prompt details */}
            {selectedPrompt ? (
              <form
                onSubmit={handleEditSubmit}
                className="border rounded p-4 bg-gold-50 dark:bg-gold-900 flex flex-col flex-1 min-h-0 h-full"
                style={{ height: "100%" }}
              >
                {/* Name and Description (editable) */}
                <input
                  type="text"
                  className="font-bold text-2xl mb-1 text-gold-700 bg-transparent border-b border-gold-200 focus:outline-none focus:border-gold-500"
                  value={editName}
                  onChange={(e) => setEditName(e.target.value)}
                  placeholder="Prompt name (optional)"
                />
                <Textarea
                  value={editDescription}
                  onChange={(e) => setEditDescription(e.target.value)}
                  placeholder="Prompt description (optional)"
                />
                {/* Actions and Context Keys (editable) */}
                <div className="items-center flex flex-wrap gap-4 text-xs text-neutral-500 dark:text-gold-300 border-b border-gold-200 dark:border-gold-800 py-2">
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
                {/* Status toggle (optional) */}
                <div className="items-center flex flex-wrap gap-4 text-xs text-neutral-500 dark:text-gold-300 border-b border-gold-200 dark:border-gold-800 justify-between py-2">
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
                {/* Prompt Body (editable) */}
                <div className="flex-1 min-h-0 h-full flex flex-col mt-2">
                  <Textarea
                    value={editBody}
                    onChange={(e) => setEditBody(e.target.value)}
                    name="body"
                    className="h-full flex-1 min-h-0 resize-none overflow-y-auto max-h-[10000]"
                  />
                </div>
                {/* Save Changes button */}
                <div className="flex justify-end mt-4">
                  <button
                    type="submit"
                    className="bg-gold-600 text-white px-4 py-2 rounded hover:bg-gold-700 disabled:opacity-50"
                    disabled={submittingEdit}
                  >
                    {submittingEdit ? "Saving..." : "Save Changes"}
                  </button>
                </div>
              </form>
            ) : (
              <div className="text-neutral-500">
                No prompt found for this version.
              </div>
            )}
          </TabsContent>
        ))}
        <TabsContent key="new" value="new">
          <NewPromptForm onSubmit={handleCreatePrompt} />
        </TabsContent>
      </Tabs>
    </div>
  );
}

function Prompts() {
  // The AdminLayout now handles all height and scrolling. This page should just fill the space.
  // Ensure this root div allows children to grow to full height.
  return (
    <div className="flex flex-col flex-1 min-h-0 h-full">
      {/* Tabs for viewing prompts by coach state and version, and for creating a new prompt */}
      <PromptsTabs />
    </div>
  );
}

export default Prompts;
