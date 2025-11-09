import { Link, useNavigate, useLocation } from "react-router-dom";
import { motion } from "framer-motion";
// import { ThemeSwitcher } from "@/components/ThemeSwitcher";
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
} from "@/components/ui/dropdown-menu";
import { Button } from "./ui/button";
import { useAuth } from "@/hooks/use-auth";
import { User2 } from "lucide-react";

export default function AuthNavbar() {
  const location = useLocation();
  
  const centerLinks = [
    { label: "Home", to: "/" },
    { label: "Chat", to: "/chat" },
    // Add more links here as needed
  ];

  const { logout } = useAuth();
  const navigate = useNavigate();

  const handleSignOut = async () => {
    await logout();
    navigate("/");
  };

  return (
    <nav className="_AuthNavbar w-full">
      <div className="flex flex-wrap justify-between items-center mx-auto p-2 bg-gold-600 border-b border-gray-200 dark:bg-neutral-800 dark:border-gray-800">
        <Link
          to="/"
          className="flex items-center space-x-3 rtl:space-x-reverse"
        >
          <span className="self-center text-2xl font-semibold whitespace-nowrap text-gold-50 dark:text-gold-600 ml-5">
            Coach
          </span>
        </Link>
        <div className="flex items-center">
          <div className="flex flex-row font-medium mt-0 space-x-8 rtl:space-x-reverse text-sm">
            {centerLinks.map((link) => (
              <motion.div
                key={link.to}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                transition={{ type: "spring", stiffness: 400, damping: 17 }}
              >
                <Link
                  to={link.to}
                  className={`relative text-gold-50 dark:text-white hover:underline px-3 py-2 rounded-lg transition-colors ${
                    location.pathname === link.to 
                      ? "text-gold-800 dark:text-gold-900 font-semibold" 
                      : "hover:bg-gold-500/20"
                  }`}
                  aria-current={location.pathname === link.to ? "page" : undefined}
                >
                  {location.pathname === link.to && (
                    <motion.div
                      className="absolute inset-0 bg-gold-200 dark:bg-gold-300 rounded-lg"
                      layoutId="activeTab"
                      transition={{ type: "spring", stiffness: 500, damping: 30 }}
                    />
                  )}
                  <span className="relative z-10">{link.label}</span>
                </Link>
              </motion.div>
            ))}
          </div>
        </div>
        <div className="flex items-center gap-4">
          {/* User menu dropdown - provides user options such as sign out */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline" className="flex items-center gap-2">
                <User2 className="w-4 h-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem
                onClick={handleSignOut}
                className="cursor-pointer"
              >
                Log out
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
          {/* <div className="flex items-center">
            <div className="flex flex-row font-medium mt-0 space-x-8 rtl:space-x-reverse text-sm">
              <ThemeSwitcher />
            </div>
          </div> */}
        </div>
      </div>
    </nav>
  );
}
