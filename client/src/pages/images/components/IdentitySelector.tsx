import { useProfile } from "@/hooks/use-profile";
import { useIdentities } from "@/hooks/use-identities";
import { useTestScenarioUserIdentities } from "@/hooks/test-scenario/use-test-scenario-user-identities";
import {
  Select,
  SelectTrigger,
  SelectValue,
  SelectContent,
  SelectItem,
  SelectGroup,
  SelectLabel,
} from "@/components/ui/select";
import { Identity } from "@/types/identity";

interface IdentitySelectorProps {
  selectedUserId: string | null;
  selectedIdentityId: string | null;
  onIdentitySelect: (identityId: string | null) => void;
}

/**
 * IdentitySelector Component
 * --------------------------
 * Allows selecting an identity from the selected user's identities.
 * Handles both current user and test user identities.
 */
export function IdentitySelector({
  selectedUserId,
  selectedIdentityId,
  onIdentitySelect,
}: IdentitySelectorProps) {
  const { profile } = useProfile();
  const isCurrentUser = profile && selectedUserId === profile.id;

  // Fetch identities based on user type
  const {
    identities: currentUserIdentities,
    isLoading: isLoadingCurrent,
  } = useIdentities();

  const {
    identities: testUserIdentities,
    isLoading: isLoadingTest,
  } = useTestScenarioUserIdentities(selectedUserId || "");

  const identities = isCurrentUser ? currentUserIdentities : testUserIdentities;
  const isLoading = isCurrentUser ? isLoadingCurrent : isLoadingTest;

  const handleValueChange = (value: string) => {
    if (value === "none") {
      onIdentitySelect(null);
    } else {
      onIdentitySelect(value);
    }
  };

  if (!selectedUserId) {
    return null;
  }

  if (isLoading) {
    return (
      <div className="text-neutral-500">Loading identities...</div>
    );
  }

  if (!identities || identities.length === 0) {
    return (
      <div className="text-neutral-500">
        No identities found for this user. Create identities first.
      </div>
    );
  }

  const selectedIdentity = identities.find(
    (id: Identity) => id.id === selectedIdentityId
  );

  return (
    <div className="flex flex-col gap-2">
      <label className="text-sm font-medium">Select Identity</label>
      <Select
        value={selectedIdentityId || "none"}
        onValueChange={handleValueChange}
      >
        <SelectTrigger className="w-full max-w-2xl h-12 text-base">
          <SelectValue placeholder="Choose an identity">
            {selectedIdentity
              ? `${selectedIdentity.name}${selectedIdentity.category ? ` (${selectedIdentity.category})` : ""}`
              : "Choose an identity"}
          </SelectValue>
        </SelectTrigger>
        <SelectContent>
          <SelectGroup>
            <SelectLabel>Identities</SelectLabel>
            <SelectItem value="none">None (Select an identity)</SelectItem>
            {identities.map((identity: Identity) => (
              <SelectItem key={identity.id} value={identity.id || ""}>
                {identity.name}
                {identity.category && ` (${identity.category})`}
              </SelectItem>
            ))}
          </SelectGroup>
        </SelectContent>
      </Select>

      {selectedIdentity && (
        <div className="mt-2 p-4 bg-neutral-50 dark:bg-neutral-900 rounded-lg border border-neutral-200 dark:border-neutral-800">
          <h3 className="font-semibold text-sm mb-2">{selectedIdentity.name}</h3>
          {selectedIdentity.i_am_statement && (
            <p className="text-sm text-neutral-600 dark:text-neutral-400 mb-2">
              <span className="font-medium">I Am:</span> {selectedIdentity.i_am_statement}
            </p>
          )}
          {selectedIdentity.visualization && (
            <p className="text-sm text-neutral-600 dark:text-neutral-400">
              <span className="font-medium">Visualization:</span> {selectedIdentity.visualization}
            </p>
          )}
        </div>
      )}
    </div>
  );
}

