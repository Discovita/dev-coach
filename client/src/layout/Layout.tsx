import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import { Outlet } from "react-router-dom";

const Layout = () => {
  return (
    <div className="_Layout flex h-screen w-full flex-col overflow-clip">
      <nav className="relative z-[40] flex-none">
        <Navbar />
      </nav>
      <main className="_Main flex flex-col grow-1 justify-center overflow-auto dark:bg-[#333333]">
        <div className="flex-1 min-h-0 overflow-y-auto">
          <Outlet />
        </div>
      </main>
      <Footer />
    </div>
  );
};

export default Layout;
