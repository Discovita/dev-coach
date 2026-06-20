import { useForm } from "@tanstack/react-form";
import { Link } from "@tanstack/react-router";
import { motion } from "framer-motion";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useAuth } from "@/hooks/use-auth";

const nvLogoSmall = "/neovita_logo_small.png";

/**
 * Forgot Password Route (/forgot-password)
 *
 * Collects an email and asks the backend to send a password-reset link.
 * Always shows the same generic confirmation (the backend does not reveal
 * whether an account exists).
 */
export default function ForgotPasswordPage() {
  const { forgotPassword } = useAuth();
  const [submitted, setSubmitted] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const form = useForm({
    defaultValues: { email: "" },
    onSubmit: async ({ value }) => {
      setErrorMessage(null);
      try {
        await forgotPassword(value.email);
        // Backend is intentionally non-committal about account existence.
        setSubmitted(true);
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

        {submitted ? (
          <motion.div
            className="rounded-2xl bg-white p-8 text-center shadow-sm"
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4 }}
          >
            <h1 className="text-[28px] font-medium text-black">Check your email</h1>
            <p className="mt-3 text-[16px] text-black/70">
              If an account exists for that address, we&apos;ve sent a link to
              reset your password.
            </p>
            <Link
              to="/login"
              className="mt-6 inline-block text-[color:var(--nv-violet-blue)] underline"
            >
              Back to login
            </Link>
          </motion.div>
        ) : (
          <motion.div
            className="rounded-2xl bg-white p-8 shadow-sm"
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4 }}
          >
            <h1 className="text-[28px] font-medium text-black text-center">
              Forgot password?
            </h1>
            <p className="mt-2 mb-6 text-center text-[16px] text-black/70">
              Enter your email and we&apos;ll send you a reset link.
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
                name="email"
                validators={{
                  onChange: ({ value }) =>
                    !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)
                      ? "Enter a valid email"
                      : undefined,
                }}
              >
                {(field) => (
                  <div className="space-y-2">
                    <Label htmlFor={field.name} className="text-base">
                      Your email
                    </Label>
                    <Input
                      id={field.name}
                      type="email"
                      placeholder="Enter your email address"
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
                    {isSubmitting ? "Sending…" : "Send reset link"}
                  </Button>
                )}
              </form.Subscribe>
            </form>

            <p className="mt-8 text-center text-sm text-foreground">
              Remembered it?{" "}
              <Link
                to="/login"
                className="text-[color:var(--nv-violet-blue)] underline"
              >
                Back to login
              </Link>
            </p>
          </motion.div>
        )}
      </div>
    </div>
  );
}
