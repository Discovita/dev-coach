import { useEffect, useState } from "react";
import { useNavigate } from "@tanstack/react-router";
import { motion } from "framer-motion";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { useProfile } from "@/hooks/use-profile";
import { useUserAppearance } from "@/hooks/use-user-appearance";
import {
  AppearanceFields,
  APPEARANCE_FIELDS,
  countFilledFields,
} from "@/pages/account/components/appearance";
import { ReferenceImageUploader } from "@/pages/account/components/ReferenceImageUploader";
import type { UserAppearance } from "@/types/userAppearance";

const nvLogoSmall = "/neovita_logo_small.png";

type Step = "appearance" | "photos";

/**
 * Onboarding (/onboarding)
 *
 * Guided post-email-verification setup. A just-verified user is routed here
 * (instead of straight to /chat) to optionally fill out the two image-related
 * profile pieces before meeting the coach:
 *   1. Appearance preferences  2. Reference photos
 *
 * Both steps are skippable — nothing here gates the coach. They gate image
 * generation later, which is why we encourage (but don't require) them now.
 * Reuses the same components the account page uses, so anything set here is
 * editable later from the account page.
 *
 * NOTE: framing copy below is intentionally lightweight — refine before launch.
 */
export default function Onboarding() {
  const navigate = useNavigate();
  const { profile } = useProfile();
  const { appearance, updateAppearance, isUpdating } = useUserAppearance(
    profile?.id ?? null
  );

  const [step, setStep] = useState<Step>("appearance");
  const [localAppearance, setLocalAppearance] = useState<UserAppearance>({});

  // Seed the editable copy once the saved appearance loads.
  useEffect(() => {
    if (appearance) setLocalAppearance(appearance);
  }, [appearance]);

  const filledCount = countFilledFields(localAppearance);

  const goToChat = () => navigate({ to: "/chat" });

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
            Step {step === "appearance" ? 1 : 2} of 2
          </p>

          {step === "appearance" ? (
            <>
              <h1 className="mt-1 text-[26px] font-medium text-black">
                How should we picture you?
              </h1>
              <p className="mt-3 text-[15px] leading-relaxed text-black/70">
                Before you meet your coach, tell us how you&rsquo;d like to be
                portrayed in the images generated for you throughout the program.
                We recommend setting this now &mdash; image generation stays locked
                until it&rsquo;s filled out &mdash; but you can skip ahead and do it
                later from your account.
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
                Add a few photos of yourself
              </h1>
              <p className="mt-3 text-[15px] leading-relaxed text-black/70">
                Real photos help your generated images actually look like you. Add
                up to five &mdash; the tips below get you the best results. You can
                update these anytime from your account, or skip for now and come
                back later.
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
                    Go to my coach
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
