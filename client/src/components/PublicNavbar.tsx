import { Link, useLocation } from "react-router-dom";
import { motion } from "framer-motion";
// import { ThemeSwitcher } from "@/components/ThemeSwitcher";

export default function PublicNavbar() {
  const location = useLocation();
  
  const centerLinks = [
    { label: "Home", to: "/" },
    // Add more links here as needed
  ];

  return (
    <nav className="_PublicNavbar w-full">
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
                      ? "text-gold-900 dark:text-gold-900 font-semibold" 
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
        <div className="flex items-center gap-4 mr-5">
          <div className="flex items-center">
            <div className="flex flex-row font-medium mt-0 space-x-8 rtl:space-x-reverse text-sm">
              <Link
                to="/login"
                className="text-gold-50 dark:text-white hover:underline"
              >
                Login
              </Link>
              <Link
                to="/signup"
                className="text-gold-50 dark:text-white hover:underline"
              >
                Sign Up
              </Link>
            </div>
          </div>
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
