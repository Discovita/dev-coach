import { useRef, useState } from "react";
import { TestScenarioChatMessage } from "@/types/testScenario";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectTrigger, SelectContent, SelectItem, SelectValue } from "@/components/ui/select";

interface Props {
  value: TestScenarioChatMessage[];
  onChange: (messages: TestScenarioChatMessage[]) => void;
}

const roles = ["user", "coach"];

/**
 * TestScenarioChatMessagesForm Visual Logic
 * -----------------------------------------
 * - Each message row has extra vertical padding and minHeight to prevent content from being cut off.
 * - Coach messages have a light gold background and a left border for emphasis.
 * - User messages have a white background and no border.
 * - Both message types use box-sizing: border-box to ensure padding is included in height calculations.
 */
export default function TestScenarioChatMessagesForm({ value, onChange }: Props) {
  const parentRef = useRef<HTMLDivElement>(null);
  const [draft, setDraft] = useState<TestScenarioChatMessage>({ role: "user", content: "" });
  const [editingIndex, setEditingIndex] = useState<number | null>(null);

  const handleSave = () => {
    if (!draft.content.trim()) return;
    if (editingIndex !== null) {
      const updated = value.map((msg, i) => (i === editingIndex ? draft : msg));
      onChange(updated);
      setEditingIndex(null);
    } else {
      onChange([...value, draft]);
    }
    setDraft({ role: "user", content: "" });
  };

  const handleEdit = (idx: number) => {
    setEditingIndex(idx);
    setDraft(value[idx]);
  };

  const handleDelete = (idx: number) => {
    onChange(value.filter((_, i) => i !== idx));
    if (editingIndex === idx) {
      setEditingIndex(null);
      setDraft({ role: "user", content: "" });
    }
  };

  return (
    <div className="_TestScenarioChatMessagesForm flex flex-col gap-4">
      <div>
        <div className="flex gap-2 mb-2">
          <Select value={draft.role} onValueChange={role => setDraft(d => ({ ...d, role }))}>
            <SelectTrigger className="w-24">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {roles.map(r => (
                <SelectItem key={r} value={r}>{r}</SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Input
            value={draft.content}
            onChange={e => setDraft(d => ({ ...d, content: e.target.value }))}
            placeholder="Message content"
            className="flex-1"
            onKeyDown={e => { if (e.key === "Enter") handleSave(); }}
          />
          <Button type="button" onClick={handleSave} className="shrink-0">
            {editingIndex !== null ? "Save" : "Add"}
          </Button>
        </div>
      </div>
      <div
        ref={parentRef}
        className="overflow-auto border border-[#eee] rounded-lg bg-white"
        style={{ height: 500, width: "100%" }}
      >
        {value.map((msg, idx) => (
          <div
            key={idx}
            className={[
              "flex items-start gap-2 border-b border-[#f3f3f3] px-4 py-3 min-h-[48px] box-border w-full",
              msg.role === "coach"
                ? "bg-[#fffbe6] border-l-4 border-l-[#eab308]"
                : "bg-white border-l-4 border-l-transparent"
            ].join(" ")}
          >
            <span
              className={[
                "font-mono text-xs w-12 mt-1",
                msg.role === "coach" ? "text-[#b45309] font-bold" : "text-neutral-500 font-normal"
              ].join(" ")}
            >
              {msg.role}
            </span>
            <div
              className="flex-1 whitespace-pre-wrap break-words leading-[1.5] py-0.5"
            >
              {msg.content}
            </div>
            <Button type="button" size="xs" variant="secondary" onClick={() => handleEdit(idx)} className="ml-2">
              Edit
            </Button>
            <Button type="button" size="xs" variant="destructive" onClick={() => handleDelete(idx)} className="ml-1">
              Delete
            </Button>
          </div>
        ))}
      </div>
    </div>
  );
} 