import { MultiSelect } from "@/components/ui/multi-select";
import { useCallback, useRef, useState } from "react";
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
import type { PromptCreate } from "@/types/prompt";
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
    useState<PromptCreate["coaching_phase"]>("");
  const [selectedPromptType, setSelectedPromptType] =
    useState<PromptCreate["prompt_type"]>("coach");
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
    setSelectedPromptType("coach");
    setSelectedActions([]);
    setSelectedContextKeys([]);
    setPrompt("");
  }

  const nonCoachingPhasePromptTypes = ["image_generation", "sentinel"];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      const promptData: PromptCreate = {
        coaching_phase: nonCoachingPhasePromptTypes.includes(
          selectedPromptType ?? ""
        )
          ? null
          : selectedCoachState,
        prompt_type: selectedPromptType,
        allowed_actions: selectedActions,
        required_context_keys: selectedContextKeys,
        body: prompt,
        name: name || undefined,
        description: description || undefined,
      };
      await onSubmit(promptData);
      toast.success("Prompt submitted successfully!");
      resetForm();
    } catch (err: unknown) {
      toast.error("Failed to submit prompt", {
        description: err instanceof Error ? err.message : undefined,
      });
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="_NewPromptForm h-full flex flex-col">
      <form
        className="flex flex-col flex-1 min-h-0 h-full border rounded p-4 bg-background"
        onSubmit={handleSubmit}
      >
        <Input
          id="name"
          name="name"
          type="text"
          className="font-bold text-2xl mb-1 text-foreground bg-transparent border-b border-border focus:outline-none focus:border-primary"
          value={name ?? ""}
          onChange={(e) => setName(e.target.value)}
          placeholder="Prompt name (optional)"
        />
        <Textarea
          id="description"
          name="description"
          value={description ?? ""}
          onChange={(e) => setDescription(e.target.value)}
          className="mb-2 text-base text-foreground bg-transparent border-b border-border focus:outline-none focus:border-primary"
          placeholder="Prompt description (optional)"
        />
        {isLoading ? (
          <div>Loading enums...</div>
        ) : isError ? (
          <div>Error loading enums</div>
        ) : (
          <div className="flex flex-wrap gap-4 mb-2">
            <div>
              <Select
                value={selectedPromptType}
                onValueChange={setSelectedPromptType}
                name="prompt_type"
              >
                <SelectTrigger className="min-w-[200px]">
                  <SelectValue placeholder="Choose Prompt Type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectGroup>
                    <SelectLabel>Prompt Type</SelectLabel>
                    {enums?.prompt_types?.map(
                      (type: { value: string; label: string }) => (
                        <SelectItem key={type.value} value={type.value}>
                          {type.label}
                        </SelectItem>
                      )
                    )}
                  </SelectGroup>
                </SelectContent>
              </Select>
            </div>
            {!nonCoachingPhasePromptTypes.includes(selectedPromptType ?? "") && (
              <div>
                <Select
                  value={selectedCoachState ?? ""}
                  onValueChange={setSelectedCoachState}
                  name="coaching_phase"
                >
                  <SelectTrigger className="min-w-[200px]">
                    <SelectValue placeholder="Choose Coaching Phase" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectGroup>
                      <SelectLabel>Coaching Phases</SelectLabel>
                      {enums?.coaching_phases?.map(
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
          </div>
        )}
        <div className="items-center flex flex-wrap gap-4 text-xs text-muted-foreground border-b border-border py-2">
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
            className="h-full flex-1 min-h-0 resize-none overflow-y-auto max-h-[10000] bg-background p-3 rounded text-sm border border-border w-full"
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
