import * as React from 'react';

import { cn } from '@/lib/utils';

/**
 * Card component
 * --------------
 * 1. Uses gold theme for background, border, shadow, and radius.
 * 2. Light mode: bg-background, border-gold-200, shadow-gold-md, rounded-xl, generous padding.
 * 3. Dark mode: bg-gold-200, border-gold-700, shadow-gold-md.
 * 4. CardTitle uses text-gold-500 for h1-like emphasis.
 * 5. All other structure and props are preserved.
 */
function Card({ className, ...props }: React.ComponentProps<'div'>) {
  return (
    <div
      data-slot="card"
      className={cn(
        // Gold theme styles
        'bg-white border border-gold-200 rounded-xl shadow-gold-md p-10 mx-auto',
        // Dark mode
        'dark:bg-gold-300 dark:border-gold-700 dark:shadow-gold-md',
        className
      )}
      {...props}
    />
  );
}

function CardHeader({ className, ...props }: React.ComponentProps<'div'>) {
  return (
    <div
      data-slot="card-header"
      className={cn(
        '@container/card-header grid auto-rows-min grid-rows-[auto_auto] items-start gap-1.5 px-0 has-data-[slot=card-action]:grid-cols-[1fr_auto] [.border-b]:pb-6',
        className
      )}
      {...props}
    />
  );
}

function CardTitle({ className, ...props }: React.ComponentProps<'div'>) {
  return (
    <div
      data-slot="card-title"
      className={cn(
        'leading-none font-semibold text-gold-500 dark:text-gold-700 text-2xl mb-4',
        className
      )}
      {...props}
    />
  );
}

function CardDescription({ className, ...props }: React.ComponentProps<'div'>) {
  return (
    <div
      data-slot="card-description"
      className={cn('text-muted-foreground dark:text-gold-800 text-sm mb-4', className)}
      {...props}
    />
  );
}

function CardAction({ className, ...props }: React.ComponentProps<'div'>) {
  return (
    <div
      data-slot="card-action"
      className={cn('col-start-2 row-span-2 row-start-1 self-start justify-self-end', className)}
      {...props}
    />
  );
}

function CardContent({ className, ...props }: React.ComponentProps<'div'>) {
  return (
    <div data-slot="card-content" className={cn('px-0 dark:text-gold-950', className)} {...props} />
  );
}

function CardFooter({ className, ...props }: React.ComponentProps<'div'>) {
  return (
    <div
      data-slot="card-footer"
      className={cn('flex items-center px-0 [.border-t]:pt-6', className)}
      {...props}
    />
  );
}

export { Card, CardHeader, CardFooter, CardTitle, CardAction, CardDescription, CardContent };
