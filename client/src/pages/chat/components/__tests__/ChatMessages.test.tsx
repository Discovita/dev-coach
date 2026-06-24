import { ComponentType } from "@/enums/componentType";
import { ChatMessages } from "@/pages/chat/components/ChatMessages";
import type { ComponentConfig } from "@/types/componentConfig";
import type { Message } from "@/types/message";
import { render, screen } from "@testing-library/react";
import { createRef } from "react";
import { describe, expect, it, vi } from "vitest";

vi.mock("@/utils/MarkdownRenderer", () => ({
	default: ({ content }: { content: string }) => (
		<span data-testid="markdown">{content}</span>
	),
}));

vi.mock("@/pages/chat/components/CoachMessage", () => ({
	CoachMessage: ({ children }: { children: React.ReactNode }) => (
		<div data-testid="coach-message">{children}</div>
	),
}));

vi.mock("@/pages/chat/components/UserMessage", () => ({
	UserMessage: ({ children }: { children: React.ReactNode }) => (
		<div data-testid="user-message">{children}</div>
	),
}));

vi.mock("@/pages/chat/components/LoadingBubbles", () => ({
	LoadingBubbles: () => <div data-testid="loading-bubbles" />,
}));

vi.mock(
	"@/pages/chat/components/coach-message-with-component/CoachMessageWithComponent",
	() => ({
		CoachMessageWithComponent: ({
			children,
		}: { children: React.ReactNode }) => (
			<div data-testid="coach-with-component">{children}</div>
		),
	}),
);

const mockOnSend = vi.fn();

function renderChatMessages(
	messages: Message[],
	options: {
		isProcessingMessage?: boolean;
		componentConfig?: ComponentConfig | null;
	} = {},
) {
	const messagesEndRef = createRef<HTMLDivElement>();
	return render(
		<ChatMessages
			messages={messages}
			isProcessingMessage={options.isProcessingMessage ?? false}
			messagesEndRef={messagesEndRef}
			componentConfig={options.componentConfig ?? null}
			onSendUserMessageToCoach={mockOnSend}
		/>,
	);
}

const sessionVideoConfig: ComponentConfig = {
	component_type: ComponentType.SESSION_VIDEO,
	video_key: "welcome_session_intro",
	video_name: "Welcome",
	video_url: "https://example.com/welcome.mov",
	buttons: [{ label: "Continue", actions: [] }],
};

const combineIdentitiesConfig: ComponentConfig = {
	component_type: ComponentType.COMBINE_IDENTITIES,
};

describe("ChatMessages", () => {
	it("renders user messages with UserMessage component", () => {
		renderChatMessages([
			{
				role: "user",
				content: "Hello coach",
				timestamp: "2025-01-01T00:00:00Z",
			},
		]);
		expect(screen.getByTestId("user-message")).toBeInTheDocument();
		expect(screen.getByText("Hello coach")).toBeInTheDocument();
	});

	it("renders coach messages with CoachMessage component", () => {
		renderChatMessages([
			{ role: "coach", content: "Welcome!", timestamp: "2025-01-01T00:00:00Z" },
		]);
		expect(screen.getByTestId("coach-message")).toBeInTheDocument();
		expect(screen.getByText("Welcome!")).toBeInTheDocument();
	});

	it("renders multiple messages in order", () => {
		renderChatMessages([
			{ role: "user", content: "Hi", timestamp: "2025-01-01T00:00:00Z" },
			{ role: "coach", content: "Hello!", timestamp: "2025-01-01T00:00:01Z" },
			{
				role: "user",
				content: "How are you?",
				timestamp: "2025-01-01T00:00:02Z",
			},
		]);
		expect(screen.getAllByTestId("user-message")).toHaveLength(2);
		expect(screen.getAllByTestId("coach-message")).toHaveLength(1);
	});

	it("shows loading bubbles when processing", () => {
		renderChatMessages(
			[{ role: "user", content: "Hello", timestamp: "2025-01-01T00:00:00Z" }],
			{ isProcessingMessage: true },
		);
		expect(screen.getByTestId("loading-bubbles")).toBeInTheDocument();
	});

	it("does not show loading bubbles when not processing", () => {
		renderChatMessages(
			[{ role: "user", content: "Hello", timestamp: "2025-01-01T00:00:00Z" }],
			{ isProcessingMessage: false },
		);
		expect(screen.queryByTestId("loading-bubbles")).not.toBeInTheDocument();
	});

	it("renders unknown role messages with fallback styling", () => {
		renderChatMessages([
			{
				role: "system",
				content: "System message",
				timestamp: "2025-01-01T00:00:00Z",
			},
		]);
		expect(screen.getByText("System message")).toBeInTheDocument();
		expect(screen.queryByTestId("coach-message")).not.toBeInTheDocument();
		expect(screen.queryByTestId("user-message")).not.toBeInTheDocument();
	});

	it("renders empty message list without crashing", () => {
		renderChatMessages([]);
		expect(screen.queryByTestId("coach-message")).not.toBeInTheDocument();
		expect(screen.queryByTestId("user-message")).not.toBeInTheDocument();
	});

	// Component-config routing — regression coverage for the fresh-chat
	// welcome card. Before this fix, the last coach message ignored
	// message.component_config entirely; the welcome SESSION_VIDEO seed
	// rendered as an empty bubble until a POST round-trip populated the
	// cache.
	describe("component routing for the last coach message", () => {
		it("renders cache componentConfig prop when present (POST round-trip path)", () => {
			renderChatMessages(
				[
					{
						role: "coach",
						content: "",
						timestamp: "2025-01-01T00:00:00Z",
					},
				],
				{ componentConfig: combineIdentitiesConfig },
			);
			expect(screen.getByTestId("coach-with-component")).toBeInTheDocument();
		});

		it("falls back to message.component_config on fresh load (welcome card seed)", () => {
			// Backend seeded the welcome SESSION_VIDEO directly on the message
			// row in ensure_initial_message_exists. No POST has happened yet,
			// so the in-memory cache is null. The card must still render.
			renderChatMessages([
				{
					role: "coach",
					content: "",
					timestamp: "2025-01-01T00:00:00Z",
					component_config: sessionVideoConfig,
				},
			]);
			expect(screen.getByTestId("coach-with-component")).toBeInTheDocument();
		});

		it("prefers the cache prop over message.component_config when both exist", () => {
			// After a POST round-trip both sources are populated. The cache
			// wins because it represents the freshest server response.
			renderChatMessages(
				[
					{
						role: "coach",
						content: "",
						timestamp: "2025-01-01T00:00:00Z",
						component_config: sessionVideoConfig,
					},
				],
				{ componentConfig: combineIdentitiesConfig },
			);
			// Both produce the same testid, so just confirm the routing fires.
			expect(screen.getByTestId("coach-with-component")).toBeInTheDocument();
			expect(screen.queryByTestId("coach-message")).not.toBeInTheDocument();
		});

		it("renders plain CoachMessage when last message has no component anywhere", () => {
			renderChatMessages([
				{
					role: "coach",
					content: "Hello!",
					timestamp: "2025-01-01T00:00:00Z",
				},
			]);
			expect(screen.getByTestId("coach-message")).toBeInTheDocument();
			expect(
				screen.queryByTestId("coach-with-component"),
			).not.toBeInTheDocument();
		});

		it("keeps server-seeded component visible during processing (no blink on Continue click)", () => {
			// The welcome SESSION_VIDEO card is persisted on the message row.
			// While the ACK click is in flight, the card must stay visible —
			// blanking it makes the UI flicker as it disappears + reappears
			// around the refetch. LoadingBubbles still appears beneath.
			renderChatMessages(
				[
					{
						role: "coach",
						content: "",
						timestamp: "2025-01-01T00:00:00Z",
						component_config: sessionVideoConfig,
					},
				],
				{ isProcessingMessage: true },
			);
			expect(screen.getByTestId("coach-with-component")).toBeInTheDocument();
			expect(screen.getByTestId("loading-bubbles")).toBeInTheDocument();
		});

		it("suppresses cache-only component while processing (legacy SHOW_XXX behavior)", () => {
			// No message.component_config; component came from in-memory
			// cache only (legacy SHOW_COMBINE_IDENTITIES-style flow). While
			// a POST is in flight, blank it so it's clear the previous
			// interactive choice is being processed.
			renderChatMessages(
				[
					{
						role: "coach",
						content: "Pick one",
						timestamp: "2025-01-01T00:00:00Z",
					},
				],
				{
					isProcessingMessage: true,
					componentConfig: combineIdentitiesConfig,
				},
			);
			expect(
				screen.queryByTestId("coach-with-component"),
			).not.toBeInTheDocument();
			expect(screen.getByTestId("loading-bubbles")).toBeInTheDocument();
		});

		it("still uses message.component_config for historical (non-last) coach messages", () => {
			renderChatMessages([
				{
					role: "coach",
					content: "",
					timestamp: "2025-01-01T00:00:00Z",
					component_config: sessionVideoConfig,
				},
				{
					role: "user",
					content: "ok",
					timestamp: "2025-01-01T00:00:01Z",
				},
				{
					role: "coach",
					content: "Hi there!",
					timestamp: "2025-01-01T00:00:02Z",
				},
			]);
			// Historical coach message routes through CoachMessageWithComponent
			// via message.component_config; the latest plain coach message
			// routes through CoachMessage.
			expect(screen.getByTestId("coach-with-component")).toBeInTheDocument();
			expect(screen.getByTestId("coach-message")).toBeInTheDocument();
		});
	});
});
