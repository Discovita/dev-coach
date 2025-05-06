import * as React from "react"
import { Slot } from "@radix-ui/react-slot"
import { cva, type VariantProps } from "class-variance-authority"

import { cn } from "@/lib/utils"

// Custom badge variants for Discovita gold/neutral theme
const badgeVariants = cva(
  // Base styles for all badges
  "inline-flex items-center justify-center rounded-md border px-2 py-0.5 text-xs font-medium w-fit whitespace-nowrap shrink-0 [&>svg]:size-3 gap-1 [&>svg]:pointer-events-none focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:ring-[3px] aria-invalid:ring-destructive/20 dark:aria-invalid:ring-destructive/40 aria-invalid:border-destructive transition-[color,box-shadow] overflow-hidden",
  {
    variants: {
      variant: {
        // Gold primary badge (default)
        default:
          // Gold background, white text, subtle border
          "border-gold-400 bg-gold-500 text-white [a&]:hover:bg-gold-600 dark:bg-gold-600 dark:text-gold-50 dark:border-gold-700",
        // Secondary badge: lighter gold background, gold text
        secondary:
          // Lighter gold background, gold text, gold border
          "border-gold-300 bg-gold-100 text-gold-800 [a&]:hover:bg-gold-200 dark:bg-gold-200 dark:text-gold-900 dark:border-gold-400",
        // Destructive badge: red background, white text
        destructive:
          "border-transparent bg-destructive text-white [a&]:hover:bg-destructive/90 focus-visible:ring-destructive/20 dark:focus-visible:ring-destructive/40 dark:bg-destructive/60",
        outline:
          // Transparent, gold border, gold text
          "bg-transparent border-gold-400 text-gold-700 [a&]:hover:bg-gold-50 [a&]:hover:text-gold-900 dark:text-gold-200 dark:border-gold-500 dark:[a&]:hover:bg-gold-900 dark:[a&]:hover:text-gold-50",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
)

function Badge({
  className,
  variant,
  asChild = false,
  ...props
}: React.ComponentProps<"span"> &
  VariantProps<typeof badgeVariants> & { asChild?: boolean }) {
  const Comp = asChild ? Slot : "span"

  return (
    <Comp
      data-slot="badge"
      className={cn(badgeVariants({ variant }), className)}
      {...props}
    />
  )
}

export { Badge, badgeVariants }
