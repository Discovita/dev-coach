import * as React from 'react';

import { cn } from '@/lib/utils';

/**
 * Textarea component
 * ------------------
 * 1. Renders a styled textarea using Tailwind utility classes that map to the app's theme variables.
 * 2. Applies background, border, text, radius, and shadow styles from the theme, matching the Input component.
 * 3. Uses a gold border and pill shape in light mode to match the white/gold theme.
 * 4. Supports dark mode by using dark: variants and dark theme variables.
 * 5. Allows additional className overrides via props.
 * 6. Forwards all other textarea props to the underlying <textarea> element.
 */
function Textarea({ className, ...props }: React.ComponentProps<'textarea'>) {
  return (
    <textarea
      data-slot="textarea"
      className={cn(
        // Base styles (match Input)
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
        // Sizing for textarea
        'resize-none min-h-[46px] max-h-[500px] leading-[1.5]',
        className
      )}
      {...props}
    />
  );
}

export { Textarea };
