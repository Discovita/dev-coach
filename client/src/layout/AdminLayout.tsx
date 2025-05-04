import AdminNavbar from "@/components/AdminNavbar";
import Footer from "@/components/Footer";
import { Outlet, Navigate } from "react-router-dom";
import { useAuth } from "@/hooks/use-auth";
import LoadingAnimation from "@/components/LoadingAnimation";

const AdminLayout = () => {
  const { user, isAdmin, isLoading } = useAuth();

  // Redirect if not admin
  if (!user || !isAdmin) {
    return <Navigate to="/" replace />;
  }
  return (
    <div className="_AdminLayout flex h-screen w-full flex-col overflow-clip">
      <nav className="relative z-[40] flex-none">
        <AdminNavbar />
      </nav>
      {/* Main content area - scrollable container */}
      <main className="_Main flex flex-col grow-1 justify-center overflow-auto dark:bg-[#333333]">
        {isLoading ? <LoadingAnimation /> : <Outlet />}
      </main>
      <Footer />
    </div>
  );
};

export default AdminLayout;
