import { UserMessage } from "@/pages/chat/components/UserMessage";
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

describe("UserMessage", () => {
	it("renders children content", () => {
		render(<UserMessage>Hello from user</UserMessage>);
		expect(screen.getByText("Hello from user")).toBeInTheDocument();
	});

	it("applies the _UserMessage class", () => {
		const { container } = render(<UserMessage>Test</UserMessage>);
		const el = container.firstChild as HTMLElement;
		expect(el.className).toContain("_UserMessage");
	});

	it("applies Montserrat font family", () => {
		const { container } = render(<UserMessage>Test</UserMessage>);
		const el = container.firstChild as HTMLElement;
		expect(el.style.fontFamily).toContain("Montserrat");
	});

	it("uses gradient background", () => {
		const { container } = render(<UserMessage>Test</UserMessage>);
		const el = container.firstChild as HTMLElement;
		expect(el.style.background).toContain("--nv-gradient-primary");
	});

	it("passes through additional HTML attributes", () => {
		render(<UserMessage data-testid="user-msg">Test</UserMessage>);
		expect(screen.getByTestId("user-msg")).toBeInTheDocument();
	});

	it("has white text styling", () => {
		const { container } = render(<UserMessage>Test</UserMessage>);
		const el = container.firstChild as HTMLElement;
		expect(el.className).toContain("text-white");
	});
});
