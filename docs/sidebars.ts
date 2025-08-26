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
          label: "Prompt Manager",
          items: [
            "core-systems/prompt-manager/overview",
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
        {
          type: "category",
          label: "Sentinel",
          items: [
            "core-systems/sentinel/overview",
            "core-systems/sentinel/implementation",
          ],
        },
        {
          type: "category",
          label: "Action Handler",
          items: [
            "core-systems/action-handler/overview",
            {
              type: "category",
              label: "Actions",
              items: [
                "core-systems/action-handler/actions/create-identity",
                "core-systems/action-handler/actions/update-identity",
                "core-systems/action-handler/actions/update-identity-name",
                "core-systems/action-handler/actions/update-identity-affirmation",
                "core-systems/action-handler/actions/update-identity-visualization",
                "core-systems/action-handler/actions/accept-identity",
                "core-systems/action-handler/actions/accept-identity-refinement",
                "core-systems/action-handler/actions/accept-identity-affirmation",
                "core-systems/action-handler/actions/accept-identity-visualization",
                "core-systems/action-handler/actions/add-identity-note",
                "core-systems/action-handler/actions/transition-phase",
                "core-systems/action-handler/actions/select-identity-focus",
                "core-systems/action-handler/actions/set-current-identity",
                "core-systems/action-handler/actions/skip-identity-category",
                "core-systems/action-handler/actions/unskip-identity-category",
                "core-systems/action-handler/actions/update-who-you-are",
                "core-systems/action-handler/actions/update-who-you-want-to-be",
                "core-systems/action-handler/actions/update-asked-questions",
                "core-systems/action-handler/actions/add-user-note",
                "core-systems/action-handler/actions/update-user-note",
                "core-systems/action-handler/actions/delete-user-note",
              ],
            },
          ],
        },
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
      ],
    },
    {
      type: "category",
      label: "Testing",
      items: [
        "testing/overview",
        "testing/scenario-management",
        "testing/coach-state-visualization",
      ],
    },
    {
      type: "category",
      label: "How-To's",
      items: [
        "how-to/overview",
        "how-to/how-to-add-a-new-context-key",
        "how-to/how-to-add-a-new-coach-phase",
        "how-to/how-to-add-a-new-coach-action",
      ],
    },
    {
      type: "category",
      label: "Development",
      items: [
        "development/overview",
        "development/docker-configuration",
        "development/common-commands",
      ],
    },
  ],
};

export default sidebars;
