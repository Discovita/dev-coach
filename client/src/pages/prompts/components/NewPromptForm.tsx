import { motion } from "framer-motion";
import { MultiSelect } from "@/components/ui/multi-select";
import { useCallback, useEffect, useRef, useState } from "react";
import { useCoreEnums } from "@/hooks/use-core";
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
import { Button } from "@/components/ui/button";
import { toast } from "sonner";
import { PromptCreate } from "@/types/prompt";
import { Input } from "@/components/ui/input";

/**
 * Props for NewPromptForm
 * @param onSubmit - Called with the form data when the form is submitted and valid.
 *   Should return a Promise. If it rejects, an error toast is shown.
 *   Uses PromptCreate type for type safety.
 */
export interface NewPromptFormProps {
  /**
   * onSubmit handler
   * Called with the form data when the form is submitted.
   * Should return a Promise. If it rejects, an error toast is shown.
   * Used in Prompts.tsx to call addPromptToBackend.
   */
  onSubmit: (data: PromptCreate) => Promise<void>;
}

/**
 * NewPromptForm
 * -------------
 * 1. Handles all state and UI for creating a new prompt.
 * 2. Fetches enums for select/multiselect fields.
 * 3. Calls onSubmit prop with form data.
 * 4. Shows toast notifications for success/error.
 *
 * Used in Prompts.tsx
 */
export function NewPromptForm({ onSubmit }: NewPromptFormProps) {
  // State for form fields, using PromptCreate type for type safety
  const [selectedActions, setSelectedActions] = useState<
    PromptCreate["allowed_actions"]
  >([]); // required
  const [selectedContextKeys, setSelectedContextKeys] = useState<
    PromptCreate["required_context_keys"]
  >([]); // required
  const [selectedCoachState, setSelectedCoachState] =
    useState<PromptCreate["coach_state"]>(""); // required
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const [prompt, setPrompt] = useState<PromptCreate["body"]>(""); // required
  const [name, setName] = useState<PromptCreate["name"]>(""); // optional
  const [description, setDescription] =
    useState<PromptCreate["description"]>(""); // optional
  const [submitting, setSubmitting] = useState<boolean>(false);

  // Fetch enums for select fields
  const { data: enums, isLoading, isError } = useCoreEnums();

  // Handle textarea input
  const handleInputChange = useCallback(
    (e: React.ChangeEvent<HTMLTextAreaElement>) => setPrompt(e.target.value),
    []
  );

  /**
   * Resets all form fields to their initial (empty) state.
   * Called after a successful submit.
   */
  function resetForm() {
    setName("");
    setDescription("");
    setSelectedCoachState("");
    setSelectedActions([]);
    setSelectedContextKeys([]);
    setPrompt("");
  }

  /**
   * Handles form submission:
   * 1. Prevents default form submit.
   * 2. Calls onSubmit prop with form data.
   * 3. Shows success or error toast.
   */
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await onSubmit({
        coach_state: selectedCoachState,
        allowed_actions: selectedActions,
        required_context_keys: selectedContextKeys,
        body: prompt,
        name: name || undefined,
        description: description || undefined,
      });
      toast.success("Prompt submitted successfully!");
      // Reset form after successful submit
      resetForm();
    } catch (err: unknown) {
      toast.error("Failed to submit prompt", {
        description: err instanceof Error ? err.message : undefined,
      });
    } finally {
      setSubmitting(false);
    }
  };

  // Debug: log selected values
  useEffect(() => {
    console.log("Selected actions:", selectedActions);
    console.log("Selected context keys:", selectedContextKeys);
    console.log("Selected coach state:", selectedCoachState);
  }, [selectedActions, selectedContextKeys, selectedCoachState]);

  return (
    <motion.div
      className="_NewPromptForm h-full flex flex-col"
      key="new-prompt-form"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.8 }}
    >
      {/*
        Layout mimics the prompt editor:
        - Form is flex-1 min-h-0 h-full flex-col
        - Name, description, selects, and status at the top
        - Body Textarea fills remaining space
        - Submit button at the bottom
      */}
      <form
        className="flex flex-col flex-1 min-h-0 h-full border rounded p-4 bg-gold-50 dark:bg-gold-900"
        onSubmit={handleSubmit}
      >
        {/* Name (optional) */}
        <Input
          id="name"
          name="name"
          type="text"
          className="font-bold text-2xl mb-1 text-gold-700 bg-transparent border-b border-gold-200 focus:outline-none focus:border-gold-500"
          value={name ?? ""}
          onChange={(e) => setName(e.target.value)}
          placeholder="Prompt name (optional)"
        />
        {/* Description (optional) */}
        <Textarea
          id="description"
          name="description"
          value={description ?? ""}
          onChange={(e) => setDescription(e.target.value)}
          className="mb-2 text-base text-neutral-700 dark:text-gold-200 bg-transparent border-b border-gold-200 focus:outline-none focus:border-gold-500"
          placeholder="Prompt description (optional)"
        />
        {/* Coach State Select */}
        {isLoading ? (
          <div>Loading coach states...</div>
        ) : isError ? (
          <div>Error loading coach states</div>
        ) : (
          <div className="max-w-2xl mb-2">
            <Select
              value={selectedCoachState}
              onValueChange={setSelectedCoachState}
              name="coach_state"
            >
              <SelectTrigger className="min-w-[200px]">
                <SelectValue placeholder="Choose Coach State" />
              </SelectTrigger>
              <SelectContent>
                <SelectGroup>
                  <SelectLabel>Coach States</SelectLabel>
                  {enums?.coach_states?.map(
                    (state: { value: string; label: string }) => (
                      <SelectItem key={state.value} value={state.value}>
                        {state.label}
                      </SelectItem>
                    )
                  )}
                </SelectGroup>
              </SelectContent>
            </Select>
          </div>
        )}
        {/* Allowed Actions and Context Keys */}
        <div className="items-center flex flex-wrap gap-4 text-xs text-neutral-500 dark:text-gold-300 border-b border-gold-200 dark:border-gold-800 py-2">
          <div className="flex items-center gap-2">
            <span className="font-semibold">Allowed Actions:</span>
            <div className="gap-2 flex flex-wrap">
              <MultiSelect
                options={enums?.allowed_actions || []}
                value={selectedActions}
                onValueChange={setSelectedActions}
                placeholder="Choose Allowed Actions"
              />
            </div>
          </div>
          <div className="flex items-center gap-2">
            <span className="font-semibold">Required Context Keys:</span>
            <div className="gap-2 flex flex-wrap">
              <MultiSelect
                options={enums?.context_keys || []}
                value={selectedContextKeys}
                onValueChange={setSelectedContextKeys}
                placeholder="Choose Context Keys"
              />
            </div>
          </div>
        </div>
        {/* Prompt Body (fills remaining space) */}
        <div className="flex-1 min-h-0 h-full flex flex-col mt-2">
          <Textarea
            ref={textareaRef}
            value={prompt}
            onChange={handleInputChange}
            name="body"
            className="h-full flex-1 min-h-0 resize-none overflow-y-auto max-h-[10000] bg-white dark:bg-gold-950 p-3 rounded text-sm border border-gold-100 dark:border-gold-800 w-full"
            placeholder="Prompt body"
          />
        </div>
        {/* Submit button at the bottom */}
        <div className="flex justify-end mt-4">
          <Button variant="default" type="submit" disabled={submitting}>
            {submitting ? "Submitting..." : "Submit Prompt"}
          </Button>
        </div>
      </form>
    </motion.div>
  );
}
