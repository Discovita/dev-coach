"use client";

import { cn } from "@/lib/utils";
import { X } from "lucide-react";
import * as React from "react";

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

/**
 * Multi-select dropdown built on top of shadcn's Command component.
 * Supports both controlled (value + onValueChange) and uncontrolled modes.
 *
 * Ported from: dev-coach/client/src/components/ui/multi-select.tsx
 * Adapted from gold theme to use shadcn semantic CSS variables.
 */
export function MultiSelect({
	options,
	value,
	onValueChange,
	placeholder = "Select options...",
}: MultiSelectProps) {
	const inputRef = React.useRef<HTMLInputElement>(null);
	const [open, setOpen] = React.useState(false);
	const [selected, setSelected] = React.useState<MultiSelectOption[]>([]);
	const [inputValue, setInputValue] = React.useState("");

	const selectedOptions = value
		? options.filter((o) => value.includes(o.value))
		: selected;

	const handleUnselect = React.useCallback(
		(option: MultiSelectOption) => {
			if (value && onValueChange) {
				onValueChange(
					selectedOptions
						.filter((s) => s.value !== option.value)
						.map((s) => s.value),
				);
			} else {
				setSelected((prev) => prev.filter((s) => s.value !== option.value));
			}
		},
		[value, onValueChange, selectedOptions],
	);

	const handleKeyDown = React.useCallback(
		(e: React.KeyboardEvent<HTMLDivElement>) => {
			const input = inputRef.current;
			if (input) {
				if (e.key === "Delete" || e.key === "Backspace") {
					if (input.value === "") {
						if (value && onValueChange) {
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
		[value, onValueChange, selectedOptions],
	);

	const selectables = options.filter(
		(option) => !selectedOptions.some((s) => s.value === option.value),
	);

	const handleSelect = (option: MultiSelectOption) => {
		if (value && onValueChange) {
			onValueChange([...selectedOptions.map((s) => s.value), option.value]);
		} else {
			setSelected((prev) => [...prev, option]);
		}
		setInputValue("");
	};

	return (
		<Command
			onKeyDown={handleKeyDown}
			className={cn(
				"overflow-visible bg-background text-foreground border border-input rounded-md",
				"focus-within:ring-1 focus-within:ring-ring focus-within:border-ring hover:border-ring",
				"ring-offset-background focus-within:ring-offset-2",
			)}
		>
			<div
				className={cn(
					"group border border-input bg-background text-foreground rounded-md px-3 py-2 text-sm",
					"focus-within:ring-1 focus-within:ring-ring focus-within:border-ring hover:border-ring",
					"ring-offset-background focus-within:ring-offset-2",
				)}
			>
				<div className="flex flex-wrap gap-1">
					{selectedOptions.map((option) => {
						return (
							<Badge
								key={option.value}
								variant="secondary"
								className="rounded-md px-2 py-1 flex items-center gap-1"
							>
								{option.label}
								<button
									type="button"
									className="ml-1 rounded-full outline-none ring-offset-background focus:ring-2 focus:ring-ring focus:ring-offset-2"
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
									<X className="h-3 w-3 text-muted-foreground hover:text-foreground" />
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
						className="ml-2 flex-1 bg-transparent outline-none placeholder:text-muted-foreground"
					/>
				</div>
			</div>
			<div className="relative">
				<CommandList>
					{open && selectables.length > 0 ? (
						<div
							className={cn(
								"mt-2 absolute top-0 z-10 w-full rounded-md border bg-popover text-popover-foreground border-border shadow-md outline-none animate-in",
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
											className="cursor-pointer"
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
