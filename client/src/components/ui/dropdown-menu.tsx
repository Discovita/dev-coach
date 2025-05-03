import * as React from 'react';
import * as DropdownMenuPrimitive from '@radix-ui/react-dropdown-menu';
import { CheckIcon, ChevronRightIcon, CircleIcon } from 'lucide-react';

import { cn } from '@/lib/utils';

function DropdownMenu({ ...props }: React.ComponentProps<typeof DropdownMenuPrimitive.Root>) {
  return <DropdownMenuPrimitive.Root data-slot="dropdown-menu" {...props} />;
}

function DropdownMenuPortal({
  ...props
}: React.ComponentProps<typeof DropdownMenuPrimitive.Portal>) {
  return <DropdownMenuPrimitive.Portal data-slot="dropdown-menu-portal" {...props} />;
}

function DropdownMenuTrigger({
  ...props
}: React.ComponentProps<typeof DropdownMenuPrimitive.Trigger>) {
  return <DropdownMenuPrimitive.Trigger data-slot="dropdown-menu-trigger" {...props} />;
}

function DropdownMenuContent({
  className,
  sideOffset = 4,
  ...props
}: React.ComponentProps<typeof DropdownMenuPrimitive.Content>) {
  return (
    <DropdownMenuPrimitive.Portal>
      <DropdownMenuPrimitive.Content
        data-slot="dropdown-menu-content"
        sideOffset={sideOffset}
        className={cn(
          // Gold theme: background, border, shadow
          'bg-gold-50 text-neutral-600 border border-gold-300 shadow-gold-md',
          // Animation and layout
          'data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95 data-[side=bottom]:slide-in-from-top-2 data-[side=left]:slide-in-from-right-2 data-[side=right]:slide-in-from-left-2 data-[side=top]:slide-in-from-bottom-2 z-50 max-h-(--radix-dropdown-menu-content-available-height) min-w-[8rem] origin-(--radix-dropdown-menu-content-transform-origin) overflow-x-hidden overflow-y-auto rounded-xl p-1',
          // Dark mode
          'dark:bg-gold-200 dark:border-gold-700 dark:shadow-gold-md',
          className
        )}
        {...props}
      />
    </DropdownMenuPrimitive.Portal>
  );
}

function DropdownMenuGroup({ ...props }: React.ComponentProps<typeof DropdownMenuPrimitive.Group>) {
  return <DropdownMenuPrimitive.Group data-slot="dropdown-menu-group" {...props} />;
}

function DropdownMenuItem({
  className,
  inset,
  variant = 'default',
  ...props
}: React.ComponentProps<typeof DropdownMenuPrimitive.Item> & {
  inset?: boolean;
  variant?: 'default' | 'destructive';
}) {
  return (
    <DropdownMenuPrimitive.Item
      data-slot="dropdown-menu-item"
      data-inset={inset}
      data-variant={variant}
      className={cn(
        // Base styles
        "relative flex cursor-default items-center gap-2 rounded-lg px-3 py-2 text-sm outline-hidden select-none data-[disabled]:pointer-events-none data-[disabled]:opacity-50 data-[inset]:pl-8 [&_svg]:pointer-events-none [&_svg]:shrink-0 [&_svg:not([class*='size-'])]:size-4",
        // focus/active states
        'active:bg-gold-400 active:text-gold-950',
        'text-gold-700 focus:bg-gold-500/40 focus:text-gold-800 *:[svg]:!text-gold-700',
        // Dark focus/active states
        'dark:text-gold-700 dark:focus:bg-gold-500/40 dark:focus:text-gold-800 dark:*:[svg]:!text-gold-700',
        // Destructive state
        'data-[variant=destructive]:text-red-500 data-[variant=destructive]:focus:bg-red-500/40 dark:data-[variant=destructive]:focus:bg-red-500/40 data-[variant=destructive]:focus:text-red-500 data-[variant=destructive]:*:[svg]:!text-red-500',
        // Dark Destructive state
        'dark:data-[variant=destructive]:text-red-500 dark:data-[variant=destructive]:focus:bg-red-500/40 dark:data-[variant=destructive]:focus:text-red-500 dark:data-[variant=destructive]:*:[svg]:!text-red-500',
        // Dark mode
        'dark:focus:bg-gold-400 dark:focus:text-gold-800',
        className
      )}
      {...props}
    />
  );
}

function DropdownMenuCheckboxItem({
  className,
  children,
  checked,
  ...props
}: React.ComponentProps<typeof DropdownMenuPrimitive.CheckboxItem>) {
  return (
    <DropdownMenuPrimitive.CheckboxItem
      data-slot="dropdown-menu-checkbox-item"
      className={cn(
        // Base styles
        "relative flex cursor-default items-center gap-2 rounded-lg py-2 pr-3 pl-8 text-sm outline-hidden select-none data-[disabled]:pointer-events-none data-[disabled]:opacity-50 [&_svg]:pointer-events-none [&_svg]:shrink-0 [&_svg:not([class*='size-'])]:size-4",
        // focus/active states
        'active:bg-gold-400 active:text-gold-950',
        'text-gold-700 focus:bg-gold-500/40 focus:text-gold-800 *:[svg]:!text-gold-700',
        // Dark focus/active states
        'dark:text-gold-700 dark:focus:bg-gold-500/40 dark:focus:text-gold-800 dark:*:[svg]:!text-gold-700',
        // Destructive state
        'data-[variant=destructive]:text-red-500 data-[variant=destructive]:focus:bg-red-500/40 dark:data-[variant=destructive]:focus:bg-red-500/40 data-[variant=destructive]:focus:text-red-500 data-[variant=destructive]:*:[svg]:!text-red-500',
        // Dark Destructive state
        'dark:data-[variant=destructive]:text-red-500 dark:data-[variant=destructive]:focus:bg-red-500/40 dark:data-[variant=destructive]:focus:text-red-500 dark:data-[variant=destructive]:*:[svg]:!text-red-500',
        // Dark mode
        'dark:focus:bg-gold-400 dark:focus:text-gold-800',
        className
      )}
      checked={checked}
      {...props}
    >
      <span className="pointer-events-none absolute left-2 flex size-3.5 items-center justify-center">
        <DropdownMenuPrimitive.ItemIndicator>
          <CheckIcon className="size-4 text-gold-500" />
        </DropdownMenuPrimitive.ItemIndicator>
      </span>
      {children}
    </DropdownMenuPrimitive.CheckboxItem>
  );
}

function DropdownMenuRadioGroup({
  ...props
}: React.ComponentProps<typeof DropdownMenuPrimitive.RadioGroup>) {
  return <DropdownMenuPrimitive.RadioGroup data-slot="dropdown-menu-radio-group" {...props} />;
}

function DropdownMenuRadioItem({
  className,
  children,
  ...props
}: React.ComponentProps<typeof DropdownMenuPrimitive.RadioItem>) {
  return (
    <DropdownMenuPrimitive.RadioItem
      data-slot="dropdown-menu-radio-item"
      className={cn(
        // Base styles
        "relative flex cursor-default items-center gap-2 rounded-lg py-2 pr-3 pl-8 text-sm outline-hidden select-none data-[disabled]:pointer-events-none data-[disabled]:opacity-50 [&_svg]:pointer-events-none [&_svg]:shrink-0 [&_svg:not([class*='size-'])]:size-4",
        // focus/active states
        'active:bg-gold-400 active:text-gold-950',
        'text-gold-700 focus:bg-gold-500/40 focus:text-gold-800 *:[svg]:!text-gold-700',
        // Dark focus/active states
        'dark:text-gold-700 dark:focus:bg-gold-500/40 dark:focus:text-gold-800 dark:*:[svg]:!text-gold-700',
        // Destructive state
        'data-[variant=destructive]:text-red-500 data-[variant=destructive]:focus:bg-red-500/40 dark:data-[variant=destructive]:focus:bg-red-500/40 data-[variant=destructive]:focus:text-red-500 data-[variant=destructive]:*:[svg]:!text-red-500',
        // Dark Destructive state
        'dark:data-[variant=destructive]:text-red-500 dark:data-[variant=destructive]:focus:bg-red-500/40 dark:data-[variant=destructive]:focus:text-red-500 dark:data-[variant=destructive]:*:[svg]:!text-red-500',
        // Dark mode
        'dark:focus:bg-gold-400 dark:focus:text-gold-800',
        className
      )}
      {...props}
    >
      <span className="pointer-events-none absolute left-2 flex size-3.5 items-center justify-center">
        <DropdownMenuPrimitive.ItemIndicator>
          <CircleIcon className="size-2 fill-gold-500" />
        </DropdownMenuPrimitive.ItemIndicator>
      </span>
      {children}
    </DropdownMenuPrimitive.RadioItem>
  );
}

function DropdownMenuLabel({
  className,
  inset,
  ...props
}: React.ComponentProps<typeof DropdownMenuPrimitive.Label> & {
  inset?: boolean;
}) {
  return (
    <DropdownMenuPrimitive.Label
      data-slot="dropdown-menu-label"
      data-inset={inset}
      className={cn(
        // Gold theme: label color
        'px-3 py-2 text-sm font-semibold text-gold-700 dark:text-gold-00 data-[inset]:pl-8',
        className
      )}
      {...props}
    />
  );
}

function DropdownMenuSeparator({
  className,
  ...props
}: React.ComponentProps<typeof DropdownMenuPrimitive.Separator>) {
  return (
    <DropdownMenuPrimitive.Separator
      data-slot="dropdown-menu-separator"
      className={cn('bg-gold-200 dark:bg-gold-700 -mx-1 my-1 h-px', className)}
      {...props}
    />
  );
}

function DropdownMenuShortcut({ className, ...props }: React.ComponentProps<'span'>) {
  return (
    <span
      data-slot="dropdown-menu-shortcut"
      className={cn(
        // Gold theme: shortcut color
        'text-gold-400 ml-auto text-xs tracking-widest',
        className
      )}
      {...props}
    />
  );
}

function DropdownMenuSub({ ...props }: React.ComponentProps<typeof DropdownMenuPrimitive.Sub>) {
  return <DropdownMenuPrimitive.Sub data-slot="dropdown-menu-sub" {...props} />;
}

function DropdownMenuSubTrigger({
  className,
  inset,
  children,
  ...props
}: React.ComponentProps<typeof DropdownMenuPrimitive.SubTrigger> & {
  inset?: boolean;
}) {
  return (
    <DropdownMenuPrimitive.SubTrigger
      data-slot="dropdown-menu-sub-trigger"
      data-inset={inset}
      className={cn(
        // Gold theme: focus/active states
        'focus:bg-gold-100 focus:text-gold-900 data-[state=open]:bg-gold-200 data-[state=open]:text-gold-950 dark:focus:bg-gold-400 dark:focus:text-gold-800 dark:data-[state=open]:bg-gold-900 dark:data-[state=open]:text-gold-100',
        // Base styles
        'flex cursor-default items-center rounded-lg px-3 py-2 text-sm outline-hidden select-none data-[inset]:pl-8',
        className
      )}
      {...props}
    >
      {children}
      <ChevronRightIcon className="ml-auto size-4" />
    </DropdownMenuPrimitive.SubTrigger>
  );
}

function DropdownMenuSubContent({
  className,
  ...props
}: React.ComponentProps<typeof DropdownMenuPrimitive.SubContent>) {
  return (
    <DropdownMenuPrimitive.SubContent
      data-slot="dropdown-menu-sub-content"
      className={cn(
        // Gold theme: background, border, shadow
        'bg-gold-50 text-neutral-600 border border-gold-300 shadow-gold-md rounded-xl p-1 dark:bg-gold-200 dark:text-neutral-600-light dark:border-gold-700 dark:shadow-gold-md',
        className
      )}
      {...props}
    />
  );
}

export {
  DropdownMenu,
  DropdownMenuPortal,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuLabel,
  DropdownMenuItem,
  DropdownMenuCheckboxItem,
  DropdownMenuRadioGroup,
  DropdownMenuRadioItem,
  DropdownMenuSeparator,
  DropdownMenuShortcut,
  DropdownMenuSub,
  DropdownMenuSubTrigger,
  DropdownMenuSubContent,
};
