import { useProfile } from "@/hooks/use-profile";
import { useTestScenarios } from "@/hooks/test-scenario/use-test-scenarios";
import {
  Select,
  SelectTrigger,
  SelectValue,
  SelectContent,
  SelectItem,
  SelectGroup,
  SelectLabel,
} from "@/components/ui/select";

interface UserOption {
  id: string;
  label: string;
  isCurrentUser: boolean;
  isTestUser: boolean;
}

interface UserSelectorProps {
  selectedUserId: string | null;
  onUserSelect: (userId: string | null) => void;
}

/**
 * UserSelector Component
 * ----------------------
 * Allows admin to select between their own account or any test account.
 * Displays current user and all test scenario users.
 */
export function UserSelector({ selectedUserId, onUserSelect }: UserSelectorProps) {
  const { profile } = useProfile();
  const { data: testScenarios, isLoading: scenariosLoading } = useTestScenarios();

  // Build user options list
  const userOptions: UserOption[] = [];

  // Add current user first
  if (profile) {
    const userName = `${profile.first_name || ""} ${profile.last_name || ""}`.trim() || profile.email || "Current User";
    userOptions.push({
      id: profile.id,
      label: `${userName} (This Account)`,
      isCurrentUser: true,
      isTestUser: false,
    });
  }

  // Add test scenario users
  if (testScenarios) {
    testScenarios.forEach((scenario) => {
      if (scenario.template?.user?.id) {
        const user = scenario.template.user;
        const userName = scenario.name || `${user.first_name || ""} ${user.last_name || ""}`.trim() || user.email || "Test User";
        userOptions.push({
          id: String(user.id),
          label: `${userName} (Test)`,
          isCurrentUser: false,
          isTestUser: true,
        });
      }
    });
  }

  const handleValueChange = (value: string) => {
    if (value === "none") {
      onUserSelect(null);
    } else {
      onUserSelect(value);
    }
  };

  if (scenariosLoading) {
    return (
      <div className="text-neutral-500">Loading users...</div>
    );
  }

  return (
    <div className="flex flex-col gap-2">
      <label className="text-sm font-medium">Select User</label>
      <Select
        value={selectedUserId || "none"}
        onValueChange={handleValueChange}
      >
        <SelectTrigger className="w-full max-w-2xl h-12 text-base">
          <SelectValue placeholder="Choose a user" />
        </SelectTrigger>
        <SelectContent>
          <SelectGroup>
            <SelectLabel>Users</SelectLabel>
            <SelectItem value="none">None (Select a user)</SelectItem>
            {userOptions.map((user) => (
              <SelectItem key={user.id} value={user.id}>
                {user.label}
              </SelectItem>
            ))}
          </SelectGroup>
        </SelectContent>
      </Select>
    </div>
  );
}

