import type { ParsedImageError } from "@/hooks/use-image-generation";
import { AlertCircle, AlertTriangle, Clock, Loader2 } from "lucide-react";
import { useEffect, useState } from "react";

/**
 * GenerationStatus Component
 * --------------------------
 * Shows a loading spinner with cycling text during image generation,
 * or an inline error message if generation fails.
 *
 * Props:
 * - isLoading: Whether generation is in progress
 * - error: Parsed error object (if any)
 * - onDismissError: Callback to dismiss the error
 */
interface GenerationStatusProps {
	isLoading: boolean;
	error: ParsedImageError | null;
	onDismissError?: () => void;
}

/**
 * Loading messages that cycle during generation.
 * These are fun, encouraging messages to keep users engaged during the wait.
 */
const LOADING_MESSAGES = [
	"Creating your vision...",
	"Mixing colors and ideas...",
	"Bringing your identity to life...",
	"Crafting something special...",
	"Working some AI magic...",
	"Painting with pixels...",
	"Almost there...",
	"Adding the finishing touches...",
	"Generating your masterpiece...",
	"Transforming your prompt...",
	"Building your image...",
	"Processing your request...",
	"Rendering your vision...",
	"Making it beautiful...",
	"Creating art just for you...",
	"Imagining possibilities...",
	"Weaving creativity...",
	"Sculpting your identity...",
];

/**
 * Get a random message from the loading messages array.
 */
function getRandomMessage(): string {
	return LOADING_MESSAGES[Math.floor(Math.random() * LOADING_MESSAGES.length)];
}

/**
 * Get the appropriate icon for the error type.
 */
function getErrorIcon(errorCode: string) {
	switch (errorCode) {
		case "MODEL_OVERLOADED":
		case "RATE_LIMITED":
			return <Clock className="size-4 flex-shrink-0" />;
		case "SAFETY_BLOCK":
		case "BLOCKED_PROMPT":
		case "BLOCKED_RESPONSE":
		case "RECITATION":
			return <AlertTriangle className="size-4 flex-shrink-0" />;
		default:
			return <AlertCircle className="size-4 flex-shrink-0" />;
	}
}

/**
 * Get styling classes based on error type.
 */
function getErrorStyles(errorCode: string) {
	switch (errorCode) {
		case "MODEL_OVERLOADED":
		case "RATE_LIMITED":
			return {
				container: "bg-amber-50 border-amber-200 text-amber-700",
				icon: "text-amber-600",
			};
		case "SAFETY_BLOCK":
		case "BLOCKED_PROMPT":
		case "BLOCKED_RESPONSE":
		case "RECITATION":
			return {
				container: "bg-orange-50 border-orange-200 text-orange-700",
				icon: "text-orange-600",
			};
		default:
			return {
				container: "bg-red-50 border-red-200 text-red-700",
				icon: "text-red-600",
			};
	}
}

export function GenerationStatus({
	isLoading,
	error,
	onDismissError,
}: GenerationStatusProps) {
	const [currentMessage, setCurrentMessage] = useState(getRandomMessage);

	// Cycle through messages every 4 seconds while loading
	useEffect(() => {
		if (!isLoading) return;

		// Set initial message
		setCurrentMessage(getRandomMessage());

		const interval = setInterval(() => {
			setCurrentMessage(getRandomMessage());
		}, 4000);

		return () => clearInterval(interval);
	}, [isLoading]);

	// Show error if present (takes priority over loading)
	if (error) {
		const styles = getErrorStyles(error.errorCode);
		const icon = getErrorIcon(error.errorCode);

		return (
			<div
				className={`flex items-center gap-2 px-3 py-2 rounded-md border text-sm max-w-full ${styles.container}`}
				role="alert"
			>
				<span className={`${styles.icon} flex-shrink-0`}>{icon}</span>
				<span className="flex-1 min-w-0">{error.message}</span>
				{onDismissError && (
					<button
						type="button"
						onClick={onDismissError}
						className="ml-2 text-current opacity-60 hover:opacity-100 transition-opacity flex-shrink-0"
						aria-label="Dismiss error"
					>
						×
					</button>
				)}
			</div>
		);
	}

	// Show loading spinner if loading
	if (isLoading) {
		return (
			<div className="flex items-center gap-3 text-[var(--nv-royal-purple)] w-64">
				<span className="text-sm font-medium animate-pulse text-right flex-1 truncate">
					{currentMessage}
				</span>
				<Loader2 className="size-5 animate-spin flex-shrink-0" />
			</div>
		);
	}

	// Nothing to show
	return null;
}
