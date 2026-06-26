import { validateInvite } from "@/api/auth";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useAuth } from "@/hooks/use-auth";
import { useForm } from "@tanstack/react-form";
import { Link, useNavigate } from "@tanstack/react-router";
import { motion } from "framer-motion";
import { useEffect, useRef, useState } from "react";

const nvLogoSmall = "/neovita_logo_small.png";
const nvLogoLarge = "/neovita_logo_large.png";

type Status = "validating" | "valid" | "invalid";

/**
 * Invite Register Route (/invite/:token)
 *
 * The only path to the register form. Validates the magic-link token on mount,
 * reveals a register form with the invited email pre-filled and locked, and on
 * submit creates a verified account (the click proves email ownership) and logs
 * the user straight into onboarding.
 */
export default function InviteRegister({ token }: { token: string }) {
	const { registerViaInvite } = useAuth();
	const navigate = useNavigate();
	const [status, setStatus] = useState<Status>("validating");
	const [email, setEmail] = useState("");
	const [inviteError, setInviteError] = useState<string | null>(null);
	const [errorMessage, setErrorMessage] = useState<string | null>(null);
	const ranRef = useRef(false);

	useEffect(() => {
		if (ranRef.current) return;
		ranRef.current = true; // guard against StrictMode double-invoke
		validateInvite(token)
			.then((res) => {
				if (res.success && res.email) {
					setEmail(res.email);
					setStatus("valid");
				} else {
					setInviteError(res.error ?? "This invite link is invalid.");
					setStatus("invalid");
				}
			})
			.catch(() => {
				setInviteError("This invite link is invalid.");
				setStatus("invalid");
			});
	}, [token]);

	const form = useForm({
		defaultValues: { password: "", confirmPassword: "" },
		onSubmit: async ({ value }) => {
			setErrorMessage(null);
			try {
				const response = await registerViaInvite({
					token,
					password: value.password,
				});
				if (response.success) {
					// Accepting an invite logs you in — go straight to onboarding.
					navigate({ to: "/onboarding" });
				} else {
					setErrorMessage(
						(typeof response.error === "string" && response.error) ||
							"Registration failed. Please try again.",
					);
				}
			} catch {
				setErrorMessage("An unexpected error occurred. Please try again.");
			}
		},
	});

	return (
		<div className="h-screen w-screen bg-[var(--nv-lilac-white)]">
			<div className="grid grid-cols-1 lg:grid-cols-2 h-full w-full">
				{/* Left brand panel */}
				<div className="hidden lg:flex h-full w-full items-center justify-center bg-[var(--nv-pale-lavender)]">
					<div className="flex flex-col items-center gap-8">
						<img
							src={nvLogoSmall}
							srcSet={`${nvLogoSmall} 181w, ${nvLogoLarge} 881w`}
							sizes="(min-width:1280px) 200px, (min-width:1024px) 160px, 120px"
							alt="Neovita mark"
							className="h-[140px] lg:h-[160px] xl:h-[200px] w-auto select-none"
							draggable={false}
						/>
						<h2 className="text-7xl font-medium tracking-tight text-[color:var(--nv-indigo)]">
							neovita
						</h2>
					</div>
				</div>

				{/* Right panel */}
				<div className="h-full w-full flex items-center justify-center px-6 sm:px-10 lg:px-16 bg-white">
					<div className="w-full max-w-[500px] py-8 sm:py-10 lg:py-0">
						{status === "validating" && (
							<p className="text-center text-[18px] text-black/70">
								Checking your invite…
							</p>
						)}

						{status === "invalid" && (
							<div className="text-center">
								<h1 className="text-[32px] font-medium text-black">
									Invite unavailable
								</h1>
								<p className="mt-3 text-[16px] text-black/70">{inviteError}</p>
								<Link
									to="/login"
									className="mt-6 inline-block text-[color:var(--nv-violet-blue)] underline"
								>
									Go to log in
								</Link>
							</div>
						)}

						{status === "valid" && (
							<>
								<motion.div
									className="mb-8 text-center"
									initial={{ y: 24, opacity: 0 }}
									animate={{ y: 0, opacity: 1 }}
									transition={{ duration: 0.6, ease: "easeOut" }}
								>
									<h1 className="text-[36px] font-medium leading-none text-black text-center">
										Create your account
									</h1>
									<p className="mt-2 text-[20px] font-normal text-black/80">
										Set a password to finish signing up.
									</p>
								</motion.div>

								<motion.form
									className="space-y-6"
									initial={{ opacity: 0 }}
									animate={{ opacity: 1 }}
									transition={{ duration: 0.5, delay: 0.15 }}
									onSubmit={(e) => {
										e.preventDefault();
										e.stopPropagation();
										form.handleSubmit();
									}}
								>
									{/* Locked, pre-filled email from the invite */}
									<div className="space-y-2">
										<Label htmlFor="invite-email" className="text-base">
											Your email
										</Label>
										<Input
											id="invite-email"
											type="email"
											value={email}
											readOnly
											disabled
											className="h-12 rounded-full px-6 border border-black/50 bg-black/5"
										/>
									</div>

									<form.Field
										name="password"
										validators={{
											onChange: ({ value }) =>
												value.length < 6
													? "Password must be at least 6 characters"
													: undefined,
										}}
									>
										{(field) => (
											<div className="space-y-2">
												<Label htmlFor={field.name} className="text-base">
													Password
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

									<form.Field
										name="confirmPassword"
										validators={{
											onChangeListenTo: ["password"],
											onChange: ({ value, fieldApi }) => {
												const password = fieldApi.form.state.values
													.password as string;
												return value !== password
													? "Passwords must match"
													: undefined;
											},
										}}
									>
										{(field) => (
											<div className="space-y-2">
												<Label htmlFor={field.name} className="text-base">
													Confirm Password
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

									{errorMessage && (
										<div className="pt-2">
											<p className="text-sm text-destructive text-center">
												{errorMessage}
											</p>
										</div>
									)}

									<div className="pt-2">
										<Button
											type="submit"
											className="nv-gradient-button w-full rounded-full h-[52px] px-8 text-[20px] font-semibold"
										>
											Create account
										</Button>
									</div>
								</motion.form>

								<p className="mt-8 text-center text-sm text-foreground">
									Already have an account?{" "}
									<Link
										to="/login"
										className="text-[color:var(--nv-violet-blue)] underline"
									>
										Log in
									</Link>
								</p>
							</>
						)}
					</div>
				</div>
			</div>
		</div>
	);
}
