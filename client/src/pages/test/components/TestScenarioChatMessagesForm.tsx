import { useRef, useState } from "react";
import { useVirtualizer } from "@tanstack/react-virtual";
import { TestScenarioChatMessage } from "@/types/testScenario";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectTrigger, SelectContent, SelectItem, SelectValue } from "@/components/ui/select";

interface Props {
  value: TestScenarioChatMessage[];
  onChange: (messages: TestScenarioChatMessage[]) => void;
}

const roles = ["user", "coach"];

export default function TestScenarioChatMessagesForm({ value, onChange }: Props) {
  const parentRef = useRef<HTMLDivElement>(null);
  const [draft, setDraft] = useState<TestScenarioChatMessage>({ role: "user", content: "" });
  const [editingIndex, setEditingIndex] = useState<number | null>(null);

  const rowVirtualizer = useVirtualizer({
    count: value.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 48,
    overscan: 10,
  });

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
    <div className="flex flex-col gap-4">
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
          <Button type="button" onClick={handleSave}>
            {editingIndex !== null ? "Save" : "Add"}
          </Button>
        </div>
      </div>
      <div
        ref={parentRef}
        style={{
          height: 320,
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
            const msg = value[virtualRow.index];
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
                <span className="font-mono text-xs text-neutral-500 w-12">{msg.role}</span>
                <span className="flex-1">{msg.content}</span>
                <Button size="xs" variant="secondary" onClick={() => handleEdit(virtualRow.index)}>Edit</Button>
                <Button size="xs" variant="destructive" onClick={() => handleDelete(virtualRow.index)}>Delete</Button>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
} 