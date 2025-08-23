import type {SidebarsConfig} from '@docusaurus/plugin-content-docs';

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
    'intro',
    {
      type: 'category',
      label: 'Getting Started',
      items: [
        'getting-started/overview',
        // 'getting-started/installation', // TODO: Create this file
        // 'getting-started/quick-start', // TODO: Create this file
      ],
    },
    {
      type: 'category',
      label: 'Core Systems',
      items: [
        'core-systems/prompt-manager',
        // 'core-systems/action-handler', // TODO: Create this file
        // 'core-systems/coach-phases', // TODO: Create this file
        // 'core-systems/identities', // TODO: Create this file
      ],
    },
    {
      type: 'category',
      label: 'API Reference',
      items: [
        'api/overview',
        {
          type: 'category',
          label: 'Authentication',
          items: [
            'api/authentication/auth',
            // 'api/authentication/tokens', // TODO: Create this file
            // 'api/authentication/permissions', // TODO: Create this file
          ],
        },
        // TODO: Add Endpoints category when files are created
        // {
        //   type: 'category',
        //   label: 'Endpoints',
        //   items: [
        //     'api/endpoints/users',
        //     'api/endpoints/coaching',
        //     'api/endpoints/admin',
        //   ],
        // },
      ],
    },
    {
      type: 'category',
      label: 'Database',
      items: [
        'database/overview',
        {
          type: 'category',
          label: 'Models',
          items: [
            'database/models/users',
            // 'database/models/coaching', // TODO: Create this file
            // 'database/models/system', // TODO: Create this file
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
    // TODO: Add these categories when the files are created
    // {
    //   type: 'category',
    //   label: 'Development',
    //   items: [
    //     'development/adding-actions',
    //     'development/adding-phases',
    //     'development/adding-context-keys',
    //     'development/api-reference',
    //   ],
    // },
    // {
    //   type: 'category',
    //   label: 'Deployment',
    //   items: [
    //     'deployment/setup',
    //     'deployment/render-deployment',
    //     'deployment/environment-variables',
    //   ],
    // },
  ],
};

export default sidebars;
