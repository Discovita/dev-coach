import AdminNavbar from "@/components/AdminNavbar";
import Footer from "@/components/Footer";
import { Outlet, useNavigate } from "react-router-dom";
import { useAuth } from "@/hooks/use-auth";
import LoadingAnimation from "@/components/LoadingAnimation";

const AdminLayout = () => {
  const navigate = useNavigate();
  const { user, isAdmin, isLoading } = useAuth();

  // Redirect if not admin
  if (!user || !isAdmin) {
    console.log("User is not admin or not logged in");
    navigate("/");
  }
  return (
    <div className="_AdminLayout flex h-screen max-h-screen w-full flex-col overflow-clip">
      <nav className="relative z-[40] flex-none">
        <AdminNavbar />
      </nav>
      {/* Main content area - scrollable container, never exceeds 100vh. Only the Outlet scrolls. */}
      <main className="_Main flex flex-col flex-1 min-h-0 max-h-screen justify-center bg-transparent dark:bg-[#333333]">
        {/* Only the Outlet (page content) scrolls if needed */}
        <div className="flex-1 min-h-0 overflow-y-auto">
          {isLoading ? <LoadingAnimation /> : <Outlet />}
        </div>
      </main>
      <Footer />
    </div>
  );
};

export default AdminLayout;
