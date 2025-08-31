# Documentation Linking Guidelines

This document provides guidelines for creating consistent and maintainable links in the Dev Coach documentation.

## Link Types

### 1. Absolute Paths (Recommended)

Use absolute paths starting with `/docs/` for all internal documentation links. This makes links independent of the current file's location and prevents broken links when files are moved.

**✅ Good:**

```markdown
- [Action Fields](/docs/database/models/action)
- [Prompt Manager Overview](/docs/core-systems/prompt-manager/overview)
- [API Endpoints](/docs/api/endpoints/actions)
```

**❌ Avoid:**

```markdown
- [Action Fields](docs/database/models/action)
- [Prompt Manager Overview](../../core-systems/prompt-manager/overview)
- [API Endpoints](../endpoints/actions)
```

### 2. External Links

Use full URLs for external links:

**✅ Good:**

```markdown
- [Docusaurus Documentation](https://docusaurus.io/docs)
- [GitHub Repository](https://github.com/Discovita/dev-coach)
```

## Link Organization

### Cross-Reference Links

When linking to related documentation, use consistent patterns:

#### API Documentation

```markdown
## Field Reference

For detailed field information on models used in these endpoints, see:

- **[Action Fields](/docs/database/models/action)** - Action model structure
- **[Chat Message Fields](/docs/database/models/chat-message)** - Chat message structure
- **[User Fields](/docs/database/models/users)** - User model structure
```

#### System Documentation

```markdown
## Related Systems

- **[Prompt Manager](/docs/core-systems/prompt-manager/overview)** - How prompts are managed
- **[Action Handler](/docs/core-systems/action-handler/overview)** - How actions are processed
- **[Sentinel](/docs/core-systems/sentinel/overview)** - Content moderation system
```

### Navigation Links

Use consistent navigation patterns:

```markdown
## Next Steps

- [Core Systems Overview](/docs/core-systems/prompt-manager/overview) - Learn about the core systems
- [API Reference](/docs/api/overview) - Complete API documentation
- [Database Schema](/docs/database/overview) - Database structure and relationships
```

## Best Practices

### 1. Always Use Absolute Paths

- Prevents broken links when files are moved
- Makes links easier to maintain
- Reduces cognitive load when writing documentation

### 2. Use Descriptive Link Text

- Avoid generic text like "click here" or "more info"
- Use descriptive text that indicates the destination content

### 3. Group Related Links

- Use consistent sections like "Field Reference", "Related Systems", "Next Steps"
- Maintain alphabetical order within sections when appropriate

### 4. Test Links Regularly

- Use Docusaurus's built-in link checking: `npm run build`
- Fix broken links immediately to maintain documentation quality

## Migration Strategy

When moving files or reorganizing documentation:

1. **Update all absolute paths** to reflect new locations
2. **Run link validation** to catch any missed updates
3. **Update sidebar configuration** in `sidebars.ts`
4. **Test the build** to ensure all links work correctly

## Tools and Validation

### Built-in Validation

Docusaurus automatically validates links during build:

```bash
npm run build
```

### Automated Link Checking

Use the provided script to find relative links:

```bash
npm run check-links
```

This script will:

- Scan all markdown files for relative links
- Suggest absolute path replacements
- Help maintain consistent linking patterns

### Manual Validation

Check for broken links in the build output and fix them immediately.

## Examples

### Good Documentation Structure

```markdown
# API Endpoint: Actions

## Overview

This endpoint handles action processing for the Dev Coach system.

## Related Documentation

- **[Action Handler System](/docs/core-systems/action-handler/overview)** - How actions are processed
- **[Action Model](/docs/database/models/action)** - Database structure for actions
- **[Action Types](/docs/core-systems/action-handler/actions/create-identity)** - Available action types

## Next Steps

- [Authentication](/docs/api/endpoints/authentication) - Learn about authentication
- [Core API](/docs/api/endpoints/core) - Core API endpoints
- [Testing](/docs/testing/overview) - Testing strategies and tools
```

This approach ensures consistent, maintainable documentation that's easy to reorganize without breaking links.
