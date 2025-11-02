# Satomi - Japanese Concept Learning Platform

A minimal Next.js backend application that delivers beautifully explained Japanese cultural concepts through conversational AI powered by OpenAI.

## Overview

Satomi provides a backend infrastructure for processing and explaining traditional Japanese concepts, philosophies, and principles to Western audiences. Each response focuses on a single concept with clear explanations, historical context, and practical applications.

## Features

- **Japanese Concept Explanation**: Server action and API endpoint for explaining Japanese cultural concepts
- **Content Processing**: Generic content processor with OpenAI integration
- **Placeholder Detection**: Automatic detection and removal of placeholder text from content
- **File Validation**: Special handling for README and LICENSE files to ensure production readiness
- **Type-Safe**: Full TypeScript implementation with comprehensive type definitions
- **Server-Only**: Backend-focused architecture using Next.js 16 app directory and server actions

## Architecture

### Core Components

1. **Server Actions** (`lib/actions/`)
   - `japanese-concept-action.ts`: Main server action for explaining Japanese concepts
   - `content-processor-action.ts`: Generic content processing and file validation

2. **API Routes** (`app/api/`)
   - `/api/japanese-concept`: POST endpoint for concept explanations
   - `/api/process-content`: POST endpoint for content processing
   - `/api/validate-file`: POST endpoint for file validation

3. **Utilities** (`lib/utils/`)
   - `placeholder-detector.ts`: Detection and removal of placeholder text

4. **OpenAI Integration** (`lib/openai.ts`)
   - Centralized OpenAI client configuration

## Installation

```bash
# Install dependencies
pnpm install

# Set up environment variables
# Create a .env.local file with:
# OPENAI_API_KEY=your_api_key_here

# Run development server
pnpm dev

# Build for production
pnpm build

# Run linter
pnpm lint
```

## API Usage

### 1. Japanese Concept Explanation

**Endpoint**: `POST /api/japanese-concept`

**Request**:
```json
{
  "query": "What is ikigai and how can I find mine?",
  "conversationHistory": [
    {
      "role": "user",
      "content": "Tell me about Japanese philosophy"
    },
    {
      "role": "assistant",
      "content": "Japanese philosophy encompasses..."
    }
  ]
}
```

**Response**:
```json
{
  "success": true,
  "concept": {
    "name": "Ikigai (生き甲斐)",
    "explanation": "Your reason for being...",
    "origin": "Traditional Japanese concept...",
    "application": "To discover your ikigai...",
    "fullResponse": "Complete formatted response..."
  },
  "timestamp": "2025-11-01T12:00:00.000Z"
}
```

### 2. Content Processing

**Endpoint**: `POST /api/process-content`

**Request**:
```json
{
  "content": "Text content to process",
  "filename": "README.md",
  "processType": "improve",
  "customPrompt": "Optional custom system prompt"
}
```

**Process Types**:
- `improve`: Enhance and polish content
- `summarize`: Create concise summary
- `analyze`: Provide detailed analysis
- `custom`: Use custom prompt

**Response**:
```json
{
  "success": true,
  "processedContent": "Enhanced content...",
  "originalContent": "Original text...",
  "hadPlaceholders": false,
  "warnings": [],
  "timestamp": "2025-11-01T12:00:00.000Z"
}
```

### 3. File Validation

**Endpoint**: `POST /api/validate-file`

**Request**:
```json
{
  "filename": "README.md",
  "content": "File content to validate"
}
```

**Response**:
```json
{
  "valid": true,
  "errors": [],
  "warnings": [],
  "cleanedContent": "Content with placeholders removed (if any)"
}
```

## Server Actions Usage

You can also use server actions directly in your Next.js components:

```typescript
import { explainJapaneseConcept } from '@/lib/actions/japanese-concept-action';
import { processContent, validateFileContent } from '@/lib/actions/content-processor-action';

// In a server component or server action
const result = await explainJapaneseConcept({
  query: "What is wabi-sabi?",
});

const processed = await processContent({
  content: "Content to process",
  processType: "improve",
});

const validation = await validateFileContent("README.md", content);
```

## Placeholder Detection

The system automatically detects and removes common placeholder patterns:

- `[placeholder]`, `{placeholder}`, `<placeholder>`
- `YOUR_*`, `REPLACE_*`, `TODO:`, `FIXME:`
- `example.com`, `lorem ipsum`
- `${VARIABLE}`, `[[placeholder]]`
- Multiple underscores or dots used as placeholders

Special handling for README and LICENSE files ensures they are production-ready.

## Environment Variables

Required environment variables:

```bash
OPENAI_API_KEY=your_openai_api_key_here
```

## Technology Stack

- **Framework**: Next.js 16 (App Router)
- **Language**: TypeScript
- **AI Integration**: OpenAI API (via openai package)
- **Package Manager**: pnpm
- **Runtime**: Node.js

## Project Structure

```
satomi/
├── app/
│   ├── api/
│   │   ├── japanese-concept/
│   │   │   └── route.ts
│   │   ├── process-content/
│   │   │   └── route.ts
│   │   └── validate-file/
│   │       └── route.ts
│   ├── layout.tsx
│   └── page.tsx
├── lib/
│   ├── actions/
│   │   ├── content-processor-action.ts
│   │   └── japanese-concept-action.ts
│   ├── utils/
│   │   └── placeholder-detector.ts
│   └── openai.ts
├── types/
│   └── index.ts
├── docs/
│   ├── README.md
│   ├── API.md
│   └── ARCHITECTURE.md
├── rules/
│   └── (project-specific rules)
└── package.json
```

## Use Cases

1. **Japanese Culture Learning Platform**: Build a conversational interface for learning about Japanese concepts
2. **Content Enhancement**: Process and improve documentation files
3. **File Validation**: Ensure README and LICENSE files are production-ready
4. **Knowledge Base**: Create a repository of Japanese wisdom and philosophy

## Business Model

- Free access to concept explanations
- Monetization through advertising
- Build an audience over time
- Launch additional products to engaged audience
- Expand into other mediums (podcast, video, courses)

## Extension Ideas

- Add conversation state management
- Implement user authentication
- Store conversation history in a database
- Add analytics and tracking
- Create a frontend interface
- Integrate with other AI models
- Add multilingual support
- Implement rate limiting

## License

This project is for demonstration and educational purposes.

## Support

For questions or issues, refer to the documentation in the `/docs` folder.

