import AdminNavbar from "@/components/AdminNavbar";
import Footer from "@/components/Footer";
import { Outlet, useNavigate } from "react-router-dom";
import LoadingAnimation from "@/components/LoadingAnimation";
import { useReactiveQueryData } from "@/hooks/useReactiveQueryData";
import { User } from "@/types/user";
import { useEffect } from "react";

const AdminLayout = () => {
  const navigate = useNavigate();
  // Use custom hook to reactively get profile and isAdmin from the cache
  const profile = useReactiveQueryData<User>(["user", "profile"]);
  const isAdmin = useReactiveQueryData<boolean>(["user", "isAdmin"]);

  // Redirect if not admin or not logged in
  useEffect(() => {
    if (profile === undefined) return; // Still loading
    if (!profile || !isAdmin) {
      console.log("User is not admin or not logged in");
      navigate("/");
    }
  }, [profile, isAdmin, navigate]);

  // Show loading animation while profile is loading
  if (profile === undefined) {
    return <LoadingAnimation />;
  }

  return (
    <div className="_AdminLayout flex h-screen max-h-screen w-full flex-col overflow-clip">
      <nav className="relative z-[40] flex-none">
        <AdminNavbar />
      </nav>
      {/* Main content area - scrollable container, never exceeds 100vh. Only the Outlet scrolls. */}
      <main className="_Main flex flex-col flex-1 min-h-0 max-h-screen justify-center bg-transparent dark:bg-[#333333]">
        {/* Only the Outlet (page content) scrolls if needed */}
        <div className="_OutletContainer flex-1 min-h-0 overflow-y-auto">
          <Outlet />
        </div>
      </main>
      <Footer />
    </div>
  );
};

export default AdminLayout;
