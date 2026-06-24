import { Button } from "@/components/ui/button";
import { Component } from "react";
import type { ErrorInfo, ReactNode } from "react";

interface ErrorBoundaryProps {
	children: ReactNode;
}

interface ErrorBoundaryState {
	hasError: boolean;
	error: Error | null;
}

/**
 * Global error boundary that catches unhandled render errors and
 * displays a recovery UI instead of blanking the entire app.
 *
 * Mounted at the root route level in `src/routes/__root.tsx`.
 */
export class ErrorBoundary extends Component<
	ErrorBoundaryProps,
	ErrorBoundaryState
> {
	constructor(props: ErrorBoundaryProps) {
		super(props);
		this.state = { hasError: false, error: null };
	}

	static getDerivedStateFromError(error: Error): ErrorBoundaryState {
		return { hasError: true, error };
	}

	componentDidCatch(error: Error, errorInfo: ErrorInfo) {
		console.error("ErrorBoundary caught:", error, errorInfo);
	}

	handleReset = () => {
		this.setState({ hasError: false, error: null });
	};

	render() {
		if (this.state.hasError) {
			return (
				<div className="min-h-screen flex items-center justify-center bg-[var(--nv-lilac-white)]">
					<div className="text-center space-y-8 px-4">
						<div className="space-y-4">
							<h1 className="text-4xl sm:text-5xl font-bold tracking-tight text-black">
								Something went wrong
							</h1>
							<p className="text-base sm:text-lg font-normal text-black/70 max-w-md mx-auto">
								An unexpected error occurred. Please try again.
							</p>
						</div>
						<div className="flex gap-4 justify-center">
							<Button
								onClick={this.handleReset}
								className="nv-gradient-button h-[52px] px-8 text-[20px] rounded-full"
							>
								Try Again
							</Button>
							<Button
								onClick={() => {
									window.location.href = "/";
								}}
								variant="outline"
								className="h-[52px] px-8 text-[20px] rounded-full"
							>
								Go Home
							</Button>
						</div>
					</div>
				</div>
			);
		}

		return this.props.children;
	}
}
