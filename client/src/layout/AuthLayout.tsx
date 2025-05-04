import AuthNavbar from "@/components/AuthNavbar";
import Footer from "@/components/Footer";
import { Outlet, Navigate } from "react-router-dom";
import { useAuth } from "@/hooks/use-auth";
import LoadingAnimation from "@/components/LoadingAnimation";

const AuthLayout = () => {
  const { user, isLoading } = useAuth();

  if (!user && !isLoading) {
    console.warn("User is not authenticated, redirecting to login page.");
    return <Navigate to="/" replace />;
  }
  return (
    <div className="_AuthLayout flex h-screen w-full flex-col overflow-clip">
      <nav className="relative z-[40] flex-none">
        <AuthNavbar />
      </nav>
      {/* Main content area - scrollable container */}
      <main className="_Main flex flex-col grow-1 justify-center overflow-auto dark:bg-[#333333]">
        {isLoading ? <LoadingAnimation /> : <Outlet />}
      </main>
      <Footer />
    </div>
  );
};

export default AuthLayout;
