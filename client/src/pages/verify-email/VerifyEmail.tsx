import { Link } from "@tanstack/react-router";
import { motion } from "framer-motion";
import { useEffect, useMemo, useRef, useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useAuth } from "@/hooks/use-auth";

const nvLogoSmall = "/neovita_logo_small.png";

type Status = "verifying" | "success" | "error" | "no-token";

/**
 * Verify Email Route (/verify-email?token=...)
 *
 * Reads the token from the verification link and confirms it on mount. On
 * failure, offers to re-send a fresh verification email.
 */
export default function VerifyEmailPage() {
  const { verifyEmail, resendVerification } = useAuth();
  const token = useMemo(
    () => new URLSearchParams(window.location.search).get("token") ?? "",
    []
  );
  const [status, setStatus] = useState<Status>(token ? "verifying" : "no-token");
  const [resendEmail, setResendEmail] = useState("");
  const [resent, setResent] = useState(false);
  const ranRef = useRef(false);

  useEffect(() => {
    if (!token || ranRef.current) return;
    ranRef.current = true; // guard against StrictMode double-invoke
    verifyEmail(token)
      .then((response) => setStatus(response.success ? "success" : "error"))
      .catch(() => setStatus("error"));
  }, [token, verifyEmail]);

  async function handleResend() {
    if (!resendEmail) return;
    try {
      await resendVerification(resendEmail);
    } finally {
      // Generic confirmation regardless of outcome (no account-existence leak).
      setResent(true);
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
          {status === "verifying" && (
            <>
              <h1 className="text-[28px] font-medium text-black">
                Verifying your email…
              </h1>
              <p className="mt-3 text-[16px] text-black/70">One moment.</p>
            </>
          )}

          {status === "success" && (
            <>
              <h1 className="text-[28px] font-medium text-black">
                Email verified
              </h1>
              <p className="mt-3 text-[16px] text-black/70">
                Thanks for confirming your email address.
              </p>
              <Link
                to="/login"
                className="mt-6 inline-block text-[color:var(--nv-violet-blue)] underline"
              >
                Continue to login
              </Link>
            </>
          )}

          {(status === "error" || status === "no-token") && (
            <>
              <h1 className="text-[28px] font-medium text-black">
                {status === "no-token"
                  ? "Invalid verification link"
                  : "Link expired or invalid"}
              </h1>
              {resent ? (
                <p className="mt-3 text-[16px] text-black/70">
                  If an unverified account exists for that address, a new
                  verification email is on its way.
                </p>
              ) : (
                <>
                  <p className="mt-3 mb-5 text-[16px] text-black/70">
                    Enter your email to get a fresh verification link.
                  </p>
                  <div className="space-y-4">
                    <Input
                      type="email"
                      placeholder="Enter your email address"
                      value={resendEmail}
                      onChange={(e) => setResendEmail(e.target.value)}
                      className="h-12 rounded-full px-6 border border-black/50"
                    />
                    <Button
                      type="button"
                      onClick={handleResend}
                      className="nv-gradient-button w-full rounded-full h-[52px] px-8 text-[18px] font-semibold"
                    >
                      Resend verification email
                    </Button>
                  </div>
                </>
              )}
              <Link
                to="/login"
                className="mt-6 inline-block text-[color:var(--nv-violet-blue)] underline"
              >
                Back to login
              </Link>
            </>
          )}
        </motion.div>
      </div>
    </div>
  );
}
