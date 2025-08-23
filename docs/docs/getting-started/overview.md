---
sidebar_position: 1
---

# System Overview

This section provides a high-level overview of how the Dev Coach system works, its architecture, and key concepts.

## Architecture Overview

Dev Coach is built as a modern web application with a clear separation between frontend and backend components:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Frontend│    │  Django Backend │    │   PostgreSQL    │
│                 │◄──►│                 │◄──►│   Database      │
│  - Chat UI      │    │  - API Endpoints│    │                 │
│  - Admin Panel  │    │  - AI Services  │    │  - User Data    │
│  - Test Tools   │    │  - Business Logic│   │  - Coach State  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Key Components

### 1. Frontend (React + TypeScript)
- **Chat Interface**: Main user interaction point
- **Admin Panel**: Management tools for prompts, actions, and system configuration
- **Test Tools**: Development and testing utilities
- **State Management**: TanStack Query for server state, React state for UI

### 2. Backend (Django Rest Framework)
- **API Endpoints**: RESTful API for all system operations
- **AI Service Integration**: Connects to various AI providers
- **Business Logic**: Core coaching algorithms and workflows
- **Authentication**: User management and security

### 3. Core Systems
- **Prompt Manager**: Manages AI prompts for different coaching phases
- **Action Handler**: Processes and executes system actions
- **Coach State**: Tracks user progress and current phase
- **Identity Management**: Stores and manages user identities

## Data Flow

1. **User Interaction**: User sends a message through the chat interface
2. **State Retrieval**: System retrieves current coach state and user data
3. **Prompt Construction**: Prompt Manager builds appropriate AI prompt
4. **AI Processing**: AI service generates response with potential actions
5. **Action Execution**: Action Handler processes and executes any actions
6. **State Update**: Coach state and user data are updated
7. **Response Delivery**: Response is sent back to the user

## Coaching Phases

The system guides users through several distinct phases:

1. **Initial Assessment** - Understanding user's current situation
2. **Identity Creation** - Creating specific identities for life areas
3. **Goal Setting** - Establishing objectives for each identity
4. **Daily Practice** - Supporting identity implementation
5. **Progress Tracking** - Monitoring and adjusting strategies

## Identity System

The core concept of Dev Coach is the **Identity System**:

- **Multiple Identities**: Users create separate identities for different life areas
- **Context Switching**: System helps users switch between identities as needed
- **Goal Alignment**: Each identity has specific goals and strategies
- **Progress Tracking**: Individual progress tracking for each identity

## AI Integration

Dev Coach integrates with multiple AI providers:

- **OpenAI**: Primary AI provider for chat responses
- **Anthropic**: Alternative AI provider for specific use cases
- **Custom Prompts**: Sophisticated prompt engineering for coaching effectiveness
- **Context Management**: Intelligent context switching based on user needs

## Security & Privacy

- **User Authentication**: Secure login and session management
- **Data Encryption**: All sensitive data is encrypted
- **Privacy Controls**: User data is protected and not shared
- **Audit Logging**: Comprehensive logging for security and debugging

## Scalability

The system is designed for scalability:

- **Microservices Architecture**: Modular design for easy scaling
- **Database Optimization**: Efficient queries and indexing
- **Caching**: Intelligent caching for performance
- **Load Balancing**: Support for multiple server instances

## Development Workflow

The development process follows modern practices:

- **Version Control**: Git-based workflow with feature branches
- **Testing**: Comprehensive test suite for all components
- **CI/CD**: Automated testing and deployment pipelines
- **Documentation**: Extensive documentation for all systems

---

Next, learn about [installation and setup](./installation.md) or dive into the [core systems](../core-systems/prompt-manager.md).
