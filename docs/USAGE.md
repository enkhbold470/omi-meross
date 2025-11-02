# Usage Guide

Complete guide for using Satomi's API and server actions.

## Quick Start

### 1. Setup Environment

```bash
# Install dependencies
pnpm install

# Configure OpenAI API key
echo "OPENAI_API_KEY=your-key-here" > .env.local

# Start development server
pnpm dev
```

### 2. Test the API

```bash
# Test Japanese concept endpoint
curl -X POST http://localhost:3000/api/japanese-concept \
  -H "Content-Type: application/json" \
  -d '{"query": "What is ikigai?"}'
```

## Using the API

### Japanese Concept Explanation

Get detailed explanations of Japanese cultural concepts.

#### Basic Usage

```bash
curl -X POST http://localhost:3000/api/japanese-concept \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Explain the concept of wabi-sabi"
  }'
```

#### With Conversation History

```bash
curl -X POST http://localhost:3000/api/japanese-concept \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How can I practice it in daily life?",
    "conversationHistory": [
      {
        "role": "user",
        "content": "Explain the concept of wabi-sabi"
      },
      {
        "role": "assistant",
        "content": "Wabi-sabi is a Japanese aesthetic philosophy..."
      }
    ]
  }'
```

#### Response Format

```json
{
  "success": true,
  "concept": {
    "name": "Ikigai (生き甲斐)",
    "explanation": "Ikigai is a Japanese concept meaning 'reason for being'...",
    "origin": "The term originates from the island of Okinawa...",
    "application": "To discover your ikigai, reflect on: What you love...",
    "fullResponse": "**Ikigai (生き甲斐)** [pronounced: ee-kee-guy]\n\n..."
  },
  "timestamp": "2025-11-01T12:00:00.000Z"
}
```

### Content Processing

Process and improve text content using AI.

#### Improve Content

```bash
curl -X POST http://localhost:3000/api/process-content \
  -H "Content-Type: application/json" \
  -d '{
    "content": "This is my project description with [placeholder] text.",
    "processType": "improve"
  }'
```

#### Summarize Content

```bash
curl -X POST http://localhost:3000/api/process-content \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Long article text here...",
    "processType": "summarize"
  }'
```

#### Analyze Content

```bash
curl -X POST http://localhost:3000/api/process-content \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Content to analyze...",
    "processType": "analyze"
  }'
```

#### Custom Processing

```bash
curl -X POST http://localhost:3000/api/process-content \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Text to process",
    "processType": "custom",
    "customPrompt": "Translate this to formal business language"
  }'
```

### File Validation

Validate README and LICENSE files for production readiness.

```bash
curl -X POST http://localhost:3000/api/validate-file \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "README.md",
    "content": "# My Project\n\nThis is a [TODO] description."
  }'
```

#### Response Format

```json
{
  "valid": false,
  "errors": [
    "Content contains placeholder text that must be replaced"
  ],
  "warnings": [
    "Documentation file contained placeholder text. Cleaned version provided."
  ],
  "cleanedContent": "# My Project\n\nThis is a  description."
}
```

## Using Server Actions

For Next.js applications, you can use server actions directly.

### In Server Components

```typescript
// app/concept/page.tsx
import { explainJapaneseConcept } from '@/lib/actions/japanese-concept-action';

export default async function ConceptPage() {
  const result = await explainJapaneseConcept({
    query: "What is ikigai?",
  });

  if (!result.success) {
    return <div>Error: {result.error}</div>;
  }

  return (
    <div>
      <h1>{result.concept?.name}</h1>
      <p>{result.concept?.explanation}</p>
    </div>
  );
}
```

### In Server Actions

```typescript
// app/actions.ts
'use server';

import { explainJapaneseConcept } from '@/lib/actions/japanese-concept-action';

export async function getConcept(formData: FormData) {
  const query = formData.get('query') as string;
  
  return await explainJapaneseConcept({ query });
}
```

### In API Routes

```typescript
// app/api/custom/route.ts
import { NextRequest } from 'next/server';
import { processContent } from '@/lib/actions/content-processor-action';

export async function POST(request: NextRequest) {
  const { content } = await request.json();
  
  const result = await processContent({
    content,
    processType: 'improve',
  });
  
  return Response.json(result);
}
```

## JavaScript/TypeScript SDK Usage

### Fetch API

```typescript
// Basic request
async function askConcept(query: string) {
  const response = await fetch('/api/japanese-concept', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query }),
  });
  
  const data = await response.json();
  
  if (data.success) {
    return data.concept;
  } else {
    throw new Error(data.error);
  }
}

// Usage
const concept = await askConcept("What is kaizen?");
console.log(concept.fullResponse);
```

### With Error Handling

```typescript
async function explainConcept(query: string) {
  try {
    const response = await fetch('/api/japanese-concept', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query }),
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    
    if (!data.success) {
      throw new Error(data.error || 'Request failed');
    }
    
    return data.concept;
  } catch (error) {
    console.error('Error explaining concept:', error);
    throw error;
  }
}
```

### With Conversation History

```typescript
class ConceptChat {
  private history: Array<{ role: 'user' | 'assistant'; content: string }> = [];
  
  async ask(query: string) {
    const response = await fetch('/api/japanese-concept', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        query,
        conversationHistory: this.history,
      }),
    });
    
    const data = await response.json();
    
    if (data.success) {
      // Add to history
      this.history.push({ role: 'user', content: query });
      this.history.push({ 
        role: 'assistant', 
        content: data.concept.fullResponse 
      });
      
      return data.concept;
    } else {
      throw new Error(data.error);
    }
  }
  
  clearHistory() {
    this.history = [];
  }
}

// Usage
const chat = new ConceptChat();
const concept1 = await chat.ask("What is ikigai?");
const concept2 = await chat.ask("How is it different from passion?");
```

## Python Integration

```python
import requests
import json

class SatomiClient:
    def __init__(self, base_url='http://localhost:3000'):
        self.base_url = base_url
        self.history = []
    
    def explain_concept(self, query: str):
        """Get explanation of a Japanese concept"""
        url = f'{self.base_url}/api/japanese-concept'
        
        payload = {
            'query': query,
            'conversationHistory': self.history
        }
        
        response = requests.post(url, json=payload)
        data = response.json()
        
        if data['success']:
            # Update history
            self.history.append({
                'role': 'user',
                'content': query
            })
            self.history.append({
                'role': 'assistant',
                'content': data['concept']['fullResponse']
            })
            
            return data['concept']
        else:
            raise Exception(data.get('error', 'Request failed'))
    
    def process_content(self, content: str, process_type='improve'):
        """Process content through AI"""
        url = f'{self.base_url}/api/process-content'
        
        payload = {
            'content': content,
            'processType': process_type
        }
        
        response = requests.post(url, json=payload)
        data = response.json()
        
        if data['success']:
            return data['processedContent']
        else:
            raise Exception(data.get('error', 'Request failed'))
    
    def validate_file(self, filename: str, content: str):
        """Validate file content"""
        url = f'{self.base_url}/api/validate-file'
        
        payload = {
            'filename': filename,
            'content': content
        }
        
        response = requests.post(url, json=payload)
        return response.json()

# Usage
client = SatomiClient()

# Get concept explanation
concept = client.explain_concept("What is mono no aware?")
print(concept['fullResponse'])

# Process content
improved = client.process_content(
    "This is my [TODO] content",
    process_type='improve'
)
print(improved)

# Validate file
validation = client.validate_file("README.md", readme_content)
if not validation['valid']:
    print("Errors:", validation['errors'])
```

## Common Use Cases

### 1. Learning Platform

```typescript
// Create a learning session
class JapaneseLearningSession {
  private concepts: string[] = [];
  
  async learnConcept(concept: string) {
    const result = await fetch('/api/japanese-concept', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: `Explain ${concept}` }),
    }).then(r => r.json());
    
    if (result.success) {
      this.concepts.push(result.concept.name);
      return result.concept;
    }
  }
  
  getLearnedConcepts() {
    return this.concepts;
  }
}
```

### 2. Content Generator

```typescript
async function generateBlogPost(topic: string) {
  // Get concept explanation
  const conceptResult = await fetch('/api/japanese-concept', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query: `Explain ${topic} in detail` }),
  }).then(r => r.json());
  
  // Enhance for blog format
  const blogResult = await fetch('/api/process-content', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      content: conceptResult.concept.fullResponse,
      processType: 'custom',
      customPrompt: 'Format this as an engaging blog post with sections',
    }),
  }).then(r => r.json());
  
  return blogResult.processedContent;
}
```

### 3. Documentation Validator

```typescript
async function validateProjectDocs() {
  const files = ['README.md', 'LICENSE', 'CONTRIBUTING.md'];
  const results = [];
  
  for (const filename of files) {
    const content = await readFile(filename);
    
    const validation = await fetch('/api/validate-file', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ filename, content }),
    }).then(r => r.json());
    
    results.push({ filename, ...validation });
  }
  
  return results;
}
```

### 4. Chatbot Integration

```typescript
class JapaneseCultureBot {
  async handleMessage(userMessage: string, history: any[]) {
    const result = await fetch('/api/japanese-concept', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        query: userMessage,
        conversationHistory: history,
      }),
    }).then(r => r.json());
    
    if (result.success) {
      return {
        reply: result.concept.fullResponse,
        conceptName: result.concept.name,
      };
    }
  }
}
```

## Rate Limiting Best Practices

To avoid hitting rate limits or excessive costs:

```typescript
// Implement simple caching
const cache = new Map();

async function getCachedConcept(query: string) {
  const cacheKey = query.toLowerCase().trim();
  
  if (cache.has(cacheKey)) {
    return cache.get(cacheKey);
  }
  
  const result = await explainConcept(query);
  cache.set(cacheKey, result);
  
  // Clear cache after 1 hour
  setTimeout(() => cache.delete(cacheKey), 60 * 60 * 1000);
  
  return result;
}
```

## Troubleshooting

### Common Errors

#### "Query is required"
```typescript
// ❌ Wrong
fetch('/api/japanese-concept', {
  method: 'POST',
  body: JSON.stringify({}),
});

// ✅ Correct
fetch('/api/japanese-concept', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ query: "What is ikigai?" }),
});
```

#### "Invalid API key"
Check your environment variable:
```bash
# .env.local
OPENAI_API_KEY=sk-proj-your-actual-key
```

## Next Steps

- Explore the [API Documentation](./API.md)
- Review the [Architecture](./ARCHITECTURE.md)
- Learn about [Deployment](./DEPLOYMENT.md)
- Check the [Examples](./examples/) folder (coming soon)

## Support

For issues or questions, open an issue in the repository or contact support.

