import { useRef, useState } from "react";
import { TestScenarioAction } from "@/types/testScenario";
import { ActionType } from "@/enums/actionType";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectTrigger, SelectContent, SelectItem, SelectValue } from "@/components/ui/select";
import { Label } from "@/components/ui/label";

interface Props {
  value: TestScenarioAction[];
  onChange: (actions: TestScenarioAction[]) => void;
}

const actionTypes = Object.values(ActionType);

/**
 * TestScenarioActionsForm Visual Logic
 * ------------------------------------
 * - Each action row has extra vertical padding and minHeight to prevent content from being cut off.
 * - Actions have a light blue background and a left border for emphasis.
 * - Uses box-sizing: border-box to ensure padding is included in height calculations.
 * - Parameters are displayed as JSON for easy editing.
 */
export default function TestScenarioActionsForm({ value, onChange }: Props) {
  const parentRef = useRef<HTMLDivElement>(null);
  const [draft, setDraft] = useState<TestScenarioAction>({ 
    action_type: ActionType.CREATE_IDENTITY, 
    parameters: {},
    result_summary: "",
    coach_message_content: ""
  });
  const [editingIndex, setEditingIndex] = useState<number | null>(null);
  const [parametersText, setParametersText] = useState("{}");

  const handleSave = () => {
    if (!draft.action_type) return;
    
    // Parse parameters JSON
    let parsedParameters = {};
    try {
      parsedParameters = JSON.parse(parametersText);
    } catch {
      alert("Invalid JSON in parameters field");
      return;
    }

    const actionToSave = {
      ...draft,
      parameters: parsedParameters
    };

    if (editingIndex !== null) {
      const updated = value.map((action, i) => (i === editingIndex ? actionToSave : action));
      onChange(updated);
      setEditingIndex(null);
    } else {
      onChange([...value, actionToSave]);
    }
    
    setDraft({ 
      action_type: ActionType.CREATE_IDENTITY, 
      parameters: {},
      result_summary: "",
      coach_message_content: ""
    });
    setParametersText("{}");
  };

  const handleEdit = (idx: number) => {
    setEditingIndex(idx);
    setDraft(value[idx]);
    setParametersText(JSON.stringify(value[idx].parameters, null, 2));
  };

  const handleDelete = (idx: number) => {
    onChange(value.filter((_, i) => i !== idx));
    if (editingIndex === idx) {
      setEditingIndex(null);
      setDraft({ 
        action_type: ActionType.CREATE_IDENTITY, 
        parameters: {},
        result_summary: "",
        coach_message_content: ""
      });
      setParametersText("{}");
    }
  };

  return (
    <div className="_TestScenarioActionsForm flex flex-col gap-4">
      <div>
        <div className="flex flex-col gap-2 mb-2">
          <div className="flex gap-2">
            <Select value={draft.action_type} onValueChange={actionType => setDraft(d => ({ ...d, action_type: actionType as ActionType }))}>
              <SelectTrigger className="w-48">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {actionTypes.map(actionType => (
                  <SelectItem key={actionType} value={actionType}>{actionType}</SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Button type="button" onClick={handleSave} className="shrink-0">
              {editingIndex !== null ? "Save" : "Add"}
            </Button>
          </div>
          
          <div className="grid grid-cols-1 gap-2">
            <div>
              <Label htmlFor="parameters">Parameters (JSON)</Label>
              <Textarea
                id="parameters"
                value={parametersText}
                onChange={e => setParametersText(e.target.value)}
                placeholder='{"name": "Professional", "category": "CAREER"}'
                className="font-mono text-sm"
                rows={3}
              />
            </div>
            
            <div>
              <Label htmlFor="result_summary">Result Summary</Label>
              <Input
                id="result_summary"
                value={draft.result_summary}
                onChange={e => setDraft(d => ({ ...d, result_summary: e.target.value }))}
                placeholder="What the action accomplished"
              />
            </div>
            
            <div>
              <Label htmlFor="coach_message_content">Coach Message Content</Label>
              <Input
                id="coach_message_content"
                value={draft.coach_message_content}
                onChange={e => setDraft(d => ({ ...d, coach_message_content: e.target.value }))}
                placeholder="Content of the coach message that triggered this action"
              />
            </div>
          </div>
        </div>
      </div>
      
      <div
        ref={parentRef}
        className="overflow-auto border border-[#eee] rounded-lg bg-white"
        style={{ height: 500, width: "100%" }}
      >
        {value.map((action, idx) => (
          <div
            key={idx}
            className="flex items-start gap-2 border-b border-[#f3f3f3] px-4 py-3 min-h-[48px] box-border w-full bg-[#f0f8ff] border-l-4 border-l-[#3b82f6]"
          >
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-1">
                <span className="font-mono text-xs text-[#1e40af] font-bold">
                  {action.action_type}
                </span>
                {action.timestamp && (
                  <span className="text-xs text-gray-500">
                    {new Date(action.timestamp).toLocaleString()}
                  </span>
                )}
              </div>
              
              <div className="text-sm mb-1">
                <strong>Parameters:</strong>
                <pre className="text-xs bg-gray-100 p-1 rounded mt-1 overflow-x-auto">
                  {JSON.stringify(action.parameters, null, 2)}
                </pre>
              </div>
              
              {action.result_summary && (
                <div className="text-sm mb-1">
                  <strong>Result:</strong> {action.result_summary}
                </div>
              )}
              
              {action.coach_message_content && (
                <div className="text-sm">
                  <strong>Coach Message:</strong> 
                  <div className="text-xs bg-yellow-50 p-1 rounded mt-1 italic">
                    {action.coach_message_content}
                  </div>
                </div>
              )}
            </div>
            
            <div className="flex gap-1">
              <Button size="xs" variant="secondary" onClick={() => handleEdit(idx)}>
                Edit
              </Button>
              <Button size="xs" variant="destructive" onClick={() => handleDelete(idx)}>
                Delete
              </Button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
} 