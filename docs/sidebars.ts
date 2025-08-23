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
        'getting-started/installation',
        'getting-started/quick-start',
      ],
    },
    {
      type: 'category',
      label: 'Core Systems',
      items: [
        'core-systems/prompt-manager',
        'core-systems/action-handler',
        'core-systems/coach-phases',
        'core-systems/identities',
      ],
    },
    {
      type: 'category',
      label: 'Development',
      items: [
        'development/adding-actions',
        'development/adding-phases',
        'development/adding-context-keys',
        'development/api-reference',
      ],
    },
    {
      type: 'category',
      label: 'Deployment',
      items: [
        'deployment/setup',
        'deployment/render-deployment',
        'deployment/environment-variables',
      ],
    },
  ],
};

export default sidebars;
