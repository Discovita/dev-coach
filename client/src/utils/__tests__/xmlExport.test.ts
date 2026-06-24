import type { CoachState } from "@/types/coachState";
import type { Message } from "@/types/message";
import { convertToXml } from "@/utils/xmlExport";
import { describe, expect, it } from "vitest";

const mockCoachState = {
	current_phase: "introduction",
	identity_focus: null,
} as unknown as CoachState;

describe("convertToXml", () => {
	it("produces valid XML with messages", () => {
		const messages: Message[] = [
			{ role: "user", content: "Hello", timestamp: "2025-01-01T00:00:00Z" },
			{
				role: "coach",
				content: "Hi there!",
				timestamp: "2025-01-01T00:00:01Z",
			},
		];
		const xml = convertToXml(messages, "user-123", mockCoachState);

		expect(xml).toContain('<?xml version="1.0" encoding="UTF-8"?>');
		expect(xml).toContain("</conversation>");
		expect(xml).toContain("<userId>user-123</userId>");
		expect(xml).toContain("<messageCount>2</messageCount>");
		expect(xml).toContain("<role>user</role>");
		expect(xml).toContain("<role>coach</role>");
		expect(xml).toContain("Hello");
		expect(xml).toContain("Hi there!");
	});

	it("handles empty messages array", () => {
		const xml = convertToXml([], "user-123", mockCoachState);

		expect(xml).toContain("<messageCount>0</messageCount>");
		expect(xml).toContain("<messages/>");
	});

	it("wraps message content in CDATA sections", () => {
		const messages: Message[] = [
			{
				role: "user",
				content: "Hello <script>alert('xss')</script> & goodbye",
				timestamp: "2025-01-01T00:00:00Z",
			},
		];
		const xml = convertToXml(messages, "user-123", mockCoachState);

		expect(xml).toContain("<![CDATA[");
		expect(xml).toContain("Hello");
		expect(xml).toContain("goodbye");
	});

	it("includes coach state fields", () => {
		const xml = convertToXml([], "user-123", mockCoachState);

		expect(xml).toContain("<coach_state>");
		expect(xml).toContain("<current_phase>introduction</current_phase>");
		expect(xml).toContain("<identity_focus>null</identity_focus>");
	});

	it("wraps object coach state values in CDATA", () => {
		const stateWithObject = {
			current_phase: "introduction",
			some_object: { key: "value" },
		} as unknown as CoachState;
		const xml = convertToXml([], "user-123", stateWithObject);

		expect(xml).toContain("<![CDATA[");
	});
});
