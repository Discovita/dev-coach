import { useForm } from "@tanstack/react-form";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Link, useNavigate } from "@tanstack/react-router";
import { motion } from "framer-motion";
// import { FaGoogle, FaApple } from "react-icons/fa";
import { useState, useEffect } from "react";
import { useAuth } from "@/hooks/use-auth";
import { useProfile } from "@/hooks/use-profile";

// Values managed by this form:
// Keeping as a type reference for future backend integration
// type LoginValues = { email: string; password: string };

// Neovita logo assets from public/ (Vite serves these at the root path)
const nvLogoSmall = "/neovita_logo_small.png";
const nvLogoLarge = "/neovita_logo_large.png";

/**
 * Login Route (/login)
 *
 * Purpose:
 * - Renders a standalone login form with email and password fields.
 * - Uses TanStack Form for state/validation and submission.
 * - Integrates with useAuth hook for authentication.
   * - Redirects users to /chat after successful login.
 *
 * Validation:
 * - Email: simple format check
 * - Password: at least 6 characters
 */
export default function LoginPage() {
  const { login } = useAuth();
  const { profile } = useProfile();
  const navigate = useNavigate();
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const form = useForm({
    defaultValues: { email: "", password: "" },
    onSubmit: async ({ value }) => {
      setErrorMessage(null);
      try {
        const response = await login({
          email: value.email,
          password: value.password,
        });
        if (response.success) {
          // Redirect handled by the useEffect below when profile cache updates
        } else {
          let errorMsg = response.error;
          if (typeof errorMsg === "object" && errorMsg !== null) {
            // Convert error object to a readable string
            errorMsg = Object.entries(errorMsg)
              .map(
                ([field, msgs]) =>
                  `${field}: ${Array.isArray(msgs) ? msgs.join(", ") : msgs}`
              )
              .join("; ");
          }
          setErrorMessage(errorMsg || "Login failed. Please try again.");
        }
      } catch (error) {
        setErrorMessage("An unexpected error occurred. Please try again.");
        console.error("Login error:", error);
      }
    },
  });

  // Redirect after successful login based on user role, as soon as cache updates
  useEffect(() => {
    if (!profile) return;

    navigate({ to: "/chat" });
  }, [profile, navigate]);

  return (
    <div className="h-screen w-screen bg-[var(--nv-lilac-white)]">
      {/* Full-viewport split layout */}
      <div className="grid grid-cols-1 lg:grid-cols-2 h-full w-full">
        {/* Left brand panel (full height on desktop) */}
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

        {/* Right form panel (full height) */}
        <div className="h-full w-full flex items-center justify-center px-6 sm:px-10 lg:px-16 bg-white">
          <div className="w-full max-w-[500px] py-8 sm:py-10 lg:py-0">
            <motion.div
              className="mb-8 text-center"
              initial={{ y: 24, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ duration: 0.6, ease: "easeOut" }}
            >
              <h1 className="text-[36px] font-medium leading-none text-black text-center">
                Welcome
              </h1>
              <p className="mt-2 text-[20px] font-normal text-black/80">
                Please enter your details to login.
              </p>
            </motion.div>

            {/* Form first in Figma order after social? We keep form primary above divider */}
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
                    <div className="flex items-center justify-between">
                      <Label htmlFor={field.name} className="text-base">
                        Password
                      </Label>
                      <button
                        type="button"
                        className="text-sm text-muted-foreground hover:underline"
                        onClick={() => console.log("Forgot password")}
                      >
                        Forgot password?
                      </button>
                    </div>
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
                  Login
                </Button>
              </div>
            </motion.form>

            {/* Divider */}
            {/* <div className="my-6 flex items-center gap-3 text-xs text-muted-foreground">
              <div className="h-px flex-1 bg-border" />
              <span>or</span>
              <div className="h-px flex-1 bg-border" />
            </div> */}

            {/* Secondary providers */}
            {/* <div className="space-y-4">
              <Button
                type="button"
                variant="ghost"
                className="w-full h-12 rounded-full border-2 border-[var(--nv-royal-purple)] bg-transparent text-[color:var(--nv-royal-purple)]"
                onClick={() => console.log("Continue with Google")}
              >
                <FaGoogle className="mr-2" aria-hidden="true" />
                <span className="nv-gradient-text">Continue with Google</span>
              </Button>
              <Button
                type="button"
                variant="ghost"
                className="w-full h-12 rounded-full border-2 border-[var(--nv-royal-purple)] bg-transparent text-[color:var(--nv-royal-purple)]"
                onClick={() => console.log("Continue with Apple")}
              >
                <FaApple className="mr-2" aria-hidden="true" />
                <span className="nv-gradient-text">Continue with Apple</span>
              </Button>
            </div> */}

            <p className="mt-8 text-center text-sm text-foreground">
              Don’t have an account?{" "}
              <Link
                to="/signup"
                className="text-[color:var(--nv-violet-blue)] underline"
              >
                Sign up.
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
