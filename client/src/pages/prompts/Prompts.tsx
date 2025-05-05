import { motion } from "framer-motion";
import { MultiSelect } from "@/components/ui/multi-select";
import { useEffect, useState } from "react";
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

function Prompts() {
  // State for selected actions, context keys, and coach state
  const [selectedActions, setSelectedActions] = useState<string[]>([]);
  const [selectedContextKeys, setSelectedContextKeys] = useState<string[]>([]);
  const [selectedCoachState, setSelectedCoachState] = useState<string>("");

  // Fetch enums from the API
  const { data: enums, isLoading, isError } = useCoreEnums();

  useEffect(() => {
    console.log("Selected actions:", selectedActions);
    console.log("Selected context keys:", selectedContextKeys);
    console.log("Selected coach state:", selectedCoachState);
  }, [selectedActions, selectedContextKeys, selectedCoachState]);

  return (
    <motion.div
      className="_Prompts text-center mb-12"
      key="prompts"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.8 }}
    >
      <h1 className="text-gold-700 text-2xl font-bold sm:text-4xl">
        Prompts Page
      </h1>
      <div className="flex flex-col items-center justify-center mt-4 max-w-2xl mx-auto gap-4">
        {/* Coach State Single Select */}
        {isLoading ? (
          <div>Loading coach states...</div>
        ) : isError ? (
          <div>Error loading coach states</div>
        ) : (
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
        )}
        {/* Actions MultiSelect */}
        {isLoading ? (
          <div>Loading actions...</div>
        ) : isError ? (
          <div>Error loading actions</div>
        ) : (
          <MultiSelect
            options={enums?.allowed_actions || []}
            value={selectedActions}
            onValueChange={setSelectedActions}
            placeholder="Choose Allowed Actions"
          />
        )}
        {/* Context Keys MultiSelect */}
        {isLoading ? (
          <div>Loading context keys...</div>
        ) : isError ? (
          <div>Error loading context keys</div>
        ) : (
          <MultiSelect
            options={enums?.context_keys || []}
            value={selectedContextKeys}
            onValueChange={setSelectedContextKeys}
            placeholder="Choose Context Keys"
          />
        )}
      </div>
    </motion.div>
  );
}

export default Prompts;
