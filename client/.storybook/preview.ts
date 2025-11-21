import React from 'react';
import type { Preview } from '@storybook/react-vite';
import '../src/index.css';
import { initialize, mswLoader } from 'msw-storybook-addon';
import { StorybookProviders } from './StorybookProviders';

// Initialize MSW
initialize();

const preview: Preview = {
  decorators: [
    (Story) =>
      React.createElement(
        StorybookProviders,
        { children: React.createElement(Story, {}) }
      ),
  ],
  parameters: {
    controls: {
      matchers: {
        color: /(background|color)$/i,
        date: /Date$/i,
      },
    },

    a11y: {
      // 'todo' - show a11y violations in the test UI only
      // 'error' - fail CI on a11y violations
      // 'off' - skip a11y checks entirely
      test: 'todo',
    },
  },
  loaders: [mswLoader],
};

export default preview;