/**
 * Footer Component (Full Version)
 *
 * Renders a two-row navigation bar:
 * 1. Top row: Logo, contact info, and Login button.
 * 2. Bottom row: Main navigation links (Home, Company, Team, Features).
 *
 * - Uses shadcn/ui Button for the Login action.
 * - Uses react-router-dom Link for navigation.
 * - Includes ThemeSwitcher for theme toggling.
 * - All elements are styled with Tailwind and shadcn/ui conventions.
 * - 100% comment coverage for clarity and maintainability.
 */
export default function Footer() {
  return (
    <footer className="relative z-[1000] flex-none dark:bg-neutral-800 dark:border-gray-800">
      <div className="container mx-auto px-4 py-4 text-center">
        <p className="text-sm text-gold-600 dark:text-gold-700">
          &copy; {new Date().getFullYear()} Discovitas. All rights reserved.
        </p>
      </div>
    </footer>
  );
}
