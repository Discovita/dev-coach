"use client";

import * as React from "react";
import { X } from "lucide-react";
import { cn } from "@/lib/utils";

import { Badge } from "@/components/ui/badge";
import {
  Command,
  CommandGroup,
  CommandItem,
  CommandList,
} from "@/components/ui/command";
import { Command as CommandPrimitive } from "cmdk";

type MultiSelectOption = Record<"value" | "label", string>;

interface MultiSelectProps {
  /**
   * The list of options to display in the multi-select dropdown.
   * Each option must have a unique value and a label.
   */
  options: MultiSelectOption[];
  /**
   * The current selected values (array of option values). If provided, the component is controlled.
   */
  value?: string[];
  /**
   * Callback when the selected values change. Receives the new array of selected values.
   */
  onValueChange?: (values: string[]) => void;
  /**
   * Placeholder text to display when the input is empty.
   * Defaults to 'Select options...'.
   */
  placeholder?: string;
}

export function MultiSelect({
  options,
  value,
  onValueChange,
  placeholder = "Select options...",
}: MultiSelectProps) {
  const inputRef = React.useRef<HTMLInputElement>(null);
  const [open, setOpen] = React.useState(false);
  // Internal state for uncontrolled mode
  const [selected, setSelected] = React.useState<MultiSelectOption[]>([]);
  const [inputValue, setInputValue] = React.useState("");

  // Determine selected options: controlled or uncontrolled
  const selectedOptions = value
    ? options.filter((o) => value.includes(o.value))
    : selected;

  const handleUnselect = React.useCallback(
    (option: MultiSelectOption) => {
      if (value && onValueChange) {
        // Controlled mode: update parent
        onValueChange(
          selectedOptions
            .filter((s) => s.value !== option.value)
            .map((s) => s.value)
        );
      } else {
        // Uncontrolled mode: update internal state
        setSelected((prev) => prev.filter((s) => s.value !== option.value));
      }
    },
    [value, onValueChange, selectedOptions]
  );

  const handleKeyDown = React.useCallback(
    (e: React.KeyboardEvent<HTMLDivElement>) => {
      const input = inputRef.current;
      if (input) {
        if (e.key === "Delete" || e.key === "Backspace") {
          if (input.value === "") {
            if (value && onValueChange) {
              // Controlled
              onValueChange(selectedOptions.slice(0, -1).map((s) => s.value));
            } else {
              setSelected((prev) => {
                const newSelected = [...prev];
                newSelected.pop();
                return newSelected;
              });
            }
          }
        }
        if (e.key === "Escape") {
          input.blur();
        }
      }
    },
    [value, onValueChange, selectedOptions]
  );

  // Only show options that are not already selected
  const selectables = options.filter(
    (option) => !selectedOptions.some((s) => s.value === option.value)
  );

  const handleSelect = (option: MultiSelectOption) => {
    if (value && onValueChange) {
      // Controlled mode
      onValueChange([...selectedOptions.map((s) => s.value), option.value]);
    } else {
      // Uncontrolled mode
      setSelected((prev) => [...prev, option]);
    }
    setInputValue("");
  };

  return (
    <Command
      onKeyDown={handleKeyDown}
      className={cn(
        "overflow-visible bg-gold-50 text-gold-900 border border-gold-300 rounded-md",
        "focus-within:ring-1 focus-within:ring-gold-400 focus-within:border-gold-500 hover:border-gold-500",
        "dark:bg-gold-100 dark:text-gold-800 dark:border-gold-700 dark:hover:border-gold-600",
        "ring-offset-background focus-within:ring-offset-2"
      )}
    >
      <div
        className={cn(
          "group border border-gold-300 bg-gold-50 text-gold-900 rounded-md px-3 py-2 text-sm",
          "focus-within:ring-1 focus-within:ring-gold-400 focus-within:border-gold-500 hover:border-gold-500",
          "dark:bg-gold-100 dark:text-gold-800 dark:border-gold-700 dark:hover:border-gold-600",
          "ring-offset-background focus-within:ring-offset-2"
        )}
      >
        <div className="flex flex-wrap gap-1">
          {selectedOptions.map((option) => {
            return (
              <Badge
                key={option.value}
                className={cn(
                  "bg-gold-200 text-gold-900 border border-gold-400 rounded-md px-2 py-1 flex items-center gap-1",
                  "dark:bg-gold-300 dark:text-gold-900 dark:border-gold-600"
                )}
              >
                {option.label}
                <button
                  className="ml-1 rounded-full outline-none ring-offset-background focus:ring-2 focus:ring-gold-400 focus:ring-offset-2"
                  onKeyDown={(e) => {
                    if (e.key === "Enter") {
                      handleUnselect(option);
                    }
                  }}
                  onMouseDown={(e) => {
                    e.preventDefault();
                    e.stopPropagation();
                  }}
                  onClick={() => handleUnselect(option)}
                >
                  <X className="h-3 w-3 text-gold-400 hover:text-gold-700" />
                </button>
              </Badge>
            );
          })}
          <CommandPrimitive.Input
            ref={inputRef}
            value={inputValue}
            onValueChange={setInputValue}
            onBlur={() => setOpen(false)}
            onFocus={() => setOpen(true)}
            placeholder={placeholder}
            className="ml-2 flex-1 bg-transparent outline-none placeholder:text-gold-400"
          />
        </div>
      </div>
      <div className="relative">
        <CommandList>
          {open && selectables.length > 0 ? (
            <div
              className={cn(
                "mt-2 absolute top-0 z-10 w-full rounded-md border bg-gold-50 text-gold-900 border-gold-400 shadow-gold-md outline-none animate-in",
                "dark:bg-gold-300 dark:text-gold-900 border dark:border-gold-600 dark:shadow-gold-md"
              )}
            >
              <CommandGroup className="h-full overflow-auto">
                {selectables.map((option) => {
                  return (
                    <CommandItem
                      key={option.value}
                      onMouseDown={(e) => {
                        e.preventDefault();
                        e.stopPropagation();
                      }}
                      onSelect={() => handleSelect(option)}
                      className={cn(
                        "cursor-pointer px-2 py-1.5 rounded-md text-sm",
                        "focus:bg-gold-500 data-[state=checked]:bg-gold-200 data-[highlighted]:bg-gold-100",
                        "dark:focus:bg-gold-500 dark:data-[state=checked]:bg-gold-600 dark:data-[state=checked]:text-gold-50 dark:data-[highlighted]:bg-gold-500"
                      )}
                    >
                      {option.label}
                    </CommandItem>
                  );
                })}
              </CommandGroup>
            </div>
          ) : null}
        </CommandList>
      </div>
    </Command>
  );
}
