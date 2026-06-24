import { LogLevel, Logger, createLogger } from "@/lib/logger";
import { beforeEach, describe, expect, it, vi } from "vitest";

describe("Logger", () => {
	beforeEach(() => {
		vi.spyOn(console, "error").mockImplementation(() => {});
		vi.spyOn(console, "warn").mockImplementation(() => {});
		vi.spyOn(console, "info").mockImplementation(() => {});
		vi.spyOn(console, "log").mockImplementation(() => {});
	});

	it("logs error when level >= ERROR", () => {
		const logger = new Logger("test", LogLevel.ERROR);
		logger.error("test error");
		expect(console.error).toHaveBeenCalledTimes(1);
	});

	it("does not log warn when level is ERROR", () => {
		const logger = new Logger("test", LogLevel.ERROR);
		logger.warn("test warn");
		expect(console.warn).not.toHaveBeenCalled();
	});

	it("logs warn when level >= WARN", () => {
		const logger = new Logger("test", LogLevel.WARN);
		logger.warn("test warn");
		expect(console.warn).toHaveBeenCalledTimes(1);
	});

	it("logs info when level >= INFO", () => {
		const logger = new Logger("test", LogLevel.INFO);
		logger.info("test info");
		expect(console.info).toHaveBeenCalledTimes(1);
	});

	it("does not log debug when level is INFO", () => {
		const logger = new Logger("test", LogLevel.INFO);
		logger.debug("test debug");
		expect(console.log).not.toHaveBeenCalled();
	});

	it("logs debug when level >= DEBUG", () => {
		const logger = new Logger("test", LogLevel.DEBUG);
		logger.debug("test debug");
		expect(console.log).toHaveBeenCalledTimes(1);
	});

	it("logs trace when level >= TRACE", () => {
		const logger = new Logger("test", LogLevel.TRACE);
		logger.trace("test trace");
		expect(console.log).toHaveBeenCalledTimes(1);
	});

	it("includes the logger name in output", () => {
		const logger = new Logger("myModule", LogLevel.ERROR);
		logger.error("something broke");
		expect(console.error).toHaveBeenCalledWith(
			expect.stringContaining("myModule"),
			"something broke",
		);
	});

	it("setLevel changes the logging threshold", () => {
		const logger = new Logger("test", LogLevel.ERROR);
		logger.debug("should not appear");
		expect(console.log).not.toHaveBeenCalled();

		logger.setLevel(LogLevel.DEBUG);
		logger.debug("should appear");
		expect(console.log).toHaveBeenCalledTimes(1);
	});
});

describe("createLogger", () => {
	it("creates a Logger instance", () => {
		const logger = createLogger("test");
		expect(logger).toBeInstanceOf(Logger);
	});

	it("defaults to INFO level", () => {
		vi.spyOn(console, "log").mockImplementation(() => {});
		const logger = createLogger("test");
		logger.debug("should not log");
		expect(console.log).not.toHaveBeenCalled();
	});

	it("accepts a custom level", () => {
		vi.spyOn(console, "log").mockImplementation(() => {});
		const logger = createLogger("test", LogLevel.DEBUG);
		logger.debug("should log");
		expect(console.log).toHaveBeenCalled();
	});
});
