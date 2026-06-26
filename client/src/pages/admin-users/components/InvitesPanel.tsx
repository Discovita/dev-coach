import type { InviteStatus } from "@/api/adminInvites";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useAdminInvites } from "@/hooks/use-admin-invites";
import { Loader2, Mail, RotateCw, Send, X } from "lucide-react";
import { useState } from "react";

/**
 * InvitesPanel
 *
 * Super-admin-only UI to send and manage email-bound invites. Rendered on the
 * admin Users page, gated on the logged-in admin's is_superuser flag (the
 * backend also enforces IsSuperUser on every endpoint).
 */

const STATUS_STYLES: Record<InviteStatus, string> = {
	pending:
		"bg-blue-100 text-blue-800 border-blue-200 dark:bg-blue-950/40 dark:text-blue-300",
	accepted:
		"bg-green-100 text-green-800 border-green-200 dark:bg-green-950/40 dark:text-green-300",
	expired:
		"bg-gray-100 text-gray-600 border-gray-200 dark:bg-gray-800 dark:text-gray-400",
};

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export default function InvitesPanel() {
	const {
		invites,
		isLoading,
		isError,
		createInvite,
		createStatus,
		createError,
		resendInvite,
		resendingId,
		revokeInvite,
		revokingId,
	} = useAdminInvites();
	const [email, setEmail] = useState("");
	const [notice, setNotice] = useState<string | null>(null);

	const isSending = createStatus === "pending";

	const handleSend = async () => {
		setNotice(null);
		const trimmed = email.trim();
		if (!EMAIL_RE.test(trimmed)) {
			setNotice("Enter a valid email address.");
			return;
		}
		try {
			const result = await createInvite(trimmed);
			setEmail("");
			setNotice(
				result.email_sent
					? `Invite sent to ${result.email}.`
					: `Invite created for ${result.email}, but the email failed to send.`,
			);
		} catch {
			// createError surfaces the message below.
		}
	};

	const formatDate = (iso: string | null) =>
		iso ? new Date(iso).toLocaleDateString() : "—";

	return (
		<div className="rounded-lg border border-border mb-8">
			<div className="px-4 py-3 border-b border-border flex items-center gap-2">
				<Mail className="w-4 h-4 text-muted-foreground" />
				<h2 className="font-semibold">Invites</h2>
				<span className="text-xs text-muted-foreground">
					Registration is invite-only
				</span>
			</div>

			{/* Send invite */}
			<div className="px-4 py-3 border-b border-border">
				<div className="flex flex-col sm:flex-row gap-2">
					<Input
						type="email"
						placeholder="name@example.com"
						value={email}
						onChange={(e) => setEmail(e.target.value)}
						onKeyDown={(e) => {
							if (e.key === "Enter") handleSend();
						}}
						className="flex-1"
					/>
					<Button
						onClick={handleSend}
						disabled={isSending}
						className="gap-1.5 shrink-0"
					>
						{isSending ? (
							<Loader2 className="w-4 h-4 animate-spin" />
						) : (
							<Send className="w-4 h-4" />
						)}
						Send invite
					</Button>
				</div>
				{notice && (
					<p className="mt-2 text-xs text-muted-foreground">{notice}</p>
				)}
				{createError && (
					<p className="mt-2 text-xs text-destructive">{createError.message}</p>
				)}
			</div>

			{/* Invite list */}
			<div className="overflow-x-auto">
				<table className="w-full text-sm">
					<thead>
						<tr className="bg-muted/50 border-b border-border">
							<th className="text-left font-medium px-4 py-2.5">Email</th>
							<th className="text-left font-medium px-4 py-2.5">Status</th>
							<th className="text-left font-medium px-4 py-2.5 hidden md:table-cell">
								Expires
							</th>
							<th className="text-left font-medium px-4 py-2.5 hidden lg:table-cell">
								Invited by
							</th>
							<th className="text-right font-medium px-4 py-2.5">Actions</th>
						</tr>
					</thead>
					<tbody className="divide-y divide-border">
						{isLoading && (
							<tr>
								<td colSpan={5} className="px-4 py-6 text-center">
									<Loader2 className="w-5 h-5 animate-spin text-muted-foreground inline" />
								</td>
							</tr>
						)}
						{isError && !isLoading && (
							<tr>
								<td
									colSpan={5}
									className="px-4 py-6 text-center text-destructive"
								>
									Failed to load invites.
								</td>
							</tr>
						)}
						{!isLoading &&
							!isError &&
							invites.map((invite) => (
								<tr key={invite.id} className="hover:bg-muted/30">
									<td className="px-4 py-2.5">{invite.email}</td>
									<td className="px-4 py-2.5">
										<Badge
											variant="outline"
											className={`text-xs font-normal ${STATUS_STYLES[invite.status]}`}
										>
											{invite.status}
										</Badge>
									</td>
									<td className="px-4 py-2.5 hidden md:table-cell text-muted-foreground">
										{formatDate(invite.expires_at)}
									</td>
									<td className="px-4 py-2.5 hidden lg:table-cell text-muted-foreground text-xs">
										{invite.invited_by_email ?? "—"}
									</td>
									<td className="px-4 py-2.5 text-right">
										{invite.status === "accepted" ? (
											<span className="text-xs text-muted-foreground">—</span>
										) : (
											<div className="flex items-center justify-end gap-1">
												<Button
													variant="ghost"
													size="sm"
													className="gap-1.5"
													disabled={resendingId === invite.id}
													onClick={() => resendInvite(invite.id)}
												>
													{resendingId === invite.id ? (
														<Loader2 className="w-3.5 h-3.5 animate-spin" />
													) : (
														<RotateCw className="w-3.5 h-3.5" />
													)}
													Resend
												</Button>
												<Button
													variant="ghost"
													size="sm"
													className="gap-1.5 text-destructive hover:text-destructive"
													disabled={revokingId === invite.id}
													onClick={() => revokeInvite(invite.id)}
												>
													{revokingId === invite.id ? (
														<Loader2 className="w-3.5 h-3.5 animate-spin" />
													) : (
														<X className="w-3.5 h-3.5" />
													)}
													Revoke
												</Button>
											</div>
										)}
									</td>
								</tr>
							))}
						{!isLoading && !isError && invites.length === 0 && (
							<tr>
								<td
									colSpan={5}
									className="px-4 py-6 text-center text-muted-foreground"
								>
									No invites yet.
								</td>
							</tr>
						)}
					</tbody>
				</table>
			</div>
		</div>
	);
}
