import { useState } from "react";
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

const emptyAction = (): TestScenarioAction => ({
  action_type: ActionType.CREATE_IDENTITY,
  parameters: {},
  result_summary: "",
  coach_message_content: ""
});

/**
 * TestScenarioActionsForm Visual Logic
 * ------------------------------------
 * - Follows the same pattern as TestScenarioIdentitiesForm
 * - Actions list displayed on top with clean, minimal design
 * - Edit form below in a bordered container
 * - Consistent styling with other form components
 * - Expandable action details for better organization
 */
export default function TestScenarioActionsForm({ value, onChange }: Props) {
  const [editingIndex, setEditingIndex] = useState<number | null>(null);
  const [draft, setDraft] = useState<TestScenarioAction>(emptyAction());
  const [error, setError] = useState<string | null>(null);
  const [parametersText, setParametersText] = useState("{}");
  const [expandedActions, setExpandedActions] = useState<Set<number>>(new Set());

  const handleEdit = (idx: number) => {
    setEditingIndex(idx);
    setDraft({ ...value[idx] });
    setParametersText(JSON.stringify(value[idx].parameters, null, 2));
    setError(null);
  };

  const handleDelete = (idx: number) => {
    const updated = value.filter((_, i) => i !== idx);
    onChange(updated);
    if (editingIndex === idx) {
      setEditingIndex(null);
      setDraft(emptyAction());
      setParametersText("{}");
    }
  };

  const handleSave = () => {
    if (!draft.action_type) {
      setError("Action type is required.");
      return;
    }
    
    // Parse parameters JSON
    let parsedParameters = {};
    try {
      parsedParameters = JSON.parse(parametersText);
    } catch {
      setError("Invalid JSON in parameters field");
      return;
    }

    setError(null);
    const actionToSave = {
      ...draft,
      parameters: parsedParameters
    };

    if (editingIndex !== null) {
      const updated = value.map((action, i) => (i === editingIndex ? actionToSave : action));
      onChange(updated);
      setEditingIndex(null);
      setDraft(emptyAction());
      setParametersText("{}");
    } else {
      const updated = [...value, actionToSave];
      onChange(updated);
      setDraft(emptyAction());
      setParametersText("{}");
    }
  };

  const handleCancel = () => {
    setEditingIndex(null);
    setDraft(emptyAction());
    setParametersText("{}");
    setError(null);
  };

  const toggleExpanded = (idx: number) => {
    const newExpanded = new Set(expandedActions);
    if (newExpanded.has(idx)) {
      newExpanded.delete(idx);
    } else {
      newExpanded.add(idx);
    }
    setExpandedActions(newExpanded);
  };

  return (
    <div className="flex flex-col gap-6 mt-4">
      <div>
        <h3 className="font-semibold mb-2">Actions</h3>
        {value.length === 0 && (
          <div className="text-neutral-400 mb-2">No actions added yet.</div>
        )}
        <ul className="divide-y divide-neutral-200 mb-4">
          {value.map((action, idx) => (
            <li
              key={idx}
              className="py-2 flex flex-col md:flex-row md:items-center gap-2"
            >
              <div className="flex-1">
                <div className="flex items-center gap-2">
                  {action.result_summary ? (
                    <span className="font-medium">
                      {action.result_summary}
                    </span>
                  ) : (
                    <span className="font-medium text-neutral-500">
                      No result summary
                    </span>
                  )}
                  <span className="text-xs text-neutral-500 font-mono">
                    [{action.action_type}]
                  </span>
                  <span
                    className={`text-xs text-neutral-400 cursor-pointer transition-transform ${
                      expandedActions.has(idx) ? "" : "rotate-[-90deg]"
                    }`}
                    onClick={() => toggleExpanded(idx)}
                  >
                    ▼
                  </span>
                </div>
                
                {/* Expandable details */}
                {expandedActions.has(idx) && (
                  <div className="mt-2 space-y-2 text-xs">
                    <div>
                      <span className="font-semibold text-neutral-700">Parameters:</span>
                      <pre className="bg-gray-100 p-2 rounded mt-1 overflow-x-auto font-mono text-xs">
                        {JSON.stringify(action.parameters, null, 2)}
                      </pre>
                    </div>
                    
                    {action.coach_message_content && (
                      <div>
                        <span className="font-semibold text-neutral-700">Coach Message:</span>
                        <div className="bg-yellow-50 p-2 rounded mt-1 italic">
                          {action.coach_message_content}
                        </div>
                      </div>
                    )}
                    
                    {action.timestamp && (
                      <div>
                        <span className="font-semibold text-neutral-700">Timestamp:</span>
                        <span className="text-neutral-600 ml-1">
                          {new Date(action.timestamp).toLocaleString()}
                        </span>
                      </div>
                    )}
                  </div>
                )}
              </div>
              <div className="flex gap-2">
                <Button
                  type="button"
                  size="xs"
                  variant="secondary"
                  onClick={() => handleEdit(idx)}
                >
                  Edit
                </Button>
                <Button
                  type="button"
                  size="xs"
                  variant="destructive"
                  onClick={() => handleDelete(idx)}
                >
                  Delete
                </Button>
              </div>
            </li>
          ))}
        </ul>
      </div>
      
      <div className="border rounded p-4 bg-neutral-50">
        <h4 className="font-semibold mb-2">
          {editingIndex !== null ? "Edit Action" : "Add Action"}
        </h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <Label className="mb-2">Action Type</Label>
            <Select value={draft.action_type} onValueChange={actionType => setDraft(d => ({ ...d, action_type: actionType as ActionType }))}>
              <SelectTrigger className="w-full mt-1">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {actionTypes.map(actionType => (
                  <SelectItem key={actionType} value={actionType}>{actionType}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          
          <div>
            <Label className="mb-2">Result Summary</Label>
            <Input
              value={draft.result_summary || ""}
              onChange={e => setDraft(d => ({ ...d, result_summary: e.target.value }))}
              placeholder="What the action accomplished"
            />
          </div>
          
          <div className="md:col-span-2">
            <Label className="mb-2">Parameters (JSON)</Label>
            <Textarea
              value={parametersText}
              onChange={e => setParametersText(e.target.value)}
              placeholder='{"name": "Professional", "category": "CAREER"}'
              className="font-mono text-sm resize-y min-h-[100px]"
            />
          </div>
          
          <div className="md:col-span-2">
            <Label className="mb-2">Coach Message Content</Label>
            <Textarea
              value={draft.coach_message_content || ""}
              onChange={e => setDraft(d => ({ ...d, coach_message_content: e.target.value }))}
              placeholder="Content of the coach message that triggered this action"
              className="resize-y min-h-[180px]"
            />
          </div>
        </div>
        
        {error && <div className="text-red-600 mt-2">{error}</div>}
        
        <div className="flex gap-2 mt-4">
          <Button type="button" variant="default" onClick={handleSave}>
            {editingIndex !== null ? "Save Changes" : "Add Action"}
          </Button>
          {editingIndex !== null && (
            <Button type="button" variant="secondary" onClick={handleCancel}>
              Cancel
            </Button>
          )}
        </div>
      </div>
    </div>
  );
} 