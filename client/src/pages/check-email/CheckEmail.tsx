import { Link } from "@tanstack/react-router";
import { motion } from "framer-motion";
import { useMemo, useState } from "react";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/hooks/use-auth";

const nvLogoSmall = "/neovita_logo_small.png";

/**
 * Check Email Route (/check-email?email=...)
 *
 * The post-registration pause page. The user has been sent a verification
 * link and cannot continue until they confirm their email. Offers a resend.
 */
export default function CheckEmailPage() {
  const { resendVerification } = useAuth();
  const email = useMemo(
    () => new URLSearchParams(window.location.search).get("email") ?? "",
    []
  );
  const [resent, setResent] = useState(false);
  const [sending, setSending] = useState(false);

  async function handleResend() {
    if (!email || sending) return;
    setSending(true);
    try {
      await resendVerification(email);
    } finally {
      setResent(true);
      setSending(false);
    }
  }

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
          className="rounded-2xl bg-white p-8 text-center shadow-sm"
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
        >
          <h1 className="text-[28px] font-medium text-black">
            Verify your email to continue
          </h1>
          <p className="mt-3 text-[16px] text-black/70">
            We sent a verification link to
            {email ? (
              <>
                {" "}
                <span className="font-medium text-black">{email}</span>.
              </>
            ) : (
              " your email."
            )}{" "}
            Click it to activate your account, then you&rsquo;ll be brought
            right back.
          </p>

          <div className="mt-6">
            {resent ? (
              <p className="text-[15px] text-[color:var(--nv-violet-blue)]">
                Sent! Check your inbox (and spam folder).
              </p>
            ) : (
              <Button
                type="button"
                onClick={handleResend}
                disabled={sending || !email}
                className="nv-gradient-button w-full rounded-full h-[52px] px-8 text-[18px] font-semibold"
              >
                {sending ? "Sending…" : "Resend verification email"}
              </Button>
            )}
          </div>

          <p className="mt-8 text-center text-sm text-foreground">
            Already verified?{" "}
            <Link
              to="/login"
              className="text-[color:var(--nv-violet-blue)] underline"
            >
              Log in
            </Link>
          </p>
        </motion.div>
      </div>
    </div>
  );
}
