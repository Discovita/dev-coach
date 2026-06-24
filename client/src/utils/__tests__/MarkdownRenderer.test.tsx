import MarkdownRenderer from "@/utils/MarkdownRenderer";
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

describe("MarkdownRenderer", () => {
	it("renders plain text content", () => {
		render(<MarkdownRenderer content="Hello world" />);
		expect(screen.getByText("Hello world")).toBeInTheDocument();
	});

	it("renders markdown bold text", () => {
		render(<MarkdownRenderer content="This is **bold** text" />);
		const bold = screen.getByText("bold");
		expect(bold.tagName).toBe("STRONG");
	});

	it("renders markdown italic text", () => {
		render(<MarkdownRenderer content="This is *italic* text" />);
		const italic = screen.getByText("italic");
		expect(italic.tagName).toBe("EM");
	});

	it("renders markdown lists", () => {
		const content = ["- Item 1", "- Item 2", "- Item 3"].join("\n");
		render(<MarkdownRenderer content={content} />);
		expect(screen.getByText("Item 1")).toBeInTheDocument();
		expect(screen.getByText("Item 2")).toBeInTheDocument();
		expect(screen.getByText("Item 3")).toBeInTheDocument();
	});

	it("applies className to wrapper div", () => {
		const { container } = render(
			<MarkdownRenderer content="test" className="custom-class" />,
		);
		expect(container.firstChild).toHaveClass("custom-class");
	});

	it("sanitizes dangerous HTML (script tags)", () => {
		const { container } = render(
			<MarkdownRenderer content='<script>alert("xss")</script>Hello' />,
		);
		expect(container.innerHTML).not.toContain("<script>");
		expect(screen.getByText("Hello")).toBeInTheDocument();
	});

	it("sanitizes onclick attributes", () => {
		const { container } = render(
			<MarkdownRenderer content='<div onclick="alert(1)">Click me</div>' />,
		);
		expect(container.innerHTML).not.toContain("onclick");
	});
});
