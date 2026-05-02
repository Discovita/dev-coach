import { Link } from "@tanstack/react-router";

/**
 * PublicNavbar
 *
 * Purpose:
 * - Top navigation for public pages (landing, auth)
 * - Used by `PublicLayout` to keep header consistent across pages
 */
export default function PublicNavbar() {
  return (
    <nav className="border-b border-purple-100/50 bg-white/70 backdrop-blur-md sticky top-0 z-50 shadow-sm shadow-purple-500/5">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <Link to="/">
            <div className="flex items-center">
              <div className="h-8 w-8 rounded-full bg-gradient-to-br from-purple-600 to-indigo-600 flex items-center justify-center shadow-lg shadow-purple-500/25">
                <span className="text-white font-bold text-sm">D</span>
              </div>
              <span className="ml-3 text-xl font-bold text-gray-900">
                Discovita
              </span>
            </div>
          </Link>
          <div className="flex items-center space-x-4">
            <Link
              to="/login"
              className="text-gray-600 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium transition-colors"
            >
              Sign In
            </Link>
            <Link
              to="/signup"
              className="bg-gradient-to-r from-purple-600 to-indigo-600 text-white px-4 py-2 rounded-full text-sm font-medium hover:from-purple-700 hover:to-indigo-700 transition-all duration-200 shadow-lg shadow-purple-500/25 hover:shadow-xl hover:shadow-purple-500/30"
            >
              Get Started
            </Link>
          </div>
        </div>
      </div>
    </nav>
  );
}
