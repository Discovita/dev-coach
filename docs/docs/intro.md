---
sidebar_position: 1
---

# Introduction

Welcome to the Dev Coach documentation! Dev Coach is a sophisticated AI-powered life coaching chatbot system developed by Discovita that helps users create and maintain multiple identities for different areas of their lives.

## What is Dev Coach?

Dev Coach is an AI-powered life coaching system that guides users through a structured process of creating and maintaining multiple identities. Each identity represents a different aspect of the user's life (career, relationships, health, etc.) and helps them achieve their goals more effectively through identity-driven transformation.

The system operates on the principle that **identity drives behavior** - when users align with who they want to be rather than forcing themselves toward what they want to achieve, sustainable change emerges naturally.

## How It Works

The Coach system operates through structured coaching phases:

1. **Coaching Phases** - The system walks users through different phases of identity development
2. **Identity Creation** - Users create specific identities for different life areas (career, health, relationships, etc.)
3. **Identity Refinement** - Each identity is refined with affirmations and visualizations
4. **Daily Integration** - Users learn to embody these identities in their daily lives
5. **Progress Tracking** - The system tracks progress and adjusts strategies based on user interactions

## Core Systems

Dev Coach is built on several interconnected systems:

- **Prompt Manager System** - Manages AI prompts for different coaching phases, with version control and context injection
- **Action Handler System** - Processes and executes actions based on user interactions (create identities, transition phases, etc.)
- **Coach State Management** - Tracks user progress, current coaching phase, and session state
- **Identity Management** - Stores and manages user-created identities with categories and states
- **Sentinel System** - Extracts long-term insights from conversations for user memory

## Technology Stack

### Frontend

- **React** with TypeScript for type safety
- **Vite** for fast development and building
- **TanStack Query** for efficient data fetching and caching
- **Shadcn/ui** for consistent component library
- **Tailwind CSS 4.0** for styling

### Backend

- **Django REST Framework** for API development
- **Python** for server-side logic
- **PostgreSQL** for data persistence
- **JWT Authentication** for secure user sessions

### AI Integration

- **Multiple AI Providers** (OpenAI used exclusively at the moment)
- **Dynamic Prompt Management** with version control
- **Context-Aware Responses** based on user state and history

## Getting Started

To get started with Dev Coach:

1. [Coach Philosophy](./coach/philosophy) - Understand the identity-based coaching methodology
2. [Core Systems Overview](./core-systems/prompt-manager/overview) - Learn about the technical architecture
3. [API Reference](./api/overview) - Explore the available endpoints
4. [Database Schema](./database/overview) - Understand the data structure

## For Developers

If you're contributing to or extending Dev Coach:

1. [How to Add New Actions](./how-to/how-to-add-a-new-coach-action) - Step-by-step guide for adding new coaching actions
2. [How to Add New Phases](./how-to/how-to-add-a-new-coach-phase) - Adding new coaching phases to the system
3. [How to Add New Context Keys](./how-to/how-to-add-a-new-context-key) - Extending the prompt context system
4. [Database Models](./database/models/users) - Understanding the data structure and relationships

## Project Structure

The Dev Coach project follows a clear separation between frontend and backend:

### Frontend (`client/`)

- **React/TypeScript** application with Vite
- **Component-based architecture** with reusable UI components
- **TanStack Query** for efficient API communication
- **Shadcn/ui** for consistent design system

### Backend (`server/`)

- **Django REST Framework** with modular app structure
- **PostgreSQL** database with comprehensive data models
- **JWT authentication** for secure user sessions
- **AI service integration** with multiple providers

## Support

- **GitHub Issues**: [Report bugs or request features](https://github.com/Discovita/dev-coach/issues)
- **Documentation**: This site contains comprehensive guides and references
- **Community**: Join our development community on GitHub

---

Ready to dive in? Start with the [Coach Philosophy](./coach/philosophy) section to learn more about how Dev Coach works.
