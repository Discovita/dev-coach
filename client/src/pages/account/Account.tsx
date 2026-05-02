import { useAuth } from "@/hooks/use-auth";
import { useProfile } from "@/hooks/use-profile";
import { useUserAppearance } from "@/hooks/use-user-appearance";
import { useImpersonation } from "@/context/ImpersonationContext";
import { useQuery } from "@tanstack/react-query";
import { fetchTestScenarioUserProfile } from "@/api/testScenarioUser";
import { Button } from "@/components/ui/button";
import { AccountInformation } from "./components/AccountInformation";
import { ReferenceImageManager } from "./components/ReferenceImageManager";
import { AppearanceSelector } from "./components/appearance";
import { toast } from "sonner";
import type { UserAppearance } from "@/types/userAppearance";
import type { User } from "@/types/user";

/**
 * Account Page
 * 
 * Purpose:
 * - Displays user account information (email, name, etc.)
 * - Manages reference photos for AI image generation
 * - Configures appearance preferences for identity images
 * - Provides a logout button to allow users to sign out
 * 
 * Impersonation-aware: when an admin is viewing as another user,
 * all sections show the impersonated user's data. The logout button
 * is hidden during impersonation.
 */
export default function Account() {
  const { logout, logoutStatus } = useAuth();
  const { profile } = useProfile();
  const { impersonatedUser } = useImpersonation();
  const isImpersonating = !!impersonatedUser;

  const { data: impersonatedProfile } = useQuery<User>({
    queryKey: ["testScenarioUser", impersonatedUser?.id, "profile"],
    queryFn: () => fetchTestScenarioUserProfile(impersonatedUser!.id),
    enabled: isImpersonating,
    staleTime: 1000 * 60 * 5,
  });

  const viewedUserId = isImpersonating
    ? impersonatedUser?.id ?? null
    : profile?.id ?? null;

  const viewedProfile = isImpersonating ? impersonatedProfile : profile;

  const { appearance, updateAppearance, isUpdating } = useUserAppearance(viewedUserId);

  const handleLogout = async () => {
    try {
      await logout();
    } catch (error) {
      console.error("Logout failed:", error);
    }
  };

  const handleAppearanceSave = async (newAppearance: UserAppearance) => {
    try {
      await updateAppearance(newAppearance);
      toast.success("Appearance preferences saved");
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : "Failed to save preferences";
      toast.error(errorMessage);
      throw error;
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-3xl font-semibold mb-6">Account</h1>

      <div className="space-y-6">
        {/* Account Information */}
        <AccountInformation profile={viewedProfile ?? null} />

        {/* Reference Photos Section */}
        <ReferenceImageManager userId={isImpersonating ? viewedUserId ?? undefined : undefined} />

        {/* Appearance Preferences Section */}
        <AppearanceSelector
          appearance={appearance}
          onSave={handleAppearanceSave}
          isSaving={isUpdating}
        />

        {/* Logout Section — hidden when impersonating */}
        {!isImpersonating && (
          <div className="bg-card rounded-lg border p-6">
            <h2 className="text-xl font-medium mb-4">Sign Out</h2>
            <p className="text-sm text-muted-foreground mb-4">
              Sign out of your account. You'll need to log in again to access your account.
            </p>
            <Button
              onClick={handleLogout}
              disabled={logoutStatus === "pending"}
              className="nv-gradient-button w-full sm:w-auto text-white"
            >
              {logoutStatus === "pending" ? "Signing out..." : "Sign Out"}
            </Button>
          </div>
        )}
      </div>
    </div>
  );
}
