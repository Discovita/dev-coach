---
sidebar_position: 4
---

# Relationships Identity Category Context

**Note**: There is no single "Relationships" `IdentityCategory` in the system. Relationship-oriented identities are split into two separate categories:

- **FAMILY** (`familial_relations`) — covers familial relationships (parent, sibling, child, etc.)
- **ROMANTIC** (`romantic_relation`) — covers romantic and sexual expression

Each has its own dedicated markdown context file loaded by `get_brainstorming_category_context()`:

- `familial_relations.md`
- `romantic_relation.md`

## Category Details

**Context Key**: `brainstorming_category_context`  
**Phase**: Identity Brainstorming  
**Data Source**: Markdown files on disk, keyed by `CoachState.identity_focus`

See the [Identity Brainstorming Context](../phases/identity-brainstorming) page for implementation details.
