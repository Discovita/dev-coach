import { useRef, useState } from "react";
import { TestScenarioUserNote } from "@/types/testScenario";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

interface Props {
  value: TestScenarioUserNote[];
  onChange: (notes: TestScenarioUserNote[]) => void;
}

export default function TestScenarioUserNotesForm({ value, onChange }: Props) {
  const parentRef = useRef<HTMLDivElement>(null);
  const [draft, setDraft] = useState<TestScenarioUserNote>({ note: "" });
  const [editingIndex, setEditingIndex] = useState<number | null>(null);

  const handleSave = () => {
    if (!draft.note.trim()) return;
    if (editingIndex !== null) {
      const updated = value.map((n, i) => (i === editingIndex ? draft : n));
      onChange(updated);
      setEditingIndex(null);
    } else {
      onChange([...value, draft]);
    }
    setDraft({ note: "" });
  };

  const handleEdit = (idx: number) => {
    setEditingIndex(idx);
    setDraft(value[idx]);
  };

  const handleDelete = (idx: number) => {
    onChange(value.filter((_, i) => i !== idx));
    if (editingIndex === idx) {
      setEditingIndex(null);
      setDraft({ note: "" });
    }
  };

  return (
    <div className="flex flex-col gap-4">
      <div className="flex gap-2 mb-2 items-end">
        <div className="flex-1">
          <Label className="mb-2">User Note</Label>
          <Input
            value={draft.note}
            onChange={e => setDraft(d => ({ ...d, note: e.target.value }))}
            placeholder="Enter a user note"
            onKeyDown={e => { if (e.key === "Enter") handleSave(); }}
          />
        </div>
        <Button type="button" onClick={handleSave}>
          {editingIndex !== null ? "Save" : "Add"}
        </Button>
      </div>
      <div
        ref={parentRef}
        className="overflow-auto border border-[#eee] rounded-lg bg-white"
        style={{ height: 500, width: "100%" }}
      >
        {value.map((note, idx) => (
          <div
            key={idx}
            className={[
              "flex items-center gap-2 border-b border-[#f3f3f3] px-4 py-3 min-h-[48px] box-border w-full",
              idx % 2 === 0 ? "bg-[#fafbfc]" : "bg-white"
            ].join(" ")}
          >
            <span className="flex-1 whitespace-pre-wrap break-words leading-[1.5] py-0.5">{note.note}</span>
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