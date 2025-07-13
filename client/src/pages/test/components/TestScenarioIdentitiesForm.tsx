import { useState } from "react";
import { TestScenarioIdentity } from "@/types/testScenario";
import { IdentityCategory } from "@/enums/identityCategory";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectTrigger,
  SelectContent,
  SelectItem,
  SelectValue,
} from "@/components/ui/select";

interface TestScenarioIdentitiesFormProps {
  value: TestScenarioIdentity[];
  onChange: (identities: TestScenarioIdentity[]) => void;
}

const emptyIdentity = (): TestScenarioIdentity => ({
  name: "",
  category: IdentityCategory.PASSIONS_AND_TALENTS,
  affirmation: "",
  visualization: "",
  notes: [],
});

export default function TestScenarioIdentitiesForm({
  value,
  onChange,
}: TestScenarioIdentitiesFormProps) {
  const [editingIndex, setEditingIndex] = useState<number | null>(null);
  const [draft, setDraft] = useState<TestScenarioIdentity>(emptyIdentity());
  const [error, setError] = useState<string | null>(null);
  const [noteInput, setNoteInput] = useState("");

  const handleEdit = (idx: number) => {
    setEditingIndex(idx);
    setDraft({ ...value[idx] });
    setError(null);
  };

  const handleDelete = (idx: number) => {
    const updated = value.filter((_, i) => i !== idx);
    onChange(updated);
    if (editingIndex === idx) {
      setEditingIndex(null);
      setDraft(emptyIdentity());
    }
  };

  const handleSave = () => {
    if (!draft.name.trim()) {
      setError("Name is required.");
      return;
    }
    if (!draft.category) {
      setError("Category is required.");
      return;
    }
    setError(null);
    if (editingIndex !== null) {
      const updated = value.map((id, i) =>
        i === editingIndex ? { ...draft } : id
      );
      console.log("Updated identities (edit):", updated);
      onChange(updated);
      setEditingIndex(null);
      setDraft(emptyIdentity());
    } else {
      const updated = [...value, { ...draft }];
      console.log("Updated identities (add):", updated);
      onChange(updated);
      setDraft(emptyIdentity());
    }
  };

  const handleCancel = () => {
    setEditingIndex(null);
    setDraft(emptyIdentity());
    setError(null);
  };

  // Notes handling
  const handleAddNote = (note: string) => {
    setDraft({ ...draft, notes: [...(draft.notes || []), note] });
  };
  const handleDeleteNote = (idx: number) => {
    setDraft({
      ...draft,
      notes: (draft.notes || []).filter((_, i) => i !== idx),
    });
  };

  return (
    <div className="flex flex-col gap-6 mt-4">
      <div>
        <h3 className="font-semibold mb-2">Identities</h3>
        {value.length === 0 && (
          <div className="text-neutral-400 mb-2">No identities added yet.</div>
        )}
        <ul className="divide-y divide-neutral-200 mb-4">
          {value.map((identity, idx) => (
            <li
              key={idx}
              className="py-2 flex flex-col md:flex-row md:items-center gap-2"
            >
              <div className="flex-1">
                <span className="font-medium">{identity.name}</span>
                <span className="ml-2 text-xs text-neutral-500">
                  [{identity.category}]
                </span>
                {identity.affirmation && (
                  <>
                    <span className="font-semibold ml-2 text-xs italic text-gold-700">
                      Affirmation:
                    </span>
                    <span className="ml-2 text-xs italic text-gold-700">
                      {identity.affirmation}
                    </span>
                  </>
                )}
                {identity.visualization && (
                  <>
                    <span className="font-semibold ml-2 text-xs italic text-gold-700">
                      Visualization:
                    </span>
                    <span className="ml-2 text-xs italic text-gold-700">
                      {identity.visualization}
                    </span>
                  </>
                )}
                {identity.notes && identity.notes.length > 0 && (
                  <span className="ml-2 text-xs text-neutral-500">
                    Notes: {identity.notes.join(", ")}
                  </span>
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
          {editingIndex !== null ? "Edit Identity" : "Add Identity"}
        </h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <Label>Name</Label>
            <Input
              value={draft.name}
              onChange={(e) => setDraft({ ...draft, name: e.target.value })}
              placeholder="e.g. Creative Visionary"
            />
          </div>
          <div>
            <Label>Category</Label>
            <Select
              value={draft.category}
              onValueChange={(v) =>
                setDraft({ ...draft, category: v as IdentityCategory })
              }
            >
              <SelectTrigger className="w-full mt-1">
                <SelectValue placeholder="Select category" />
              </SelectTrigger>
              <SelectContent>
                {Object.values(IdentityCategory).map((cat) => (
                  <SelectItem key={cat} value={cat}>
                    {cat
                      .replace(/_/g, " ")
                      .replace(/\b\w/g, (c) => c.toUpperCase())}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div>
            <Label>Affirmation</Label>
            <Input
              value={draft.affirmation || ""}
              onChange={(e) =>
                setDraft({ ...draft, affirmation: e.target.value })
              }
              placeholder="e.g. I am curious and open to new ideas."
            />
          </div>
          <div>
            <Label>Visualization</Label>
            <Input
              value={draft.visualization || ""}
              onChange={(e) =>
                setDraft({ ...draft, visualization: e.target.value })
              }
              placeholder="e.g. Standing on a mountain, seeing the horizon."
            />
          </div>
          <div className="md:col-span-2">
            <Label>Notes</Label>
            <div className="flex flex-wrap gap-2 mb-2">
              {(draft.notes || []).map((note, idx) => (
                <span
                  key={idx}
                  className="inline-flex items-center bg-gold-100 text-gold-900 rounded px-2 py-1 text-xs"
                >
                  {note}
                  <Button
                    type="button"
                    size="xs"
                    variant="ghost"
                    className="ml-1 px-1"
                    onClick={() => handleDeleteNote(idx)}
                  >
                    ×
                  </Button>
                </span>
              ))}
            </div>
            <div className="flex gap-2">
              <Input
                value={noteInput}
                onChange={(e) => setNoteInput(e.target.value)}
                placeholder="Type a note and press Enter"
                onKeyDown={(e) => {
                  if (e.key === "Enter" && noteInput.trim()) {
                    handleAddNote(noteInput.trim());
                    setNoteInput("");
                    e.preventDefault();
                  }
                }}
                className="flex-1"
              />
            </div>
          </div>
        </div>
        {error && <div className="text-red-600 mt-2">{error}</div>}
        <div className="flex gap-2 mt-4">
          <Button type="button" variant="default" onClick={handleSave}>
            {editingIndex !== null ? "Save Changes" : "Add Identity"}
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
