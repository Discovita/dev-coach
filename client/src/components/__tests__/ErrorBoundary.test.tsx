import { ErrorBoundary } from "@/components/ErrorBoundary";
import { fireEvent, render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

function ThrowingChild({ shouldThrow }: { shouldThrow: boolean }) {
	if (shouldThrow) throw new Error("Test error");
	return <div>Child content</div>;
}

describe("ErrorBoundary", () => {
	beforeEach(() => {
		vi.spyOn(console, "error").mockImplementation(() => {});
	});

	it("renders children when no error occurs", () => {
		render(
			<ErrorBoundary>
				<div>Hello world</div>
			</ErrorBoundary>,
		);
		expect(screen.getByText("Hello world")).toBeInTheDocument();
	});

	it("renders error UI when child throws", () => {
		render(
			<ErrorBoundary>
				<ThrowingChild shouldThrow={true} />
			</ErrorBoundary>,
		);

		expect(screen.getByText("Something went wrong")).toBeInTheDocument();
		expect(
			screen.getByText(/An unexpected error occurred/),
		).toBeInTheDocument();
		expect(screen.getByText("Try Again")).toBeInTheDocument();
		expect(screen.getByText("Go Home")).toBeInTheDocument();
	});

	it("recovers when Try Again is clicked", () => {
		const { rerender } = render(
			<ErrorBoundary>
				<ThrowingChild shouldThrow={true} />
			</ErrorBoundary>,
		);

		expect(screen.getByText("Something went wrong")).toBeInTheDocument();

		rerender(
			<ErrorBoundary>
				<ThrowingChild shouldThrow={false} />
			</ErrorBoundary>,
		);
		fireEvent.click(screen.getByText("Try Again"));

		expect(screen.queryByText("Something went wrong")).not.toBeInTheDocument();
	});

	it("calls console.error when catching an error", () => {
		render(
			<ErrorBoundary>
				<ThrowingChild shouldThrow={true} />
			</ErrorBoundary>,
		);

		expect(console.error).toHaveBeenCalled();
	});

	it('navigates home when "Go Home" is clicked', () => {
		const originalLocation = window.location.href;
		Object.defineProperty(window, "location", {
			writable: true,
			value: { href: originalLocation },
		});

		render(
			<ErrorBoundary>
				<ThrowingChild shouldThrow={true} />
			</ErrorBoundary>,
		);

		fireEvent.click(screen.getByText("Go Home"));
		expect(window.location.href).toBe("/");
	});
});
