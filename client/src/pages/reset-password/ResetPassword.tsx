import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useAuth } from "@/hooks/use-auth";
import { useForm } from "@tanstack/react-form";
import { Link, useNavigate } from "@tanstack/react-router";
import { motion } from "framer-motion";
import { useMemo, useState } from "react";

const nvLogoSmall = "/neovita_logo_small.png";

/**
 * Reset Password Route (/reset-password?token=...)
 *
 * Reads the reset token from the query string (the link emailed by the
 * backend), collects a new password, and submits it. On success the user is
 * sent back to the login page.
 */
export default function ResetPasswordPage() {
	const { resetPassword } = useAuth();
	const navigate = useNavigate();
	const [errorMessage, setErrorMessage] = useState<string | null>(null);
	const [done, setDone] = useState(false);

	const token = useMemo(
		() => new URLSearchParams(window.location.search).get("token") ?? "",
		[],
	);

	const form = useForm({
		defaultValues: { password: "", confirm: "" },
		onSubmit: async ({ value }) => {
			setErrorMessage(null);
			if (value.password !== value.confirm) {
				setErrorMessage("Passwords don't match.");
				return;
			}
			try {
				const response = await resetPassword({
					token,
					password: value.password,
				});
				if (response.success) {
					setDone(true);
					setTimeout(() => navigate({ to: "/login" }), 2000);
				} else {
					setErrorMessage(
						response.error || "This reset link is invalid or has expired.",
					);
				}
			} catch {
				setErrorMessage("Something went wrong. Please try again.");
			}
		},
	});

	return (
		<div className="min-h-screen w-screen flex items-center justify-center bg-[var(--nv-lilac-white)] px-6">
			<div className="w-full max-w-[460px]">
				<div className="mb-8 flex flex-col items-center gap-4">
					<img
						src={nvLogoSmall}
						alt="Neovita mark"
						className="h-[80px] w-auto select-none"
						draggable={false}
					/>
				</div>

				<motion.div
					className="rounded-2xl bg-white p-8 shadow-sm"
					initial={{ opacity: 0, y: 12 }}
					animate={{ opacity: 1, y: 0 }}
					transition={{ duration: 0.4 }}
				>
					{done ? (
						<div className="text-center">
							<h1 className="text-[28px] font-medium text-black">
								Password updated
							</h1>
							<p className="mt-3 text-[16px] text-black/70">
								You can now log in with your new password. Redirecting…
							</p>
							<Link
								to="/login"
								className="mt-6 inline-block text-[color:var(--nv-violet-blue)] underline"
							>
								Go to login
							</Link>
						</div>
					) : !token ? (
						<div className="text-center">
							<h1 className="text-[28px] font-medium text-black">
								Invalid reset link
							</h1>
							<p className="mt-3 text-[16px] text-black/70">
								This link is missing its token. Request a new one from the
								forgot-password page.
							</p>
							<Link
								to="/forgot-password"
								className="mt-6 inline-block text-[color:var(--nv-violet-blue)] underline"
							>
								Request a new link
							</Link>
						</div>
					) : (
						<>
							<h1 className="text-[28px] font-medium text-black text-center">
								Choose a new password
							</h1>
							<p className="mt-2 mb-6 text-center text-[16px] text-black/70">
								Enter and confirm your new password.
							</p>

							<form
								className="space-y-6"
								onSubmit={(e) => {
									e.preventDefault();
									e.stopPropagation();
									form.handleSubmit();
								}}
							>
								<form.Field
									name="password"
									validators={{
										onChange: ({ value }) =>
											value.length < 8
												? "Password must be at least 8 characters"
												: undefined,
									}}
								>
									{(field) => (
										<div className="space-y-2">
											<Label htmlFor={field.name} className="text-base">
												New password
											</Label>
											<Input
												id={field.name}
												type="password"
												value={field.state.value}
												onBlur={field.handleBlur}
												onChange={(e) => field.handleChange(e.target.value)}
												className="h-12 rounded-full px-6 border border-black/50"
												aria-invalid={
													field.state.meta.errors.length ? true : undefined
												}
											/>
											{field.state.meta.isTouched &&
											field.state.meta.errors.length ? (
												<p className="mt-1 text-sm text-destructive">
													{field.state.meta.errors[0] as string}
												</p>
											) : null}
										</div>
									)}
								</form.Field>

								<form.Field name="confirm">
									{(field) => (
										<div className="space-y-2">
											<Label htmlFor={field.name} className="text-base">
												Confirm password
											</Label>
											<Input
												id={field.name}
												type="password"
												value={field.state.value}
												onBlur={field.handleBlur}
												onChange={(e) => field.handleChange(e.target.value)}
												className="h-12 rounded-full px-6 border border-black/50"
											/>
										</div>
									)}
								</form.Field>

								{errorMessage && (
									<p className="text-sm text-destructive text-center">
										{errorMessage}
									</p>
								)}

								<form.Subscribe selector={(s) => s.isSubmitting}>
									{(isSubmitting) => (
										<Button
											type="submit"
											disabled={isSubmitting}
											className="nv-gradient-button w-full rounded-full h-[52px] px-8 text-[20px] font-semibold"
										>
											{isSubmitting ? "Updating…" : "Update password"}
										</Button>
									)}
								</form.Subscribe>
							</form>
						</>
					)}
				</motion.div>
			</div>
		</div>
	);
}
