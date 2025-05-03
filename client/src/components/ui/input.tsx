import * as React from 'react';

import { cn } from '@/lib/utils';
import { FaEye, FaEyeSlash } from 'react-icons/fa';

/**
 * Input component
 * ------------------
 * 1. Renders a styled input using Tailwind utility classes that map to the app's theme variables.
 * 2. Applies background, border, text, radius, and shadow styles from the theme.
 * 3. Uses a gold border and pill shape in light mode to match the white/gold theme.
 * 4. Supports dark mode by using dark: variants and dark theme variables.
 * 5. Allows additional className overrides via props.
 * 6. Forwards all other input props to the underlying <input> element.
 * 7. If showPasswordToggle is true and type is 'password', renders an eye button to toggle visibility.
 */
interface InputProps extends React.ComponentProps<'input'> {
  /**
   * If true and type is 'password', shows an eye button to toggle password visibility.
   * Used in password fields where users may want to see/hide their input.
   * Example usage: <Input type="password" showPasswordToggle />
   */
  showPasswordToggle?: boolean;
}

function Input({ className, type, showPasswordToggle, ...props }: InputProps) {
  // State to track whether the password is visible or not
  const [show, setShow] = React.useState(false);

  // If showPasswordToggle is true and type is 'password', render the toggle button
  if (showPasswordToggle && type === 'password') {
    return (
      <div className="relative">
        {/* Password input with dynamic type based on show state */}
        <input
          type={show ? 'text' : 'password'}
          data-slot="input"
          className={cn(
            // Base styles
            'text-sm rounded-xl block w-full px-5 py-3 transition-all',
            // Border and background
            'border border-gold-300 bg-gold-50',
            // Text and placeholder
            'text-neutral-600 placeholder-neutral-400',
            // Focus and hover: gold border, no dark border
            'focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-gold-400 focus-visible:border-gold-500',
            'hover:border-gold-500',
            // Dark mode
            'dark:bg-input/30 dark:text-neutral-100 dark:border-neutral-500 dark:placeholder-neutral-400 dark:hover:border-gold-600',
            'dark:focus-visible:ring-gold-600 dark:focus-visible:border-gold-600',
            // Disabled state
            'disabled:cursor-not-allowed disabled:opacity-50 disabled:hover:border-transparent',
            'pr-12', // Add padding to make space for the eye button
            className
          )}
          {...props}
        />
        {/* Eye button to toggle password visibility */}
        <button
          type="button"
          tabIndex={-1}
          aria-label={show ? 'Hide password' : 'Show password'}
          className="absolute right-3 top-1/2 -translate-y-1/2 text-lg text-neutral-400 hover:text-neutral-700 dark:hover:text-neutral-200 focus:outline-none dark:text-gold-50"
          onClick={() => setShow(prev => !prev)}
        >
          {show ? <FaEyeSlash /> : <FaEye />}
        </button>
      </div>
    );
  }

  // Default input rendering (no password toggle)
  return (
    <input
      type={type}
      data-slot="input"
      className={cn(
        // Base styles
        'text-sm rounded-xl block w-full px-5 py-3 transition-all',
        // Border and background
        'border border-gold-300 bg-gold-50',
        // Text and placeholder
        'text-neutral-600 placeholder-neutral-400',
        // Focus and hover: gold border, no dark border
        'focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-gold-400 focus-visible:border-gold-500',
        'hover:border-gold-500',
        // Dark mode
        'dark:bg-input/30 dark:text-neutral-100 dark:border-neutral-500 dark:placeholder-neutral-400 dark:hover:border-gold-600',
        'dark:focus-visible:ring-gold-600 dark:focus-visible:border-gold-600',
        // Disabled state
        'disabled:cursor-not-allowed disabled:opacity-50 disabled:hover:border-transparent',
        className
      )}
      {...props}
    />
  );
}

export { Input };
