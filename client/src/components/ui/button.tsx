import * as React from "react";
import { Slot } from "@radix-ui/react-slot";
import { cva, type VariantProps } from "class-variance-authority";

import { cn } from "@/lib/utils";

/**
 * Button component
 * ------------------
 * 1. Renders a styled button using Tailwind utility classes that map to the app's theme variables.
 * 2. Applies a solid gold background, white text, no border, rounded-md, and gold shadow for the default button.
 * 3. Uses deeper gold and larger shadow for hover/focus states.
 * 4. Supports dark mode by using dark: variants and dark theme variables.
 * 5. Allows additional className overrides via props.
 * 6. Forwards all other button props to the underlying <button> element or Slot.
 */
const buttonVariants = cva(
  // Base styles for all buttons
  "inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-md text-sm font-medium transition-colors transition-shadow disabled:pointer-events-none disabled:opacity-50 [&_svg]:pointer-events-none [&_svg:not([class*='size-'])]:size-4 shrink-0 [&_svg]:shrink-0 outline-none cursor-pointer",
  {
    variants: {
      variant: {
        default: cn(
          "bg-gold-500",
          "text-black",
          "border-0",
          "rounded-md",
          "px-2 py-4",
          "font-medium",
          "transition-colors transition-shadow",
          "hover:bg-gold-600 hover:shadow-gold-sm",
          "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-gold-600",
          "dark:bg-gold-600 dark:text-white dark:hover:bg-gold-700"
        ),
        destructive:
          "bg-red-600/90 text-white shadow-xs hover:bg-red-600/70 focus-visible:ring-red-600/20 dark:focus-visible:ring-red-600/40 dark:bg-red-600/60 dark:hover:bg-red-500/60",
        outline: cn(
          "border border-gold-400",
          "bg-background",
          "text-gold-700",
          "hover:bg-gold-50 hover:text-gold-900",
          "dark:bg-gold-950 dark:text-gold-100 dark:border-gold-700",
          "dark:hover:bg-gold-900/50 dark:hover:text-gold-100"
        ),
        secondary: cn(
          "bg-gold-100",
          "text-gold-900",
          "border border-gold-200",
          "hover:bg-gold-200 hover:text-gold-950",
          "dark:bg-gold-800 dark:text-gold-100 dark:border-gold-700",
          "dark:hover:bg-gold-700 dark:hover:text-gold-200"
        ),
        ghost: cn(
          "hover:bg-gold-50 hover:text-gold-900",
          "dark:hover:bg-gold-900/50 dark:hover:text-gold-100"
        ),
        link: "text-gold-700 underline-offset-4 hover:underline dark:text-gold-200",
      },
      size: {
        default: "px-6 py-2",
        xs: "h-5 rounded-md gap-1 px-2 py-3 text-xs",
        sm: "h-9 rounded-md gap-1.5 px-4 text-xs",
        lg: "h-12 rounded-md px-8 text-lg",
        icon: "size-8",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
);

function Button({
  className,
  variant,
  size,
  asChild = false,
  ...props
}: React.ComponentProps<"button"> &
  VariantProps<typeof buttonVariants> & {
    asChild?: boolean;
  }) {
  const Comp = asChild ? Slot : "button";

  return (
    <Comp
      data-slot="button"
      className={cn(buttonVariants({ variant, size, className }))}
      {...props}
    />
  );
}

export { Button, buttonVariants };
