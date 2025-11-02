import { useRef, useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";

import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Link } from "react-router-dom";
import { FaGoogle, FaApple } from "react-icons/fa";
import {
  PASSWORD_REGEX,
  EMAIL_REGEX,
} from "@/pages/signup/constants/constants";
import { useAuth } from "@/hooks/use-auth";
import { FormMessage, Message } from "@/components/FormMessage";
import { useProfile } from "@/hooks/use-profile";
import { useIsAdmin } from "@/hooks/use-is-admin";

export function SignupForm({
  className,
  ...props
}: React.ComponentProps<"div">) {
  const { register, registerStatus } = useAuth();
  const { profile } = useProfile();
  const isAdmin = useIsAdmin();
  const navigate = useNavigate();
  const emailRef = useRef<HTMLInputElement>(null);
  const [email, setEmail] = useState("");
  const [validEmail, setValidEmail] = useState(false);
  const [password, setPassword] = useState("");
  const [validPassword, setValidPassword] = useState(false);
  const [matchPassword, setMatchPassword] = useState("");
  const [validMatch, setValidMatch] = useState(false);
  const [registerSuccess, setRegisterSuccess] = useState(false);
  const [message, setMessage] = useState<Message | null>(null);

  // automatically focus the email input field when the component mounts.
  useEffect(() => {
    emailRef.current?.focus();
  }, []);

  useEffect(() => {
    const result = EMAIL_REGEX.test(email);
    setValidEmail(result);
  }, [email]);

  useEffect(() => {
    const result = PASSWORD_REGEX.test(password);
    setValidPassword(result);
    const match = password === matchPassword;
    setValidMatch(match);
  }, [password, matchPassword]);

  useEffect(() => {
    if (profile && isAdmin) {
      console.log("Admin registered successfully. Redirecting to test...");
      navigate("/test");
    } else if (profile) {
      console.log("User registered successfully. Redirecting to chat...");
      navigate("/chat");
    }
  }, [profile, isAdmin, navigate, registerSuccess]);

  // Handle form submission
  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setMessage(null);

    // Client-side validation
    if (!validEmail) {
      setMessage({ error: "Please enter a valid email address." });
      return;
    }
    if (!validPassword) {
      setMessage({ error: "Password does not meet requirements." });
      return;
    }
    if (!validMatch) {
      setMessage({ error: "Passwords do not match." });
      return;
    }

    try {
      const response = await register({ email, password });
      if (response.success) {
        setRegisterSuccess(true);
        setMessage({ success: "Registration successful!" });
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
        setMessage({
          error: errorMsg || "Registration failed. Please try again.",
        });
      }
    } catch {
      setMessage({ error: "An unexpected error occurred. Please try again." });
    }
  };

  return (
    <div
      className={cn(
        "_SignupForm flex flex-col gap-6 mx-auto w-[450px]",
        className
      )}
      {...props}
    >
      {/* Card container with adaptive background and shadow for dark mode */}
      <Card className="w-full bg-card dark:bg-gold-400 shadow-gold-sm dark:shadow-gold-md border border-border dark:border-gold-700">
        <CardHeader className="text-center">
          <CardDescription className="text-muted-foreground dark:text-gold-200">
            Signup with your Apple or Google account
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form className="space-y-6" method="POST" onSubmit={handleSubmit}>
            <div className="grid gap-6">
              {/* Social signup buttons with gold accents in dark mode */}
              <div className="flex flex-col gap-4">
                <Button
                  variant="outline"
                  className="w-full bg-white dark:bg-gold-700/90 dark:text-gold-50 border border-border dark:border-gold-600 hover:dark:bg-gold-600/90"
                >
                  <FaApple className="mr-2" />
                  Signup with Apple
                </Button>
                <Button
                  variant="outline"
                  className="w-full bg-white dark:bg-gold-700/90 dark:text-gold-50 border border-border dark:border-gold-600 hover:dark:bg-gold-600/90"
                >
                  <FaGoogle className="mr-2" />
                  Signup with Google
                </Button>
              </div>
              {/* Divider with adaptive color */}
              <div className="after:border-border relative text-center text-sm after:absolute after:inset-0 after:top-1/2 after:z-0 after:flex after:items-center after:border-t dark:after:border-gold-700">
                <span className="text-muted-foreground dark:text-gold-200 relative z-10 px-2 bg-gold-50 dark:bg-gold-400">
                  or create an account with
                </span>
              </div>
              {/* Email/password fields with gold highlights in dark mode */}{" "}
              <div className="grid gap-6">
                <div className="grid gap-3">
                  <Label
                    htmlFor="email"
                    className="text-gold-900 dark:text-gold-100"
                  >
                    Email
                  </Label>
                  <Input
                    id="email"
                    type="email"
                    placeholder="m@example.com"
                    required
                    ref={emailRef}
                    aria-invalid={validEmail ? "false" : "true"}
                    onChange={(e) => setEmail(e.target.value)}
                    className="bg-background dark:bg-gold-700/40 border border-border dark:border-gold-600 text-foreground dark:text-gold-50 placeholder:text-muted-foreground dark:placeholder:text-gold-300 focus:ring-2 focus:ring-gold-500"
                  />
                </div>
                <div className="grid gap-3">
                  <Label
                    htmlFor="password"
                    className="text-gold-900 dark:text-gold-100"
                  >
                    Password
                  </Label>
                  <Input
                    name="password"
                    type={"password"}
                    id="password"
                    onChange={(e) => setPassword(e.target.value)}
                    required
                    aria-invalid={validPassword ? "false" : "true"}
                    showPasswordToggle
                    className="bg-background dark:bg-gold-700/40 border border-border dark:border-gold-600 text-foreground dark:text-gold-50 placeholder:text-muted-foreground dark:placeholder:text-gold-300 focus:ring-2 focus:ring-gold-500"
                  />
                </div>
                <div className="grid gap-3">
                  <Label
                    htmlFor="confirm_password"
                    className="text-gold-900 dark:text-gold-100"
                  >
                    Confirm Password
                  </Label>
                  <Input
                    name="confirm_password"
                    type={"password"}
                    id="confirm_password"
                    onChange={(e) => setMatchPassword(e.target.value)}
                    required
                    aria-invalid={validMatch ? "false" : "true"}
                    showPasswordToggle
                    className="bg-background dark:bg-gold-700/40 border border-border dark:border-gold-600 text-foreground dark:text-gold-50 placeholder:text-muted-foreground dark:placeholder:text-gold-300 focus:ring-2 focus:ring-gold-500"
                  />
                </div>
                <Button
                  type="submit"
                  className="w-full bg-gold-500 hover:bg-gold-600 text-white dark:bg-gold-700 dark:hover:bg-gold-600 dark:text-gold-50 font-semibold shadow-gold-md"
                >
                  {registerStatus === "pending" ? "Signing Up..." : "Sign up"}
                </Button>
              </div>
              {message && (
                <div className="w-full">
                  <FormMessage message={message} />
                </div>
              )}
              {/* Login link with gold hover in dark mode */}
              <div className="text-center text-sm text-muted-foreground dark:text-gold-200">
                Already have an account?{" "}
                <Link
                  to="/login"
                  className="underline underline-offset-4 hover:text-gold-700 dark:hover:text-gold-300"
                >
                  Log in
                </Link>
              </div>
            </div>
          </form>
        </CardContent>
      </Card>
      {/* Terms and privacy links with gold hover in dark mode */}
      <div className="text-muted-foreground dark:text-gold-300 *:[a]:hover:text-gold-500 dark:*:[a]:hover:text-gold-200 text-center text-xs text-balance *:[a]:underline *:[a]:underline-offset-4">
        By clicking continue, you agree to our{" "}
        <Link to="#">Terms of Service</Link> and{" "}
        <Link to="#">Privacy Policy</Link>.
      </div>
    </div>
  );
}
