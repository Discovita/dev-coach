import { Button } from "@/components/ui/button";
import { useProfile } from "@/hooks/use-profile";
import { useUpdateProfile } from "@/hooks/use-update-profile";
import { useUserAppearance } from "@/hooks/use-user-appearance";
import {
	NameFields,
	type NameValue,
} from "@/pages/account/components/NameFields";
import { ReferenceImageUploader } from "@/pages/account/components/ReferenceImageUploader";
import {
	APPEARANCE_FIELDS,
	AppearanceFields,
	countFilledFields,
} from "@/pages/account/components/appearance";
import type { UserAppearance } from "@/types/userAppearance";
import { useNavigate } from "@tanstack/react-router";
import { motion } from "framer-motion";
import { useEffect, useState } from "react";
import { toast } from "sonner";

const nvLogoSmall = "/neovita_logo_small.png";

type Step = "name" | "appearance" | "photos";

const STEP_NUMBER: Record<Step, number> = { name: 1, appearance: 2, photos: 3 };

/**
 * Onboarding (/onboarding)
 *
 * Guided post-email-verification setup. A just-verified user is routed here
 * (instead of straight to /chat) to fill out their profile before meeting the
 * coach:
 *   1. Name (required)  2. Appearance preferences  3. Reference photos
 *
 * The name step is required — it has no skip and blocks until both names are
 * filled. The appearance and photo steps are skippable; nothing there gates the
 * coach (they gate image generation later). Reuses the same components the
 * account page uses, so anything set here is editable later from the account page.
 */
export default function Onboarding() {
	const navigate = useNavigate();
	const { profile } = useProfile();
	const { updateProfile, isUpdating: isSavingName } = useUpdateProfile();
	const { appearance, updateAppearance, isUpdating } = useUserAppearance(
		profile?.id ?? null,
	);

	const [step, setStep] = useState<Step>("name");
	const [localName, setLocalName] = useState<NameValue>({
		first_name: "",
		last_name: "",
	});
	const [localAppearance, setLocalAppearance] = useState<UserAppearance>({});

	// Seed the editable name copy once the profile loads (pre-fill if already set).
	useEffect(() => {
		if (profile) {
			setLocalName({
				first_name: profile.first_name ?? "",
				last_name: profile.last_name ?? "",
			});
		}
	}, [profile]);

	// Seed the editable copy once the saved appearance loads.
	useEffect(() => {
		if (appearance) setLocalAppearance(appearance);
	}, [appearance]);

	const filledCount = countFilledFields(localAppearance);
	const nameComplete =
		localName.first_name.trim().length > 0 &&
		localName.last_name.trim().length > 0;

	const goToChat = () => navigate({ to: "/chat" });

	const handleSaveName = async () => {
		try {
			await updateProfile({
				first_name: localName.first_name.trim(),
				last_name: localName.last_name.trim(),
			});
			setStep("appearance");
		} catch (error) {
			const message =
				error instanceof Error ? error.message : "Failed to save your name";
			toast.error(message);
		}
	};

	const handleSaveAppearance = async () => {
		try {
			await updateAppearance(localAppearance);
			setStep("photos");
		} catch (error) {
			const message =
				error instanceof Error ? error.message : "Failed to save preferences";
			toast.error(message);
		}
	};

	return (
		<div className="min-h-screen w-screen flex items-center justify-center bg-[var(--nv-lilac-white)] px-6 py-10">
			<div className="w-full max-w-[640px]">
				<div className="mb-8 flex flex-col items-center gap-4">
					<img
						src={nvLogoSmall}
						alt="Neovita mark"
						className="h-[80px] w-auto select-none"
						draggable={false}
					/>
				</div>

				<motion.div
					key={step}
					className="rounded-2xl bg-white p-8 shadow-sm"
					initial={{ opacity: 0, y: 12 }}
					animate={{ opacity: 1, y: 0 }}
					transition={{ duration: 0.4 }}
				>
					<p className="text-sm font-medium text-[color:var(--nv-violet-blue)]">
						Step {STEP_NUMBER[step]} of 3
					</p>

					{step === "name" ? (
						<>
							<h1 className="mt-1 text-[26px] font-medium text-black">
								What should we call you?
							</h1>
							<p className="mt-3 text-[15px] leading-relaxed text-black/70">
								Let&rsquo;s start with your name &mdash; it&rsquo;s how your
								coach will address you throughout your journey.
							</p>

							<div className="mt-6">
								<NameFields value={localName} onChange={setLocalName} />
							</div>

							<div className="mt-8 flex items-center justify-end gap-3">
								<Button
									type="button"
									onClick={handleSaveName}
									disabled={!nameComplete || isSavingName}
									className="nv-gradient-button text-white"
								>
									{isSavingName ? "Saving..." : "Save & continue"}
								</Button>
							</div>
						</>
					) : step === "appearance" ? (
						<>
							<h1 className="mt-1 text-[26px] font-medium text-black">
								How should we picture you?
							</h1>
							<p className="mt-3 text-[15px] leading-relaxed text-black/70">
								Part of designing your new life is creating personalized images
								of you. These details tell us how to portray you &mdash; so
								those images actually look like you. It takes just a minute, and
								you can change any of it later if you want. If you&rsquo;re
								excited to just get started, you can skip for now &mdash; just
								know image generation stays locked until this is filled out.
							</p>

							<div className="mt-6">
								<AppearanceFields
									value={localAppearance}
									onChange={setLocalAppearance}
								/>
							</div>

							<p className="mt-4 text-sm text-muted-foreground">
								{filledCount} of {APPEARANCE_FIELDS.length} selected
							</p>

							<div className="mt-8 flex items-center justify-between gap-3">
								<Button
									type="button"
									variant="ghost"
									onClick={() => setStep("photos")}
									className="text-black/60"
								>
									Skip for now
								</Button>
								<Button
									type="button"
									onClick={handleSaveAppearance}
									disabled={isUpdating}
									className="nv-gradient-button text-white"
								>
									{isUpdating ? "Saving..." : "Save & continue"}
								</Button>
							</div>
						</>
					) : (
						<>
							<h1 className="mt-1 text-[26px] font-medium text-black">
								Now add a few photos of you
							</h1>
							<p className="mt-3 text-[15px] leading-relaxed text-black/70">
								A few real photos help us generate images that genuinely look
								like you. Add up to five &mdash; the tips below get you the best
								results. Like everything here, you can update these anytime from
								your account, or skip for now and come back later.
							</p>

							<div className="mt-6">
								<ReferenceImageUploader heading="Your photos" intro={null} />
							</div>

							<div className="mt-8 flex items-center justify-between gap-3">
								<Button
									type="button"
									variant="ghost"
									onClick={() => setStep("appearance")}
									className="text-black/60"
								>
									Back
								</Button>
								<div className="flex items-center gap-3">
									<Button
										type="button"
										variant="ghost"
										onClick={goToChat}
										className="text-black/60"
									>
										Skip for now
									</Button>
									<Button
										type="button"
										onClick={goToChat}
										className="nv-gradient-button text-white"
									>
										Let&rsquo;s Go!
									</Button>
								</div>
							</div>
						</>
					)}
				</motion.div>
			</div>
		</div>
	);
}
