import { useRef, useState } from "react";
import { useVirtualizer } from "@tanstack/react-virtual";
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

  const rowVirtualizer = useVirtualizer({
    count: value.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 48,
    overscan: 10,
  });

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
        style={{
          height: 240,
          width: "100%",
          overflow: "auto",
          border: "1px solid #eee",
          borderRadius: 6,
        }}
      >
        <div
          style={{
            height: `${rowVirtualizer.getTotalSize()}px`,
            position: "relative",
          }}
        >
          {rowVirtualizer.getVirtualItems().map(virtualRow => {
            const note = value[virtualRow.index];
            return (
              <div
                key={virtualRow.key}
                style={{
                  position: "absolute",
                  top: 0,
                  left: 0,
                  width: "100%",
                  transform: `translateY(${virtualRow.start}px)`,
                  display: "flex",
                  alignItems: "center",
                  gap: 8,
                  borderBottom: "1px solid #f3f3f3",
                  padding: "4px 8px",
                  background: virtualRow.index % 2 === 0 ? "#fafbfc" : "#fff",
                }}
              >
                <span className="flex-1">{note.note}</span>
                <Button type="button" size="xs" variant="secondary" onClick={() => handleEdit(virtualRow.index)}>
                  Edit
                </Button>
                <Button type="button" size="xs" variant="destructive" onClick={() => handleDelete(virtualRow.index)}>
                  Delete
                </Button>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
} 