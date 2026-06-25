import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
	Dialog,
	DialogContent,
	DialogFooter,
	DialogHeader,
	DialogTitle,
	DialogTrigger,
} from "@/components/ui/dialog";
import {
	Select,
	SelectContent,
	SelectItem,
	SelectTrigger,
	SelectValue,
} from "@/components/ui/select";
import {
	useCreateMeditation,
	useMeditationsList,
} from "@/hooks/use-admin-meditations";
import { useAdminUsers } from "@/hooks/use-admin-users";
import { Loader2, Plus } from "lucide-react";
import { useState } from "react";
import MeditationDetailView from "./MeditationDetailView";
import {
	MEDITATION_STATUSES,
	formatStatus,
	statusVariant,
} from "./meditation-helpers";

/**
 * AdminMeditations page
 *
 * Status-filterable table of meditations. Selecting one opens the QC detail
 * view (per-segment video/audio parts). Route: /admin/meditations (admin-only,
 * gated behind the MEDITATIONS_ENABLED backend flag).
 */
export default function AdminMeditations() {
	const [selectedId, setSelectedId] = useState<string | null>(null);
	const [status, setStatus] = useState<string>("all");
	const { data: meditations, isLoading } = useMeditationsList(
		status === "all" ? undefined : status,
	);

	if (selectedId) {
		return (
			<MeditationDetailView
				meditationId={selectedId}
				onBack={() => setSelectedId(null)}
			/>
		);
	}

	return (
		<div className="max-w-5xl mx-auto">
			<div className="flex items-center justify-between mb-6">
				<div>
					<h1 className="text-2xl font-bold">Meditations</h1>
					<p className="text-sm text-muted-foreground mt-1">
						{meditations?.length ?? 0} meditations
					</p>
				</div>
				<CreateMeditationDialog onCreated={(id) => setSelectedId(id)} />
			</div>

			<div className="mb-4 w-56">
				<Select value={status} onValueChange={setStatus}>
					<SelectTrigger>
						<SelectValue placeholder="Filter by status" />
					</SelectTrigger>
					<SelectContent>
						<SelectItem value="all">All statuses</SelectItem>
						{MEDITATION_STATUSES.map((s) => (
							<SelectItem key={s} value={s}>
								{formatStatus(s)}
							</SelectItem>
						))}
					</SelectContent>
				</Select>
			</div>

			{isLoading ? (
				<div className="flex items-center justify-center h-64">
					<Loader2 className="w-6 h-6 animate-spin text-muted-foreground" />
				</div>
			) : (
				<div className="rounded-lg border border-border overflow-hidden">
					<table className="w-full text-sm">
						<thead>
							<tr className="bg-muted/50 border-b border-border">
								<th className="text-left font-medium px-4 py-3">User</th>
								<th className="text-left font-medium px-4 py-3">Status</th>
								<th className="text-left font-medium px-4 py-3 hidden md:table-cell">
									Segments
								</th>
								<th className="text-left font-medium px-4 py-3 hidden md:table-cell">
									Created
								</th>
							</tr>
						</thead>
						<tbody className="divide-y divide-border">
							{(meditations ?? []).map((m) => (
								<tr
									key={m.id}
									onClick={() => setSelectedId(m.id)}
									className="hover:bg-muted/30 transition-colors cursor-pointer"
								>
									<td className="px-4 py-3 font-medium">{m.user_email}</td>
									<td className="px-4 py-3">
										<Badge variant={statusVariant(m.status)}>
											{formatStatus(m.status)}
										</Badge>
									</td>
									<td className="px-4 py-3 hidden md:table-cell">
										{m.segment_count}
									</td>
									<td className="px-4 py-3 hidden md:table-cell text-muted-foreground">
										{new Date(m.created_at).toLocaleDateString()}
									</td>
								</tr>
							))}
							{(meditations ?? []).length === 0 && (
								<tr>
									<td
										colSpan={4}
										className="px-4 py-8 text-center text-muted-foreground"
									>
										No meditations yet.
									</td>
								</tr>
							)}
						</tbody>
					</table>
				</div>
			)}
		</div>
	);
}

function CreateMeditationDialog({
	onCreated,
}: {
	onCreated: (id: string) => void;
}) {
	const [open, setOpen] = useState(false);
	const [userId, setUserId] = useState<string>("");
	const { data: users } = useAdminUsers();
	const createMeditation = useCreateMeditation();

	const handleCreate = () => {
		if (!userId) return;
		createMeditation.mutate(userId, {
			onSuccess: (meditation) => {
				setOpen(false);
				setUserId("");
				onCreated(meditation.id);
			},
		});
	};

	return (
		<Dialog open={open} onOpenChange={setOpen}>
			<DialogTrigger asChild>
				<Button size="sm" className="gap-1.5">
					<Plus className="w-4 h-4" />
					New meditation
				</Button>
			</DialogTrigger>
			<DialogContent>
				<DialogHeader>
					<DialogTitle>Create a meditation</DialogTitle>
				</DialogHeader>
				<div className="py-2">
					<Select value={userId} onValueChange={setUserId}>
						<SelectTrigger>
							<SelectValue placeholder="Select a user" />
						</SelectTrigger>
						<SelectContent>
							{(users ?? []).map((u) => (
								<SelectItem key={u.id} value={u.id}>
									{u.email}
								</SelectItem>
							))}
						</SelectContent>
					</Select>
				</div>
				<DialogFooter>
					<Button
						onClick={handleCreate}
						disabled={!userId || createMeditation.isPending}
					>
						{createMeditation.isPending ? "Creating…" : "Create"}
					</Button>
				</DialogFooter>
			</DialogContent>
		</Dialog>
	);
}
