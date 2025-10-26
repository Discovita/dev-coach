# Logger Usage Guide

## Basic Usage

Create a logger at the top of your file, named after the file:

```typescript
import { createLogger, LogLevel } from "./logger";

const log = createLogger("userService", LogLevel.INFO);

function fetchUser(id: string) {
  log.debug("Fetching user");
  // [DEBUG] [userService:fetchUser] Fetching user
}
```

The logger automatically shows which function called it.

## Log Levels

- `ERROR` - Critical errors only
- `WARN` - Warnings and errors
- `INFO` - General info (default)
- `DEBUG` - Debug info
- `TRACE` - Most verbose

## The Main Workflow

Keep all your debug/trace logs in your code, but control them with the level:

```typescript
// Normal: hide debug logs
const log = createLogger("userService", LogLevel.INFO);

function processUser(user: any) {
  log.trace("Starting process"); // Hidden
  log.debug("Processing data"); // Hidden
  log.info("Process complete"); // Visible
}
```

When troubleshooting, change ONE line at the top:

```typescript
// Troubleshooting: see everything
const log = createLogger("userService", LogLevel.TRACE);
// Now all logs appear with function names!
```

No need to delete debug logs. Just toggle the level.

## Quick Reference

```typescript
log.error("message"); // [ERROR] [fileName:functionName] message
log.warn("message"); // [WARN] [fileName:functionName] message
log.info("message"); // [INFO] [fileName:functionName] message
log.debug("message"); // [DEBUG] [fileName:functionName] message
log.trace("message"); // [TRACE] [fileName:functionName] message
```
