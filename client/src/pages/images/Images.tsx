import { useState, useEffect } from "react";
import { UserSelector } from "./components/UserSelector";
import { useProfile } from "@/hooks/use-profile";

/**
 * Images Page
 * -----------
 * Admin-only page for generating identity images.
 * Allows admins to:
 * 1. Select a user (self or test account)
 * 2. Manage reference images for that user
 * 3. Select an identity
 * 4. Generate and save identity images
 */
export default function Images() {
  const { profile } = useProfile();
  const [selectedUserId, setSelectedUserId] = useState<string | null>(null);

  // Set profile as default when it loads
  useEffect(() => {
    if (profile && !selectedUserId) {
      setSelectedUserId(profile.id);
    }
  }, [profile, selectedUserId]);

  return (
    <div className="flex flex-col h-full w-full p-6">
      <h1 className="text-3xl font-bold mb-6">Identity Image Generation</h1>
      
      <div className="mb-6">
        <UserSelector
          selectedUserId={selectedUserId}
          onUserSelect={setSelectedUserId}
        />
      </div>

      {selectedUserId && (
        <div className="flex-1 min-h-0">
          {/* Reference Image Manager will go here */}
          {/* Identity Selection & Generation will go here */}
        </div>
      )}

      {!selectedUserId && (
        <div className="flex-1 flex items-center justify-center text-neutral-500">
          Select a user to begin generating identity images
        </div>
      )}
    </div>
  );
}

