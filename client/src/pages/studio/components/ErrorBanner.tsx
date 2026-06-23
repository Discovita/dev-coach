import { X, AlertCircle, RefreshCw, AlertTriangle, Clock } from "lucide-react";
import { Button } from "@/components/ui/button";
import type { ParsedImageError } from "@/hooks/use-image-generation";

/**
 * ErrorBanner Component
 * --------------------
 * Displays a persistent error message with dismiss button.
 * Shows different icons and styling based on error type.
 * 
 * Props:
 * - error: Parsed error object with message, code, and retryability
 * - onDismiss: Callback when user clicks the X button
 * - onRetry: Optional callback for retry button (shown for retryable errors)
 * - isRetrying: Whether a retry is in progress
 */
interface ErrorBannerProps {
  error: ParsedImageError;
  onDismiss: () => void;
  onRetry?: () => void;
  isRetrying?: boolean;
}

/**
 * Get the appropriate icon for the error type.
 */
function getErrorIcon(errorCode: string) {
  switch (errorCode) {
    case "MODEL_OVERLOADED":
    case "RATE_LIMITED":
      return <Clock className="size-5 flex-shrink-0" />;
    case "SAFETY_BLOCK":
    case "BLOCKED_PROMPT":
    case "BLOCKED_RESPONSE":
    case "RECITATION":
      return <AlertTriangle className="size-5 flex-shrink-0" />;
    default:
      return <AlertCircle className="size-5 flex-shrink-0" />;
  }
}

/**
 * Get styling classes based on error type.
 */
function getErrorStyles(errorCode: string) {
  switch (errorCode) {
    case "MODEL_OVERLOADED":
    case "RATE_LIMITED":
      // Yellow/amber for temporary issues
      return {
        container: "bg-amber-50 border-amber-300",
        icon: "text-amber-600",
        title: "text-amber-800",
        message: "text-amber-700",
        dismissButton: "text-amber-500 hover:text-amber-700 hover:bg-amber-100",
      };
    case "SAFETY_BLOCK":
    case "BLOCKED_PROMPT":
    case "BLOCKED_RESPONSE":
    case "RECITATION":
      // Orange for content policy issues
      return {
        container: "bg-orange-50 border-orange-300",
        icon: "text-orange-600",
        title: "text-orange-800",
        message: "text-orange-700",
        dismissButton: "text-orange-500 hover:text-orange-700 hover:bg-orange-100",
      };
    default:
      // Red for general errors
      return {
        container: "bg-red-50 border-red-300",
        icon: "text-red-600",
        title: "text-red-800",
        message: "text-red-700",
        dismissButton: "text-red-500 hover:text-red-700 hover:bg-red-100",
      };
  }
}

/**
 * Get a title for the error based on error code.
 */
function getErrorTitle(errorCode: string): string {
  switch (errorCode) {
    case "MODEL_OVERLOADED":
      return "Model Temporarily Unavailable";
    case "RATE_LIMITED":
      return "Rate Limit Reached";
    case "SAFETY_BLOCK":
      return "Content Blocked by Safety Filters";
    case "BLOCKED_PROMPT":
      return "Prompt Blocked";
    case "BLOCKED_RESPONSE":
      return "Response Blocked";
    case "RECITATION":
      return "Copyright Concern Detected";
    case "EMPTY_RESPONSE":
      return "No Image Generated";
    default:
      return "Image Generation Failed";
  }
}

export function ErrorBanner({
  error,
  onDismiss,
  onRetry,
  isRetrying = false,
}: ErrorBannerProps) {
  const styles = getErrorStyles(error.errorCode);
  const icon = getErrorIcon(error.errorCode);
  const title = getErrorTitle(error.errorCode);

  return (
    <div
      className={`relative p-4 border rounded-lg ${styles.container}`}
      role="alert"
    >
      {/* Dismiss button */}
      <button
        onClick={onDismiss}
        className={`absolute top-2 right-2 p-1 rounded-md transition-colors ${styles.dismissButton}`}
        aria-label="Dismiss error"
      >
        <X className="size-4" />
      </button>

      <div className="flex items-start gap-3 pr-8">
        <div className={styles.icon}>{icon}</div>
        <div className="flex-1 min-w-0">
          <h3 className={`font-semibold ${styles.title}`}>{title}</h3>
          <p className={`mt-1 text-sm ${styles.message}`}>{error.message}</p>
          
          {/* Show retry button for retryable errors */}
          {error.isRetryable && onRetry && (
            <Button
              variant="outline"
              size="sm"
              onClick={onRetry}
              disabled={isRetrying}
              className="mt-3"
            >
              {isRetrying ? (
                <>
                  <RefreshCw className="size-4 animate-spin mr-2" />
                  Retrying...
                </>
              ) : (
                <>
                  <RefreshCw className="size-4 mr-2" />
                  Try Again
                </>
              )}
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}
