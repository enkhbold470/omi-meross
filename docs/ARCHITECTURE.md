# Architecture Documentation

Detailed technical architecture of the Satomi Japanese Concept Learning Platform.

## System Overview

Satomi is built as a backend-focused Next.js application that leverages OpenAI's API to provide intelligent explanations of Japanese cultural concepts. The architecture follows a modular, type-safe approach using Next.js 16 App Router conventions.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         Client Layer                         │
│  (External Services / Frontend Apps / API Consumers)         │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ HTTP/HTTPS
                         │
┌────────────────────────▼────────────────────────────────────┐
│                     Next.js App Router                       │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │           API Routes (app/api/)                    │    │
│  │                                                     │    │
│  │  ┌─────────────────┐  ┌─────────────────────┐    │    │
│  │  │ /japanese-      │  │ /process-content    │    │    │
│  │  │  concept        │  │                     │    │    │
│  │  └────────┬────────┘  └────────┬────────────┘    │    │
│  │           │                     │                  │    │
│  │           │    ┌────────────────▼─────┐          │    │
│  │           │    │ /validate-file       │          │    │
│  │           │    └──────────────────────┘          │    │
│  └───────────┼────────────┬────────────────────────┘    │
│              │            │                              │
│  ┌───────────▼────────────▼─────────────────────────┐   │
│  │         Server Actions (lib/actions/)            │   │
│  │                                                   │   │
│  │  ┌──────────────────┐  ┌───────────────────┐   │   │
│  │  │ japanese-concept │  │ content-processor │   │   │
│  │  │ -action.ts       │  │ -action.ts        │   │   │
│  │  └────────┬─────────┘  └─────────┬─────────┘   │   │
│  └───────────┼────────────────────────┼─────────────┘   │
│              │                        │                  │
│  ┌───────────▼────────────────────────▼─────────────┐   │
│  │        Utilities & Helpers (lib/)                │   │
│  │                                                   │   │
│  │  ┌────────────────┐    ┌──────────────────┐    │   │
│  │  │ openai.ts      │    │ placeholder-     │    │   │
│  │  │ (Client Setup) │    │ detector.ts      │    │   │
│  │  └───────┬────────┘    └──────────────────┘    │   │
│  └──────────┼───────────────────────────────────────┘   │
└─────────────┼───────────────────────────────────────────┘
              │
              │ API Calls
              │
┌─────────────▼─────────────────────────────────────────────┐
│                     OpenAI API                             │
│                  (GPT-4 / GPT-4o)                          │
└────────────────────────────────────────────────────────────┘
```

## Core Layers

### 1. API Layer (`app/api/`)

REST API endpoints that expose functionality to external clients.

**Responsibilities**:
- Request validation and parsing
- HTTP response formatting
- Error handling and status codes
- Input sanitization

**Endpoints**:
- `/api/japanese-concept`: Concept explanation endpoint
- `/api/process-content`: Generic content processing
- `/api/validate-file`: File validation and placeholder detection

### 2. Server Actions Layer (`lib/actions/`)

Server-side business logic using Next.js Server Actions.

**Responsibilities**:
- Core business logic
- OpenAI API integration
- Content processing and transformation
- Validation logic

**Components**:
- `japanese-concept-action.ts`: Japanese concept explanation logic
- `content-processor-action.ts`: Generic content processing and file validation

### 3. Utilities Layer (`lib/utils/` & `lib/`)

Reusable utility functions and configurations.

**Responsibilities**:
- Placeholder detection and removal
- OpenAI client configuration
- Helper functions
- Common patterns and algorithms

**Components**:
- `placeholder-detector.ts`: Pattern matching and content cleaning
- `openai.ts`: OpenAI client initialization

### 4. Type System (`types/`)

TypeScript type definitions for type safety across the application.

**Responsibilities**:
- Interface definitions
- Type exports
- API contract definitions
- Shared type utilities

## Data Flow

### Japanese Concept Explanation Flow

```
1. Client Request
   └─> POST /api/japanese-concept
       └─> { query: "What is ikigai?" }

2. API Route Handler
   └─> Validates request body
   └─> Calls server action

3. Server Action (explainJapaneseConcept)
   └─> Removes placeholders from query
   └─> Validates cleaned content
   └─> Builds conversation context
   └─> Calls OpenAI API

4. OpenAI Processing
   └─> Applies system prompt
   └─> Generates concept explanation
   └─> Returns formatted response

5. Response Parsing
   └─> Extracts structured data
   └─> Parses concept name, explanation, origin, application

6. API Response
   └─> Returns JSON with concept data
   └─> Includes timestamp and success status
```

### Content Processing Flow

```
1. Client Request
   └─> POST /api/process-content
       └─> { content: "...", processType: "improve" }

2. API Route Handler
   └─> Validates request
   └─> Determines process type

3. Server Action (processContent)
   └─> Detects placeholders
   └─> Removes placeholders
   └─> Validates content
   └─> Checks if documentation file

4. OpenAI Processing
   └─> Applies process-specific prompt
   └─> Enhances/summarizes/analyzes content

5. API Response
   └─> Returns processed content
   └─> Includes warnings if placeholders found
   └─> Returns cleaned version
```

## Key Design Decisions

### 1. Server Actions Over Client Components

**Decision**: Use Next.js Server Actions exclusively for backend logic.

**Rationale**:
- Keeps API keys secure on the server
- Reduces client bundle size
- Improves performance
- Simplifies architecture

**Trade-offs**:
- No client-side interactivity in current version
- Requires server deployment (cannot be fully static)

### 2. Placeholder Detection System

**Decision**: Implement comprehensive placeholder detection before processing content.

**Rationale**:
- Ensures production-ready output
- Prevents accidental publishing of placeholder text
- Validates README and LICENSE files
- Reduces manual review burden

**Implementation**:
- Pattern-based detection (regex)
- Keyword matching
- Line-level filtering
- Whitespace normalization

### 3. Modular Content Processing

**Decision**: Separate Japanese concept logic from generic content processing.

**Rationale**:
- Allows different processing strategies
- Makes system extensible
- Enables reuse in other contexts
- Maintains separation of concerns

### 4. Type-Safe API Contracts

**Decision**: Use TypeScript interfaces for all API inputs and outputs.

**Rationale**:
- Compile-time type checking
- Better IDE support
- Self-documenting code
- Reduces runtime errors

## Technology Choices

### Next.js 16 App Router

**Why**: 
- Native server actions support
- File-based routing
- Built-in API routes
- Excellent TypeScript support
- Server-side rendering capabilities

### OpenAI API

**Why**:
- State-of-the-art language understanding
- Excellent at explaining cultural concepts
- Reliable API with good documentation
- Supports conversation history
- Flexible prompt engineering

### TypeScript

**Why**:
- Type safety
- Enhanced IDE support
- Catches errors at compile time
- Better refactoring support
- Improved code documentation

### pnpm

**Why**:
- Fast package installation
- Efficient disk space usage
- Strict dependency management
- Modern package manager

## Security Considerations

### 1. API Key Protection

- OpenAI API key stored in environment variables
- Never exposed to client
- Server-side validation only

### 2. Input Validation

- All user inputs validated before processing
- Content length limits enforced
- Type checking on all inputs

### 3. Error Handling

- Errors logged server-side only
- Generic error messages to clients
- No sensitive information in error responses

### 4. Rate Limiting (Recommended)

Not currently implemented, but recommended for production:
- IP-based rate limiting
- API key quotas
- Request throttling

## Performance Considerations

### 1. Response Times

- OpenAI API calls: 2-10 seconds (typical)
- Placeholder detection: <10ms
- Total response time: Primarily limited by OpenAI API

### 2. Optimization Strategies

**Current**:
- Efficient placeholder detection algorithms
- Minimal data transfer
- Server-side caching of OpenAI client

**Future Improvements**:
- Response caching for common queries
- Streaming responses from OpenAI
- Background processing for long operations
- Database storage for conversation history

### 3. Scalability

**Current Architecture**:
- Stateless server actions
- Horizontal scaling possible
- No database dependencies

**Scaling Recommendations**:
- Add Redis for caching
- Implement CDN for static assets
- Use database for conversation persistence
- Add queue system for background jobs

## Extensibility Points

### 1. Adding New Processing Types

Extend `ProcessType` in `types/index.ts` and add case in `content-processor-action.ts`:

```typescript
type ProcessType = 'improve' | 'summarize' | 'analyze' | 'translate' | 'custom';
```

### 2. Adding New Validation Rules

Add patterns to `PLACEHOLDER_PATTERNS` in `placeholder-detector.ts`:

```typescript
/new-pattern-here/g,
```

### 3. Supporting Multiple AI Models

Extend `openai.ts` to support model selection:

```typescript
export async function createCompletion(model: string, messages: Message[]) {
  return openai.chat.completions.create({ model, messages });
}
```

### 4. Adding Authentication

Wrap server actions with authentication middleware:

```typescript
export async function explainJapaneseConcept(request: Request) {
  await requireAuth(request);
  // ... existing logic
}
```

## Testing Strategy

### Unit Tests (Recommended)

- Test placeholder detection functions
- Test response parsing logic
- Mock OpenAI API calls

### Integration Tests (Recommended)

- Test API endpoints end-to-end
- Test server actions with real OpenAI API
- Test error handling paths

### Example Test Structure

```typescript
describe('Placeholder Detector', () => {
  it('should detect placeholder patterns', () => {
    expect(hasPlaceholders('[TODO]')).toBe(true);
  });
  
  it('should remove placeholders', () => {
    const cleaned = removePlaceholders('Text with [placeholder]');
    expect(cleaned).not.toContain('[placeholder]');
  });
});
```

## Deployment Considerations

### Environment Variables

Required for all deployments:
```bash
OPENAI_API_KEY=sk-...
```

### Hosting Recommendations

- **Vercel**: Optimal for Next.js (built by same team)
- **Netlify**: Good alternative with edge functions
- **AWS Lambda**: For custom infrastructure
- **Docker**: For containerized deployments

### Build Process

```bash
# Install dependencies
pnpm install

# Build production bundle
pnpm build

# Start production server
pnpm start
```

## Monitoring and Observability

### Recommended Additions

1. **Logging**: Add structured logging (e.g., Pino, Winston)
2. **Error Tracking**: Integrate Sentry or similar
3. **Analytics**: Track API usage patterns
4. **Performance Monitoring**: Add APM (Application Performance Monitoring)

### Key Metrics to Track

- API response times
- OpenAI API success/failure rates
- Placeholder detection hit rates
- Error rates by endpoint
- Token usage and costs

## Future Architecture Enhancements

### Short Term

1. Add response caching layer
2. Implement rate limiting
3. Add conversation persistence (database)
4. Create frontend interface

### Long Term

1. Multi-model AI support (Claude, Gemini)
2. Vector database for semantic search
3. Real-time streaming responses
4. WebSocket support for live conversations
5. Multi-language support
6. User authentication and profiles
7. Analytics dashboard
8. Admin panel for content curation

## Conclusion

The Satomi architecture is designed to be:
- **Modular**: Easy to extend and modify
- **Type-Safe**: Full TypeScript support
- **Scalable**: Stateless design enables horizontal scaling
- **Maintainable**: Clear separation of concerns
- **Secure**: Server-side API key management

The current implementation provides a solid foundation for a Japanese concept learning platform while remaining flexible enough to accommodate future enhancements and features.

