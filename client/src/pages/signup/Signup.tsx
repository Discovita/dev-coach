import { useForm } from "@tanstack/react-form";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Link, useNavigate } from "@tanstack/react-router";
import { motion } from "framer-motion";
import { useState, useEffect } from "react";
import { useAuth } from "@/hooks/use-auth";
import { useProfile } from "@/hooks/use-profile";

/**
 * Signup Route (/signup)
 *
 * Purpose:
 * - Renders a signup form with email, password, confirmPassword.
 * - Uses TanStack Form for state/validation and submission.
 * - Integrates with useAuth hook for registration.
 * - Redirects users after successful registration to /chat.
 *
 * Validation:
 * - Email: simple format check
 * - Password: at least 6 characters
 * - Confirm Password: must match password
 */

// Neovita logo assets from public/
const nvLogoSmall = "/neovita_logo_small.png";
const nvLogoLarge = "/neovita_logo_large.png";

export default function Signup() {
  const { register } = useAuth();
  const { profile } = useProfile();
  const navigate = useNavigate();
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const form = useForm({
    defaultValues: { email: "", password: "", confirmPassword: "" },
    onSubmit: async ({ value }) => {
      setErrorMessage(null);
      try {
        const response = await register({
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
          setErrorMessage(errorMsg || "Registration failed. Please try again.");
        }
      } catch (error) {
        setErrorMessage("An unexpected error occurred. Please try again.");
        console.error("Registration error:", error);
      }
    },
  });

  // Redirect after successful registration when profile is available
  useEffect(() => {
    if (!profile) return;

    navigate({ to: "/chat" });
  }, [profile, navigate]);

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
            <motion.div
              className="mb-8 text-center"
              initial={{ y: 24, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ duration: 0.6, ease: "easeOut" }}
            >
              <h1 className="text-[36px] font-medium leading-none text-black text-center">
                Create account
              </h1>
              <p className="mt-2 text-[20px] font-normal text-black/80">
                Please enter your details to sign up.
              </p>
            </motion.div>

            {/* Form */}
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
                    const password = fieldApi.form.state.values.password as string;
                    return value !== password ? "Passwords must match" : undefined;
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
                  Sign up
                </Button>
              </div>
            </motion.form>

            {/* Divider */}
            {/* <div className="my-6 flex items-center gap-3 text-xs text-muted-foreground">
              <div className="h-px flex-1 bg-border" />
              <span>or create an account with</span>
              <div className="h-px flex-1 bg-border" />
            </div> */}

            {/* Providers */}
            {/* <div className="space-y-4">
              <Button
                type="button"
                variant="ghost"
                className="w-full h-12 rounded-full border-2 border-[var(--nv-royal-purple)] bg-transparent text-[color:var(--nv-royal-purple)]"
                onClick={() => console.log("Signup with Google")}
              >
                <FaGoogle className="mr-2" aria-hidden="true" />
                <span className="nv-gradient-text">Continue with Google</span>
              </Button>
              <Button
                type="button"
                variant="ghost"
                className="w-full h-12 rounded-full border-2 border-[var(--nv-royal-purple)] bg-transparent text-[color:var(--nv-royal-purple)]"
                onClick={() => console.log("Signup with Apple")}
              >
                <FaApple className="mr-2" aria-hidden="true" />
                <span className="nv-gradient-text">Continue with Apple</span>
              </Button>
            </div> */}

            <p className="mt-8 text-center text-sm text-foreground">
              Already have an account?{" "}
              <Link to="/login" className="text-[color:var(--nv-violet-blue)] underline">
                Log in
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
