import type { SidebarsConfig } from "@docusaurus/plugin-content-docs";

// This runs in Node.js - Don't use client-side code here (browser APIs, JSX...)

/**
 * Creating a sidebar enables you to:
 - create an ordered group of docs
 - render a sidebar for each doc of that group
 - provide next/previous navigation

 The sidebars can be generated from the filesystem, or explicitly defined here.

 Create as many sidebars as you want.
 */
const sidebars: SidebarsConfig = {
  // Coach documentation sidebar
  coachSidebar: [
    "intro",
    {
      type: "category",
      label: "The Coach",
      items: [
        "coach/philosophy",
        "coach/techniques-and-approaches",
        "coach/integration-and-application",
        "coach/identity-categories",
        "coach/phases",
      ],
    },
    {
      type: "category",
      label: "Core Systems",
      items: [
        {
          type: "category",
          label: "Prompt Manager System",
          items: [
            "core-systems/prompt-manager/overview",
            "core-systems/prompt-manager/construction-process",
            "core-systems/prompt-manager/database-integration",
            "core-systems/prompt-manager/action-system",
            "core-systems/prompt-manager/provider-formatting",
            "core-systems/prompt-manager/system-context",
            "core-systems/prompt-manager/templates",
            {
              type: "category",
              label: "Context Keys",
              items: [
                "core-systems/prompt-manager/context-keys/overview",
                "core-systems/prompt-manager/context-keys/user-name",
                "core-systems/prompt-manager/context-keys/user-notes",
                "core-systems/prompt-manager/context-keys/identities",
                "core-systems/prompt-manager/context-keys/number-of-identities",
                "core-systems/prompt-manager/context-keys/identity-focus",
                "core-systems/prompt-manager/context-keys/current-identity",
                "core-systems/prompt-manager/context-keys/focused-identities",
                "core-systems/prompt-manager/context-keys/refinement-identities",
                "core-systems/prompt-manager/context-keys/affirmation-identities",
                "core-systems/prompt-manager/context-keys/visualization-identities",
                "core-systems/prompt-manager/context-keys/current-phase",
                "core-systems/prompt-manager/context-keys/who-you-are",
                "core-systems/prompt-manager/context-keys/who-you-want-to-be",
                "core-systems/prompt-manager/context-keys/asked-questions",
                "core-systems/prompt-manager/context-keys/current-message",
                "core-systems/prompt-manager/context-keys/previous-message",
                "core-systems/prompt-manager/context-keys/recent-messages",
                {
                  type: "category",
                  label: "Brainstorming Category Context",
                  items: [
                    "core-systems/prompt-manager/context-keys/brainstorming/overview",
                    "core-systems/prompt-manager/context-keys/brainstorming/passions-and-talents",
                    "core-systems/prompt-manager/context-keys/brainstorming/maker-of-money",
                    "core-systems/prompt-manager/context-keys/brainstorming/keeper-of-money",
                    "core-systems/prompt-manager/context-keys/brainstorming/spiritual",
                    "core-systems/prompt-manager/context-keys/brainstorming/personal-appearance",
                    "core-systems/prompt-manager/context-keys/brainstorming/physical-expression",
                    "core-systems/prompt-manager/context-keys/brainstorming/familial-relations",
                    "core-systems/prompt-manager/context-keys/brainstorming/romantic-relation",
                    "core-systems/prompt-manager/context-keys/brainstorming/doer-of-things",
                  ],
                },
              ],
            },
          ],
        },
        // 'core-systems/action-handler', // TODO: Create this file
        // 'core-systems/coach-phases', // TODO: Create this file
        // 'core-systems/identities', // TODO: Create this file
      ],
    },
    {
      type: "category",
      label: "API Reference",
      items: [
        "api/overview",
        {
          type: "category",
          label: "Endpoints",
          items: [
            "api/endpoints/authentication",
            "api/endpoints/coach",
            "api/endpoints/users",
            "api/endpoints/core",
            "api/endpoints/prompts",
            "api/endpoints/test-users",
            "api/endpoints/test-scenarios",
            "api/endpoints/actions",
          ],
        },
      ],
    },
    {
      type: "category",
      label: "Database",
      items: [
        "database/overview",
        {
          type: "category",
          label: "Models",
          items: [
            "database/models/users",
            "database/models/coach-state",
            "database/models/identity",
            "database/models/chat-message",
            "database/models/prompt",
            "database/models/action",
            "database/models/test-scenario",
            "database/models/user-note",
          ],
        },
        {
          type: "category",
          label: "Schema",
          items: [
            "database/schema/overview",
            "database/schema/relationships",
            "database/schema/indexes",
          ],
        },
        // TODO: Add Schema category when files are created
        // {
        //   type: 'category',
        //   label: 'Schema',
        //   items: [
        //     'database/schema/tables',
        //     'database/schema/relationships',
        //     'database/schema/indexes',
        //   ],
        // },
      ],
    },
  ],
};

export default sidebars;
