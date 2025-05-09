import { Link, useNavigate } from "react-router-dom";
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

export default function AdminNavbar() {
  const centerLinks = [
    { label: "Home", to: "/", ariaCurrent: true },
    { label: "Chat", to: "/chat" },
    { label: "Test", to: "/test" },
    { label: "Prompts", to: "/prompts" },
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
