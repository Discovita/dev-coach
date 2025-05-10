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

export interface NewPromptFormProps {
  onSubmit: (data: PromptCreate) => Promise<void>;
}

export function NewPromptForm({ onSubmit }: NewPromptFormProps) {
  const [selectedActions, setSelectedActions] = useState<
    PromptCreate["allowed_actions"]
  >([]);
  const [selectedContextKeys, setSelectedContextKeys] = useState<
    PromptCreate["required_context_keys"]
  >([]);
  const [selectedCoachState, setSelectedCoachState] =
    useState<PromptCreate["coach_state"]>("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const [prompt, setPrompt] = useState<PromptCreate["body"]>("");
  const [name, setName] = useState<PromptCreate["name"]>("");
  const [description, setDescription] =
    useState<PromptCreate["description"]>("");
  const [submitting, setSubmitting] = useState<boolean>(false);

  const { data: enums, isLoading, isError } = useCoreEnums();

  const handleInputChange = useCallback(
    (e: React.ChangeEvent<HTMLTextAreaElement>) => setPrompt(e.target.value),
    []
  );

  function resetForm() {
    setName("");
    setDescription("");
    setSelectedCoachState("");
    setSelectedActions([]);
    setSelectedContextKeys([]);
    setPrompt("");
  }

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

  useEffect(() => {
    console.log("Selected actions:", selectedActions);
    console.log("Selected context keys:", selectedContextKeys);
    console.log("Selected coach state:", selectedCoachState);
  }, [selectedActions, selectedContextKeys, selectedCoachState]);

  return (
    <div className="_NewPromptForm h-full flex flex-col">
      <form
        className="flex flex-col flex-1 min-h-0 h-full border rounded p-4 bg-gold-50 dark:bg-gold-900"
        onSubmit={handleSubmit}
      >
        <Input
          id="name"
          name="name"
          type="text"
          className="font-bold text-2xl mb-1 text-gold-700 bg-transparent border-b border-gold-200 focus:outline-none focus:border-gold-500"
          value={name ?? ""}
          onChange={(e) => setName(e.target.value)}
          placeholder="Prompt name (optional)"
        />
        <Textarea
          id="description"
          name="description"
          value={description ?? ""}
          onChange={(e) => setDescription(e.target.value)}
          className="mb-2 text-base text-neutral-700 dark:text-gold-200 bg-transparent border-b border-gold-200 focus:outline-none focus:border-gold-500"
          placeholder="Prompt description (optional)"
        />
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
        <div className="flex justify-end mt-4">
          <Button variant="default" type="submit" disabled={submitting}>
            {submitting ? "Submitting..." : "Submit Prompt"}
          </Button>
        </div>
      </form>
    </div>
  );
}
