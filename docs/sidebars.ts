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
        "core-systems/prompt-manager",
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
