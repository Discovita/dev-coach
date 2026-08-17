import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useProfile } from "@/hooks/use-profile";
import InvitesPanel from "@/pages/admin-users/components/InvitesPanel";
import UsersPanel from "@/pages/admin-users/components/UsersPanel";

/**
 * AdminUsers page
 *
 * Two tabs: the user list (search, impersonate) and invite management.
 * The Invites tab is super-admin only — the backend also enforces
 * IsSuperUser on every invite endpoint — so plain admins see the user
 * list on its own with no tab strip.
 *
 * Route: /admin/users
 */
export default function AdminUsers() {
	const { profile } = useProfile();

	if (!profile?.is_superuser) {
		return (
			<div className="max-w-5xl mx-auto">
				<h1 className="text-2xl font-bold mb-6">Users</h1>
				<UsersPanel />
			</div>
		);
	}

	return (
		<div className="max-w-5xl mx-auto">
			<h1 className="text-2xl font-bold mb-6">Users</h1>

			<Tabs defaultValue="users">
				<TabsList className="mb-4">
					<TabsTrigger value="users">Users</TabsTrigger>
					<TabsTrigger value="invites">Invites</TabsTrigger>
				</TabsList>

				<TabsContent value="users">
					<UsersPanel />
				</TabsContent>

				<TabsContent value="invites">
					<InvitesPanel />
				</TabsContent>
			</Tabs>
		</div>
	);
}
