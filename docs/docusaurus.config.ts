import { themes as prismThemes } from "prism-react-renderer";
import type { Config } from "@docusaurus/types";
import type * as Preset from "@docusaurus/preset-classic";

// This runs in Node.js - Don't use client-side code here (browser APIs, JSX...)

const config: Config = {
  title: "Dev Coach Documentation",
  tagline: "Documentation for the Discovita Dev Coach System",
  favicon: "img/favicon.ico",

  // Future flags, see https://docusaurus.io/docs/api/docusaurus-config#future
  future: {
    v4: true, // Improve compatibility with the upcoming Docusaurus v4
  },

  // Set the production url of your site here
  url: "https://dev-coach-docs.onrender.com", // Update this to your actual Render URL
  // Set the /<baseUrl>/ pathname under which your site is served
  // For GitHub pages deployment, it is often '/<projectName>/'
  baseUrl: "/",

  // GitHub pages deployment config.
  // If you aren't using GitHub pages, you don't need these.
  // organizationName: 'facebook', // Usually your GitHub org/user name.
  // projectName: 'docusaurus', // Usually your repo name.

  onBrokenLinks: "throw",
  onBrokenMarkdownLinks: "warn",

  // Enable Mermaid diagrams
  markdown: {
    mermaid: true,
  },

  // Even if you don't use internationalization, you can use this field to set
  // useful metadata like html lang. For example, if your site is Chinese, you
  // may want to replace "en" with "zh-Hans".
  i18n: {
    defaultLocale: "en",
    locales: ["en"],
  },

  presets: [
    [
      "classic",
      {
        docs: {
          sidebarPath: "./sidebars.ts",
          editUrl: "https://github.com/Discovita/dev-coach/edit/main/docs",
        },
        theme: {
          customCss: "./src/css/custom.css",
        },
      } satisfies Preset.Options,
    ],
  ],

  // Add Mermaid theme
  themes: ["@docusaurus/theme-mermaid"],

  themeConfig: {
    // Replace with your project's social card
    image: "img/docusaurus-social-card.jpg",
    // Set dark theme as default
    colorMode: {
      defaultMode: 'dark',
      disableSwitch: false,
      respectPrefersColorScheme: false,
    },
    navbar: {
      title: "Dev Coach Docs",
      logo: {
        alt: "Dev Coach Logo",
        src: "img/logo.svg",
      },
      items: [
        {
          type: "docSidebar",
          sidebarId: "coachSidebar",
          position: "left",
          label: "Documentation",
        },
        {
          href: "https://github.com/Discovita/dev-coach",
          label: "GitHub",
          position: "right",
        },
      ],
    },
    footer: {
      style: "dark",
      links: [
        {
          title: "Documentation",
          items: [
            {
              label: "Getting Started",
              to: "/docs/intro",
            },
            {
              label: "Core Systems",
              to: "/docs/core-systems/prompt-manager/overview",
            },
            {
              label: "Action Handler",
              to: "/docs/core-systems/action-handler/overview",
            },
          ],
        },
        {
          title: "Development",
          items: [
            {
              label: "GitHub",
              href: "https://github.com/Discovita/dev-coach",
            },
            {
              label: "Issues",
              href: "https://github.com/Discovita/dev-coach/issues",
            },
          ],
        },
      ],
      copyright: `Copyright © ${new Date().getFullYear()} Discovita.`,
    },
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
    },
    // Mermaid configuration
    mermaid: {
      theme: { light: "neutral", dark: "dark" },
      options: {
        maxTextSize: 500,
        fontSize: 12,
        fontFamily: "Arial, sans-serif",
      },
    },
  } satisfies Preset.ThemeConfig,
};

export default config;
