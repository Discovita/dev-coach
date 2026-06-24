import { CoachMessage } from "@/pages/chat/components/CoachMessage";
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

describe("CoachMessage", () => {
	it("renders children content", () => {
		render(<CoachMessage>Hello from coach</CoachMessage>);
		expect(screen.getByText("Hello from coach")).toBeInTheDocument();
	});

	it("applies the _CoachMessage class", () => {
		const { container } = render(<CoachMessage>Test</CoachMessage>);
		const el = container.firstChild as HTMLElement;
		expect(el.className).toContain("_CoachMessage");
	});

	it("applies Montserrat font family", () => {
		const { container } = render(<CoachMessage>Test</CoachMessage>);
		const el = container.firstChild as HTMLElement;
		expect(el.style.fontFamily).toContain("Montserrat");
	});

	it("uses pale lavender background", () => {
		const { container } = render(<CoachMessage>Test</CoachMessage>);
		const el = container.firstChild as HTMLElement;
		expect(el.style.backgroundColor).toContain("--nv-pale-lavender");
	});

	it("passes through additional HTML attributes", () => {
		render(<CoachMessage data-testid="coach-msg">Test</CoachMessage>);
		expect(screen.getByTestId("coach-msg")).toBeInTheDocument();
	});
});
