import { Link } from "react-router-dom";
// import { ThemeSwitcher } from "@/components/ThemeSwitcher";

export default function Navbar() {
  const centerLinks = [
    { label: "Home", to: "/", ariaCurrent: true },
    { label: "Chat", to: "/chat" },
    // Add more links here as needed
  ];

  return (
    <nav className="_Navbar w-full">
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
              <Link
                key={link.to}
                to={link.to}
                className="text-gold-50 dark:text-white hover:underline"
                aria-current={link.ariaCurrent ? "page" : undefined}
              >
                {link.label}
              </Link>
            ))}
          </div>
        </div>
        <div className="flex items-center gap-4">
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
