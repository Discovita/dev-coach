import AuthNavbar from "@/components/AuthNavbar";
import Footer from "@/components/Footer";
import { Outlet, useNavigate } from "react-router-dom";
import LoadingAnimation from "@/components/LoadingAnimation";
import { useReactiveQueryData } from "@/hooks/useReactiveQueryData";
import { User } from "@/types/user";
import { useEffect } from "react";

const AuthLayout = () => {
  const navigate = useNavigate();
  // Use custom hook to reactively get profile from the cache
  const profile = useReactiveQueryData<User>(["user", "profile"]);

  // Redirect to login if not authenticated
  useEffect(() => {
    if (profile === undefined) return; // Still loading
    if (!profile) {
      console.warn("User is not authenticated, redirecting to login page.");
      navigate("/", { replace: true });
    }
  }, [profile, navigate]);

  // Show loading animation while profile is loading
  if (profile === undefined) {
    return <LoadingAnimation />;
  }

  return (
    <div className="_AuthLayout flex h-screen w-full flex-col overflow-clip">
      <nav className="relative z-[40] flex-none">
        <AuthNavbar />
      </nav>
      {/* Main content area - scrollable container */}
      <main className="_Main flex flex-col grow-1 justify-center overflow-auto dark:bg-[#333333]">
        <Outlet />
      </main>
      <Footer />
    </div>
  );
};

export default AuthLayout;
