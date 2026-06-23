import { useState } from "react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { NameFields, type NameValue } from "./NameFields";
import type { User } from "@/types/user";

/**
 * AccountInformation Component
 * ----------------------------
 * Displays user account information (email, name, member since).
 * Receives profile data as a prop from the parent Account page,
 * which handles impersonation-aware data fetching.
 *
 * When an `onSave` callback is provided the Name field becomes editable
 * (the parent owns persistence). It is omitted while impersonating, leaving
 * the card read-only.
 *
 * Used in: Account page.
 */
export function AccountInformation({
  profile,
  onSave,
}: {
  profile: User | null;
  onSave?: (updates: NameValue) => Promise<void>;
}) {
  const [isEditing, setIsEditing] = useState(false);
  const [draft, setDraft] = useState<NameValue>({ first_name: "", last_name: "" });
  const [isSaving, setIsSaving] = useState(false);

  if (!profile) {
    return (
      <div className="bg-card rounded-lg border p-6">
        <h2 className="text-xl font-medium mb-4">Account Information</h2>
        <div className="text-muted-foreground">Loading...</div>
      </div>
    );
  }

  const fullName =
    [profile.first_name, profile.last_name].filter(Boolean).join(" ") || null;

  const startEditing = () => {
    setDraft({
      first_name: profile.first_name ?? "",
      last_name: profile.last_name ?? "",
    });
    setIsEditing(true);
  };

  const handleSave = async () => {
    if (!onSave) return;
    setIsSaving(true);
    try {
      await onSave({
        first_name: draft.first_name.trim(),
        last_name: draft.last_name.trim(),
      });
      toast.success("Name updated");
      setIsEditing(false);
    } catch (error) {
      const message =
        error instanceof Error ? error.message : "Failed to update name";
      toast.error(message);
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="bg-card rounded-lg border p-6 space-y-4">
      <h2 className="text-xl font-medium mb-4">Account Information</h2>

      <div className="space-y-3">
        <div>
          <label className="text-sm font-medium text-muted-foreground">Email</label>
          <p className="text-base mt-1">{profile.email || "Not available"}</p>
        </div>

        <div>
          <label className="text-sm font-medium text-muted-foreground">Name</label>
          {isEditing ? (
            <div className="mt-2 space-y-4">
              <NameFields value={draft} onChange={setDraft} disabled={isSaving} />
              <div className="flex items-center gap-3">
                <Button
                  type="button"
                  onClick={handleSave}
                  disabled={isSaving}
                  className="nv-gradient-button text-white"
                >
                  {isSaving ? "Saving..." : "Save"}
                </Button>
                <Button
                  type="button"
                  variant="ghost"
                  onClick={() => setIsEditing(false)}
                  disabled={isSaving}
                >
                  Cancel
                </Button>
              </div>
            </div>
          ) : (
            <div className="mt-1 flex items-center justify-between gap-3">
              <p className="text-base">{fullName || "Not set"}</p>
              {onSave && (
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={startEditing}
                >
                  Edit
                </Button>
              )}
            </div>
          )}
        </div>

        {profile.created_at && (
          <div>
            <label className="text-sm font-medium text-muted-foreground">Member since</label>
            <p className="text-base mt-1">
              {new Date(profile.created_at).toLocaleDateString("en-US", {
                year: "numeric",
                month: "long",
                day: "numeric",
              })}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
