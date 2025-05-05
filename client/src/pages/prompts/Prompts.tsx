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
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";

function Prompts() {
  // State for selected actions, context keys, and coach state
  const [selectedActions, setSelectedActions] = useState<string[]>([]);
  const [selectedContextKeys, setSelectedContextKeys] = useState<string[]>([]);
  const [selectedCoachState, setSelectedCoachState] = useState<string>("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const [prompt, setPrompt] = useState("");

  // Fetch enums from the API
  const { data: enums, isLoading, isError } = useCoreEnums();

  const handleInputChange = useCallback(
    (e: React.ChangeEvent<HTMLTextAreaElement>) => {
      setPrompt(e.target.value);
      // resizeTextarea will be called by useEffect
    },
    []
  );

  useEffect(() => {
    console.log("Selected actions:", selectedActions);
    console.log("Selected context keys:", selectedContextKeys);
    console.log("Selected coach state:", selectedCoachState);
  }, [selectedActions, selectedContextKeys, selectedCoachState]);

  return (
    <motion.div
      className="_Prompts text-center mb-16 h-full mt-10"
      key="prompts"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.8 }}
    >
      <h1 className="text-gold-700 text-2xl font-bold sm:text-4xl">
        New Prompt
      </h1>
      <div className="flex flex-col items-center mt-4 max-w-5xl mx-auto gap-4 h-full">
        {/* Coach State Single Select */}
        {isLoading ? (
          <div>Loading coach states...</div>
        ) : isError ? (
          <div>Error loading coach states</div>
        ) : (
          <div className="max-w-2xl">
            <Select
              value={selectedCoachState}
              onValueChange={setSelectedCoachState}
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
        {/* Actions MultiSelect */}
        {isLoading ? (
          <div>Loading actions...</div>
        ) : isError ? (
          <div>Error loading actions</div>
        ) : (
          <div className="w-2xl">
            <MultiSelect
              options={enums?.allowed_actions || []}
              value={selectedActions}
              onValueChange={setSelectedActions}
              placeholder="Choose Allowed Actions"
            />
          </div>
        )}
        {/* Context Keys MultiSelect */}
        {isLoading ? (
          <div>Loading context keys...</div>
        ) : isError ? (
          <div>Error loading context keys</div>
        ) : (
          <div className="w-2xl">
            <MultiSelect
              options={enums?.context_keys || []}
              value={selectedContextKeys}
              onValueChange={setSelectedContextKeys}
              placeholder="Choose Context Keys"
            />
          </div>
        )}
        <Label
          htmlFor="prompt"
          className="text-gold-700 text-lg font-bold mt-4"
        >
          Prompt
        </Label>
        {/* Make the textarea grow to fill remaining space */}
        <div className="flex flex-col h-full w-full max-w-5xl">
          <Textarea
            ref={textareaRef}
            value={prompt}
            onChange={handleInputChange}
            className="h-full flex-1 max-h-[10000]"
          />
        </div>
        <Button
          className="mt-4"
          variant="default"
          onClick={() => {
            console.log("Prompt submitted");
          }}
        >
          Submit Prompt
        </Button>
      </div>
    </motion.div>
  );
}

export default Prompts;
