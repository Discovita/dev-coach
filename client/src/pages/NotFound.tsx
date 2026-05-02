import { Link } from "@tanstack/react-router";
import { Button } from "@/components/ui/button";

export default function NotFound() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-[var(--nv-lilac-white)]">
      <div className="text-center space-y-8 px-4">
        <div className="space-y-4">
          <h1 className="text-6xl sm:text-7xl font-bold tracking-tight text-black">
            404
          </h1>
          <p className="text-xl sm:text-2xl font-normal text-black">
            Page not found
          </p>
          <p className="text-base sm:text-lg font-normal text-black/70 max-w-md mx-auto">
            The page you're looking for doesn't exist or has been moved.
          </p>
        </div>
        <Button asChild className="nv-gradient-button h-[52px] px-8 text-[20px] rounded-full">
          <Link to="/login">Go to Login</Link>
        </Button>
      </div>
    </div>
  );
}
