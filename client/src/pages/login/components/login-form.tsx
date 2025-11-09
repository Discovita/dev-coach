import { useEffect, useState } from "react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Link, useNavigate } from "react-router-dom";
import { FaGoogle, FaApple } from "react-icons/fa";

import { useAuth } from "@/hooks/use-auth";
import { useProfile } from "@/hooks/use-profile";
import { useIsAdmin } from "@/hooks/use-is-admin";
import { FormMessage, Message } from "@/components/FormMessage";

export function LoginForm({
  className,
  ...props
}: React.ComponentProps<"div">) {
  const { login, loginStatus } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState<Message | null>(null);
  const navigate = useNavigate();

  // Get profile and isAdmin using hooks
  const { profile } = useProfile();
  const isAdmin = useIsAdmin();

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setMessage(null);

    try {
      const response = await login({ email, password });
      if (response.success) {
        console.log("Login successful:", response);
        // No redirect here; let the effect below handle it when cache updates
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
        setMessage({ error: errorMsg || "Login failed. Please try again." });
      }
    } catch {
      setMessage({ error: "An unexpected error occurred. Please try again." });
    }
  };

  // Redirect after successful login based on user role, as soon as cache updates
  useEffect(() => {
    if (profile && isAdmin) {
      console.log("Admin logged in successfully. Redirecting to test...");
      navigate("/test");
    } else if (profile) {
      console.log("User logged in successfully. Redirecting to chat...");
      navigate("/chat");
    }
  }, [profile, isAdmin, navigate]);

  return (
    <div
      className={cn(
        "_LoginForm flex flex-col gap-6 mx-auto w-[450px]",
        className
      )}
      {...props}
    >
      {/* Card container with adaptive background and shadow for dark mode */}
      <Card className="w-full bg-card dark:bg-gold-400 shadow-gold-sm dark:shadow-gold-md border border-border dark:border-gold-700">
        <CardHeader className="text-center">
          <CardTitle className="text-xl text-gold-900 dark:text-gold-100">
            Welcome back
          </CardTitle>
          <CardDescription className="text-muted-foreground dark:text-gold-200">
            Login with your Apple or Google account
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit}>
            <div className="grid gap-6">
              <div className="flex flex-col gap-4">
                <Button
                  variant="outline"
                  className="w-full bg-white dark:bg-gold-700/90 dark:text-gold-50 border border-border dark:border-gold-600 hover:dark:bg-gold-600/90"
                >
                  <FaApple className="mr-2" />
                  Login with Apple
                </Button>
                <Button
                  variant="outline"
                  className="w-full bg-white dark:bg-gold-700/90 dark:text-gold-50 border border-border dark:border-gold-600 hover:dark:bg-gold-600/90"
                >
                  <FaGoogle className="mr-2" />
                  Login with Google
                </Button>
              </div>
              {/* Divider with adaptive color */}
              <div className="after:border-border relative text-center text-sm after:absolute after:inset-0 after:top-1/2 after:z-0 after:flex after:items-center after:border-t dark:after:border-gold-700">
                <span className="text-muted-foreground dark:text-gold-200 relative z-10 px-2 bg-gold-50 dark:bg-gold-400">
                  or continue with
                </span>
              </div>
              {/* Email/password fields with gold highlights in dark mode */}
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
                    onChange={(e) => setEmail(e.target.value)}
                    disabled={loginStatus === "pending"}
                    className="bg-background dark:bg-gold-700/40 border border-border dark:border-gold-600 text-foreground dark:text-gold-50 placeholder:text-muted-foreground dark:placeholder:text-gold-300 focus:ring-2 focus:ring-gold-500"
                  />
                </div>
                <div className="grid gap-3">
                  <div className="flex items-center">
                    <Label
                      htmlFor="password"
                      className="text-gold-900 dark:text-gold-100"
                    >
                      Password
                    </Label>
                    <a
                      href="#"
                      className="ml-auto text-sm underline-offset-4 hover:underline text-gold-700 dark:text-gold-200 hover:dark:text-gold-100"
                    >
                      Forgot your password?
                    </a>
                  </div>
                  <Input
                    id="password"
                    type="password"
                    disabled={loginStatus === "pending"}
                    onChange={(e) => setPassword(e.target.value)}
                    className="bg-background dark:bg-gold-700/40 border border-border dark:border-gold-600 text-foreground dark:text-gold-50 placeholder:text-muted-foreground dark:placeholder:text-gold-300 focus:ring-2 focus:ring-gold-500"
                    showPasswordToggle={true}
                  />
                </div>
                <Button
                  type="submit"
                  className="w-full bg-gold-500 hover:bg-gold-600 text-white dark:bg-gold-700 dark:hover:bg-gold-600 dark:text-gold-50 font-semibold shadow-gold-md"
                >
                  Log in
                </Button>
              </div>
              {/* Display error/info messages using FormMessage */}
              {message && <FormMessage message={message} />}
              {/* Signup link with gold hover in dark mode */}
              <div className="text-center text-sm text-muted-foreground dark:text-gold-200">
                Don&apos;t have an account?{" "}
                <Link
                  to="/signup"
                  className="underline underline-offset-4 hover:text-gold-700 dark:hover:text-gold-300"
                >
                  Sign up
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
