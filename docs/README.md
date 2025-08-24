# Website

This website is built using [Docusaurus](https://docusaurus.io/), a modern static website generator.

## Installation

```bash
yarn
```

## Local Development

```bash
yarn start
```

This command starts a local development server and opens up a browser window. Most changes are reflected live without having to restart the server.

## Build

```bash
yarn build
```

This command generates static content into the `build` directory and can be served using any static contents hosting service.

## Deployment

Using SSH:

```bash
USE_SSH=true yarn deploy
```

Not using SSH:

```bash
GIT_USER=<Your GitHub username> yarn deploy
```

If you are using GitHub pages for hosting, this command is a convenient way to build the website and push to the `gh-pages` branch.

# Docs to make
- All views.
- All models
- Explain Sentry
    - How it works
    - Celery setup
    - Actions it can take
    - How the user notes are used in prompts
    - Cross reference with Prompt Manager
- Explan Action Handler
    - All Actions and exactly what they do
        - Cross reference with models
- Explain Prompt Manager
    - All Context Keys
        - IB Context prompts
- Explain Testing
- Coaching Philosophy
