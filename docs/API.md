# API Documentation

Complete API reference for Satomi backend services.

## Base URL

All API endpoints are relative to your application's base URL:

```
http://localhost:3000  (development)
https://yourdomain.com  (production)
```

## Authentication

Currently, the API does not require user authentication. The OpenAI API key is configured server-side through environment variables.

## Common Response Format

All API endpoints return JSON responses with a common structure:

```typescript
{
  success: boolean;      // Indicates if the request was successful
  timestamp: string;     // ISO 8601 timestamp
  error?: string;        // Error message (only if success is false)
  warnings?: string[];   // Optional warnings
  // ... additional endpoint-specific fields
}
```

## Endpoints

### 1. Japanese Concept Explanation

Explains a Japanese cultural concept based on user query.

**Endpoint**: `POST /api/japanese-concept`

**Request Headers**:
```
Content-Type: application/json
```

**Request Body**:
```typescript
{
  query: string;                           // Required: User's question or topic
  conversationHistory?: Array<{            // Optional: Previous conversation
    role: 'user' | 'assistant';
    content: string;
  }>;
}
```

**Example Request**:
```bash
curl -X POST http://localhost:3000/api/japanese-concept \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is ikigai?",
    "conversationHistory": []
  }'
```

**Success Response** (200):
```typescript
{
  success: true,
  concept: {
    name: string;              // Name of the concept (with pronunciation)
    explanation: string;       // What it means
    origin: string;           // Historical and cultural context
    application: string;      // How to apply it in daily life
    fullResponse: string;     // Complete formatted response
  },
  timestamp: string;
}
```

**Error Response** (400, 500):
```typescript
{
  success: false,
  error: string,
  timestamp: string;
}
```

**Error Codes**:
- `400`: Invalid request (missing or invalid query)
- `500`: Server error (OpenAI API failure, etc.)

---

### 2. Content Processing

Processes text content through OpenAI with various processing types.

**Endpoint**: `POST /api/process-content`

**Request Headers**:
```
Content-Type: application/json
```

**Request Body**:
```typescript
{
  content: string;                                           // Required: Text to process
  filename?: string;                                         // Optional: Original filename
  processType?: 'improve' | 'summarize' | 'analyze' | 'custom';  // Optional: Default 'improve'
  customPrompt?: string;                                     // Optional: Used with 'custom' type
}
```

**Process Types**:

| Type | Description |
|------|-------------|
| `improve` | Enhances and polishes content, removes placeholders |
| `summarize` | Creates a concise summary |
| `analyze` | Provides detailed analysis and insights |
| `custom` | Uses your custom system prompt |

**Example Request**:
```bash
curl -X POST http://localhost:3000/api/process-content \
  -H "Content-Type: application/json" \
  -d '{
    "content": "This is my README content with [placeholder] text",
    "filename": "README.md",
    "processType": "improve"
  }'
```

**Success Response** (200):
```typescript
{
  success: true,
  processedContent: string;      // Enhanced/processed content
  originalContent: string;       // Original input content
  hadPlaceholders: boolean;      // Whether placeholders were detected
  warnings?: string[];           // Optional warnings
  timestamp: string;
}
```

**Error Response** (400, 500):
```typescript
{
  success: false,
  error: string,
  hadPlaceholders?: boolean,
  warnings?: string[],
  timestamp: string;
}
```

---

### 3. File Validation

Validates file content for production readiness, especially README and LICENSE files.

**Endpoint**: `POST /api/validate-file`

**Request Headers**:
```
Content-Type: application/json
```

**Request Body**:
```typescript
{
  filename: string;    // Required: Filename (e.g., "README.md")
  content: string;     // Required: File content to validate
}
```

**Example Request**:
```bash
curl -X POST http://localhost:3000/api/validate-file \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "README.md",
    "content": "# My Project\n\nThis is a [placeholder] description."
  }'
```

**Success Response** (200):
```typescript
{
  valid: boolean;              // Whether the file passed validation
  errors: string[];            // List of validation errors
  warnings: string[];          // List of warnings
  cleanedContent?: string;     // Content with placeholders removed (if any)
}
```

**Special Handling**:

The validator applies special rules for documentation files:

- **README files**: Checks for minimum length, placeholder text
- **LICENSE files**: Ensures file is complete (minimum length requirement)
- **All files**: Removes common placeholder patterns

**Placeholder Patterns Detected**:
- `[text]`, `{text}`, `<text>`
- `YOUR_*`, `REPLACE_*`
- `TODO:`, `FIXME:`
- `example.com`, `lorem ipsum`
- `${VARIABLE}`
- Multiple underscores or ellipses

---

## Server Actions

For Next.js server components, you can use server actions directly instead of API routes:

### explainJapaneseConcept

```typescript
import { explainJapaneseConcept } from '@/lib/actions/japanese-concept-action';

const result = await explainJapaneseConcept({
  query: "What is mono no aware?",
  conversationHistory: [
    { role: "user", content: "Tell me about beauty" },
    { role: "assistant", content: "Japanese aesthetics..." }
  ]
});
```

### processContent

```typescript
import { processContent } from '@/lib/actions/content-processor-action';

const result = await processContent({
  content: "Content to improve",
  filename: "README.md",
  processType: "improve"
});
```

### validateFileContent

```typescript
import { validateFileContent } from '@/lib/actions/content-processor-action';

const validation = await validateFileContent("LICENSE", fileContent);

if (!validation.valid) {
  console.error("Validation errors:", validation.errors);
}
```

---

## Rate Limiting

Currently, there is no rate limiting implemented. Consider adding rate limiting for production deployments to prevent abuse and control OpenAI API costs.

Recommended implementations:
- Use `@upstash/ratelimit` with Redis
- Implement IP-based or API key-based rate limiting
- Set limits per endpoint based on usage patterns

---

## Error Handling

All endpoints use consistent error handling:

### Client Errors (4xx)

**400 Bad Request**: Invalid input parameters
```json
{
  "success": false,
  "error": "Query is required and must be a string"
}
```

### Server Errors (5xx)

**500 Internal Server Error**: Server-side or OpenAI API errors
```json
{
  "success": false,
  "error": "OpenAI API request failed: Rate limit exceeded"
}
```

### Common Error Messages

| Error | Meaning | Solution |
|-------|---------|----------|
| "Query is required" | Missing required field | Include `query` in request body |
| "Content is required" | Missing required field | Include `content` in request body |
| "Content validation failed" | Invalid content (empty or only placeholders) | Provide valid content |
| "No response generated from OpenAI" | OpenAI API returned empty response | Check OpenAI API status, retry request |
| "Invalid API key" | OPENAI_API_KEY is missing or invalid | Verify environment variable is set correctly |

---

## Best Practices

### 1. Conversation History

Keep conversation history limited to recent messages (e.g., last 10 messages) to reduce token usage and costs.

### 2. Content Length

For large documents, consider chunking content and processing in batches. The OpenAI API has token limits:
- GPT-4: Up to 128k tokens (approximately 96,000 words)
- Consider context window size when sending conversation history

### 3. Error Handling

Always check the `success` field before accessing response data:

```typescript
const response = await fetch('/api/japanese-concept', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ query: 'What is ikigai?' })
});

const data = await response.json();

if (data.success) {
  console.log(data.concept.fullResponse);
} else {
  console.error('Error:', data.error);
}
```

### 4. Caching

Consider implementing caching for frequently asked concepts to reduce API calls and costs:

```typescript
// Example with simple in-memory cache
const conceptCache = new Map<string, ConceptResponse>();

if (conceptCache.has(query)) {
  return conceptCache.get(query);
}

const result = await explainJapaneseConcept({ query });
conceptCache.set(query, result);
```

---

## Testing

### cURL Examples

**Test Japanese Concept API**:
```bash
curl -X POST http://localhost:3000/api/japanese-concept \
  -H "Content-Type: application/json" \
  -d '{"query": "Explain wabi-sabi"}'
```

**Test Content Processing**:
```bash
curl -X POST http://localhost:3000/api/process-content \
  -H "Content-Type: application/json" \
  -d '{
    "content": "This is test content with TODO: placeholder",
    "processType": "improve"
  }'
```

**Test File Validation**:
```bash
curl -X POST http://localhost:3000/api/validate-file \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "README.md",
    "content": "# Project\nDescription here"
  }'
```

---

## Support

For issues or questions about the API, please refer to the main documentation or create an issue in the project repository.

