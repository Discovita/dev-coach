import { useState, useRef, useCallback } from "react";
import { TestScenarioIdentity } from "@/types/testScenario";
import { IdentityCategory } from "@/enums/identityCategory";
import { IdentityState } from "@/enums/identityState";
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
  onImageFilesChange?: (files: Map<number, File>) => void;
}

const emptyIdentity = (): TestScenarioIdentity => ({
  name: "",
  category: IdentityCategory.PASSIONS_AND_TALENTS,
  state: IdentityState.PROPOSED,
  i_am_statement: "",
  visualization: "",
  notes: [],
});

export default function TestScenarioIdentitiesForm({
  value,
  onChange,
  onImageFilesChange,
}: TestScenarioIdentitiesFormProps) {
  const [editingIndex, setEditingIndex] = useState<number | null>(null);
  const [draft, setDraft] = useState<TestScenarioIdentity>(emptyIdentity());
  const [error, setError] = useState<string | null>(null);
  const [noteInput, setNoteInput] = useState("");
  const [imageFiles, setImageFiles] = useState<Map<number, File>>(new Map());
  const [selectedImageFile, setSelectedImageFile] = useState<File | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleEdit = (idx: number) => {
    setEditingIndex(idx);
    setDraft({ ...value[idx] });
    setError(null);
    // Set selected image file if one exists for this identity
    setSelectedImageFile(imageFiles.get(idx) || null);
  };

  const handleDelete = (idx: number) => {
    const updated = value.filter((_, i) => i !== idx);
    onChange(updated);
    // Remove image file for deleted identity and reindex remaining files
    if (imageFiles.has(idx)) {
      const newImageFiles = new Map<number, File>();
      imageFiles.forEach((file, index) => {
        if (index < idx) {
          // Keep files before deleted index
          newImageFiles.set(index, file);
        } else if (index > idx) {
          // Shift files after deleted index down by 1
          newImageFiles.set(index - 1, file);
        }
        // Skip the deleted index
      });
      setImageFiles(newImageFiles);
      onImageFilesChange?.(newImageFiles);
    }
    if (editingIndex === idx) {
      setEditingIndex(null);
      setDraft(emptyIdentity());
      setSelectedImageFile(null);
    } else if (editingIndex !== null && editingIndex > idx) {
      // Adjust editing index if it's after the deleted one
      setEditingIndex(editingIndex - 1);
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
      // Preserve existing image URL if no new file is selected
      // If a new file is selected, the backend will replace it with the new URL
      const updatedDraft = { ...draft };
      // Don't clear the image URL - let the backend handle it when a new file is uploaded
      const updated = value.map((id, i) =>
        i === editingIndex ? updatedDraft : id
      );
      console.log("Updated identities (edit):", updated);
      onChange(updated);
      // Update image files map if a file was selected
      if (selectedImageFile) {
        const newImageFiles = new Map(imageFiles);
        newImageFiles.set(editingIndex, selectedImageFile);
        setImageFiles(newImageFiles);
        onImageFilesChange?.(newImageFiles);
      } else {
        // If no new file selected but image was deleted, remove from map
        if (!draft.image && imageFiles.has(editingIndex)) {
          const newImageFiles = new Map(imageFiles);
          newImageFiles.delete(editingIndex);
          setImageFiles(newImageFiles);
          onImageFilesChange?.(newImageFiles);
        }
      }
      setEditingIndex(null);
      setDraft(emptyIdentity());
      setSelectedImageFile(null);
    } else {
      // For new identities, preserve image URL if set
      const updatedDraft = { ...draft };
      const updated = [...value, updatedDraft];
      console.log("Updated identities (add):", updated);
      onChange(updated);
      // Update image files map if a file was selected
      if (selectedImageFile) {
        const newImageFiles = new Map(imageFiles);
        newImageFiles.set(updated.length - 1, selectedImageFile);
        setImageFiles(newImageFiles);
        onImageFilesChange?.(newImageFiles);
      }
      setDraft(emptyIdentity());
      setSelectedImageFile(null);
    }
  };

  const handleCancel = () => {
    setEditingIndex(null);
    setDraft(emptyIdentity());
    setError(null);
    setSelectedImageFile(null);
  };

  const handleFileSelect = (file: File) => {
    // Validate file type
    if (!file.type.startsWith("image/")) {
      setError("Please select an image file.");
      return;
    }
    // Validate file size (max 10MB)
    if (file.size > 10 * 1024 * 1024) {
      setError("Image file size must be less than 10MB.");
      return;
    }
    setError(null);
    setSelectedImageFile(file);
    // Don't clear draft.image here - it will be replaced by backend when file is uploaded
    // The selected file preview will show, and the existing image URL will remain until backend updates it
  };

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      handleFileSelect(file);
    }
  };

  const handleDrop = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    const file = e.dataTransfer.files[0];
    if (file) {
      handleFileSelect(file);
    }
  }, []);

  const handleDragOver = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
  }, []);

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
                {identity.state && (
                  <span className="ml-2 text-xs text-neutral-500">
                    ({identity.state})
                  </span>
                )}
                {identity.i_am_statement && (
                  <>
                    <span className="font-semibold ml-2 text-xs italic text-gold-700">
                      I Am Statement:
                    </span>
                    <span className="ml-2 text-xs italic text-gold-700">
                      {identity.i_am_statement}
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
                {identity.image && (
                  <div className="mt-2">
                    <div className="text-xs text-neutral-500 mb-1">
                      Image URL: <span className="font-mono text-xs break-all">{identity.image}</span>
                    </div>
                    <img
                      src={identity.image}
                      alt={identity.name}
                      className="max-w-[200px] max-h-[200px] object-contain border rounded"
                      onError={(e) => {
                        (e.target as HTMLImageElement).style.display = "none";
                      }}
                    />
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
          {editingIndex !== null ? "Edit Identity" : "Add Identity"}
        </h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <Label className="mb-2">Name</Label>
            <Input
              value={draft.name}
              onChange={(e) => setDraft({ ...draft, name: e.target.value })}
              placeholder="e.g. Creative Visionary"
            />
          </div>
          <div>
            <Label className="mb-2">Category</Label>
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
            <Label className="mb-2">State</Label>
            <Select
              value={draft.state}
              onValueChange={(v) =>
                setDraft({ ...draft, state: v as IdentityState })
              }
            >
              <SelectTrigger className="w-full mt-1">
                <SelectValue placeholder="Select state" />
              </SelectTrigger>
              <SelectContent>
                {Object.values(IdentityState).map((st) => (
                  <SelectItem key={st} value={st}>
                    {st.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase())}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div>
            <Label className="mb-2">I Am Statement</Label>
            <Input
              value={draft.i_am_statement || ""}
              onChange={(e) =>
                setDraft({ ...draft, i_am_statement: e.target.value })
              }
              placeholder="e.g. I am curious and open to new ideas."
            />
          </div>
          <div>
            <Label className="mb-2">Visualization</Label>
            <Input
              value={draft.visualization || ""}
              onChange={(e) =>
                setDraft({ ...draft, visualization: e.target.value })
              }
              placeholder="e.g. Standing on a mountain, seeing the horizon."
            />
          </div>
          <div className="md:col-span-2">
            <Label>Image</Label>
            <div className="mb-2">
              <div className="flex items-center justify-between mb-1">
                <div className="text-xs text-neutral-500">
                  Current Image URL:{" "}
                  {draft.image ? (
                    <span className="font-mono text-xs break-all">{draft.image}</span>
                  ) : (
                    <span className="text-neutral-400 italic">No image URL set</span>
                  )}
                </div>
                {draft.image && (
                  <Button
                    type="button"
                    size="xs"
                    variant="destructive"
                    onClick={() => {
                      setDraft({ ...draft, image: undefined });
                      setError(null);
                    }}
                  >
                    Delete Image
                  </Button>
                )}
              </div>
              {draft.image ? (
                <img
                  src={draft.image}
                  alt={draft.name || "Identity"}
                  className="max-w-[200px] max-h-[200px] object-contain border rounded mb-2"
                  onError={(e) => {
                    (e.target as HTMLImageElement).style.display = "none";
                  }}
                />
              ) : (
                <div className="max-w-[200px] max-h-[200px] border rounded mb-2 flex items-center justify-center bg-neutral-50 text-neutral-400 text-xs p-4">
                  No image preview available
                </div>
              )}
            </div>
            {selectedImageFile && (
              <div className="mb-2">
                <div className="text-xs text-green-600 mb-1">
                  Selected file: {selectedImageFile.name} ({(selectedImageFile.size / 1024).toFixed(2)} KB)
                </div>
                <img
                  src={URL.createObjectURL(selectedImageFile)}
                  alt="Preview"
                  className="max-w-[200px] max-h-[200px] object-contain border rounded mb-2"
                />
                <Button
                  type="button"
                  size="xs"
                  variant="ghost"
                  onClick={() => {
                    setSelectedImageFile(null);
                    if (fileInputRef.current) {
                      fileInputRef.current.value = "";
                    }
                    // Clear the image file from the map if it was set
                    if (editingIndex !== null && imageFiles.has(editingIndex)) {
                      const newImageFiles = new Map(imageFiles);
                      newImageFiles.delete(editingIndex);
                      setImageFiles(newImageFiles);
                      onImageFilesChange?.(newImageFiles);
                    }
                  }}
                >
                  Remove
                </Button>
              </div>
            )}
            <div
              className="border-2 border-dashed border-neutral-300 rounded p-4 text-center cursor-pointer hover:border-gold-500 transition-colors"
              onDrop={handleDrop}
              onDragOver={handleDragOver}
              onClick={() => fileInputRef.current?.click()}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                onChange={handleFileInputChange}
                className="hidden"
              />
              <div className="text-sm text-neutral-600">
                {selectedImageFile
                  ? "Click to change image"
                  : "Drag and drop an image here, or click to browse"}
              </div>
              <div className="text-xs text-neutral-400 mt-1">
                Supports: JPEG, PNG, GIF, WebP (max 10MB)
              </div>
            </div>
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
