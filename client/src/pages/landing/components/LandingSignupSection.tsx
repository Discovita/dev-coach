/**
 * LandingSignupSection
 *
 * Purpose:
 * - Signup form section for the landing page based on Figma Option 3 design
 * - Features fully functional email/password/confirmPassword form using TanStack Form
 * - Integrates with useAuth hook for registration
 * - Redirects users after successful registration to /chat
 * - Uses existing brand tokens and gradient helpers
 *
 * Validation:
 * - Email: simple format check
 * - Password: at least 6 characters
 * - Confirm Password: must match password
 */

import { useForm } from "@tanstack/react-form";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useNavigate } from "@tanstack/react-router";
import { useState, useEffect } from "react";
import { useAuth } from "@/hooks/use-auth";
import { useProfile } from "@/hooks/use-profile";

export default function LandingSignupSection() {
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
    <div className="bg-white flex flex-col gap-12 sm:gap-16 md:gap-20 lg:gap-[100px] items-center p-4 sm:p-6 md:p-12 lg:p-16 xl:p-[100px] relative shrink-0 w-full">
      <div className="flex flex-col gap-6 sm:gap-8 items-start relative shrink-0 w-full max-w-[500px]">
        {/* Headline */}
        <div className="flex flex-col gap-2 items-center relative shrink-0 w-full">
          <p className="font-medium leading-[1.4] relative shrink-0 text-xl sm:text-2xl md:text-3xl lg:text-[36px] text-black text-center w-full">
            Create your account, free for the first 30 days, no credit card required
          </p>
        </div>

        {/* Form */}
        <form
          className="space-y-6 w-full"
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
              Create your account
            </Button>
          </div>
        </form>

        {/* Divider and social buttons */}
        <div className="flex flex-col gap-6 sm:gap-8 items-center relative shrink-0 w-full">
          {/* "or" divider */}
          {/* <div className="relative w-full flex items-center justify-center">
            <div className="flex-1 h-px bg-black/20" />
            <p className="px-4 font-medium leading-[1.5] relative text-sm sm:text-base md:text-lg lg:text-[18px] text-black/50 text-center whitespace-pre">
              or
            </p>
            <div className="flex-1 h-px bg-black/20" />
          </div> */}

          {/* Social login buttons */}
          {/* <div className="flex flex-col gap-4 sm:gap-6 items-start relative shrink-0 w-full">
            <Link
              to="/signup"
              className="border-2 border-[var(--nv-royal-purple)] border-solid relative rounded-full shrink-0 w-full"
            >
              <div className="flex gap-2 sm:gap-[10px] items-center justify-center overflow-hidden px-6 sm:px-8 py-3 sm:py-4 relative rounded-[inherit] w-full">
                <p className="nv-gradient-text font-semibold leading-none relative shrink-0 text-base sm:text-lg md:text-[20px] text-nowrap whitespace-pre">
                  Continue with Google
                </p>
              </div>
            </Link>
            <Link
              to="/signup"
              className="border-2 border-[var(--nv-royal-purple)] border-solid relative rounded-full shrink-0 w-full"
            >
              <div className="flex gap-2 sm:gap-[10px] items-center justify-center overflow-hidden px-6 sm:px-8 py-3 sm:py-4 relative rounded-[inherit] w-full">
                <p className="nv-gradient-text font-semibold leading-none relative shrink-0 text-base sm:text-lg md:text-[20px] text-nowrap whitespace-pre">
                  Continue with Apple
                </p>
              </div>
            </Link>
          </div> */}
        </div>
      </div>
    </div>
  );
}

