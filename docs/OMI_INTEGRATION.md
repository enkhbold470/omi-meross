# OMI Integration Guide

Complete guide for integrating Satomi with OMI (AI Wearable Device) to deliver beautifully explained Japanese concepts through conversation.

## Overview

Satomi's OMI integration allows users to ask about Japanese cultural concepts through natural conversation with their OMI wearable device. Each response delivers a beautifully formatted 3-minute read with:

- ✨ Clear meaning and definition
- 📜 Historical and cultural origin
- 💡 Practical application in daily life
- 🎌 Quotable wisdom perfect for sharing

## Business Model Alignment

- **Free Conversation**: All concept explanations are free
- **3-Minute Reads**: Optimized response length for engagement
- **Quotable Content**: Formatted for screenshots and sharing
- **Cultural Accuracy**: Powered by OpenAI with curated prompts
- **Media Brand**: Foundation for audience building and monetization

## Quick Start

### 1. Deploy Satomi

Deploy your Satomi instance to a public URL:

```bash
# Using Vercel (recommended)
vercel --prod

# Or use ngrok for testing
ngrok http 3000
```

### 2. Get Your Webhook URL

Your OMI webhook URL will be:
```
https://your-domain.com/api/omi/webhook
```

### 3. Create OMI App

1. Open the OMI mobile app
2. Go to **"Explore" → "Create an App"**
3. Select **"Integration App"**
4. Enter your webhook URL
5. Name: **"Satomi - Japanese Concepts"**
6. Description: **"Beautifully explained Japanese concepts"**
7. Save and enable the app

### 4. Start Asking Questions

Speak to your OMI device:
- "What is ikigai?"
- "Explain wabi-sabi to me"
- "Tell me about kaizen"

## How It Works

### Conversation Flow

```
1. User speaks to OMI device
   ↓
2. OMI transcribes speech to text
   ↓
3. OMI sends transcript to Satomi webhook
   ↓
4. Satomi detects Japanese concept query
   ↓
5. Satomi processes through OpenAI
   ↓
6. Satomi returns formatted explanation
   ↓
7. OMI displays/speaks the response
```

### Example Interaction

**User**: "What is ikigai?"

**Satomi Response**:
```
🇯🇵 Ikigai (生き甲斐)

✨ Meaning:
Ikigai is a Japanese concept meaning "reason for being"...

📜 Origin:
The term originates from the island of Okinawa...

💡 How to Apply:
To discover your ikigai, reflect on what you love...

---
A beautifully explained Japanese concept from Satomi 🎌
```

## API Endpoints

### 1. Real-Time Transcript Webhook

**Endpoint**: `POST /api/omi/webhook`

Receives real-time transcripts from OMI and returns concept explanations.

**Request from OMI**:
```json
{
  "session_id": "RYEXvYutQeb3OwmmEsYDgiafmd02",
  "segments": [
    {
      "id": "seg_001",
      "text": "What is ikigai?",
      "speaker": "SPEAKER_0",
      "speaker_id": 0,
      "is_user": true,
      "person_id": null,
      "start": 0.0,
      "end": 2.5,
      "translations": [],
      "speech_profile_processed": true
    }
  ]
}
```

**Response to OMI**:
```json
{
  "message": "🇯🇵 Ikigai (生き甲斐)\n\n✨ Meaning:\n...",
  "concept_name": "Ikigai",
  "timestamp": "2025-11-01T..."
}
```

### 2. Memory Creation Webhook

**Endpoint**: `POST /api/omi/memory`

Triggered when OMI creates a memory. Annotates memories that mention Japanese concepts.

**Request from OMI**:
```json
{
  "memory_id": "mem_789",
  "session_id": "session_123",
  "segments": [
    {
      "id": "seg_001",
      "text": "I learned about ikigai today...",
      "speaker": "SPEAKER_0",
      "speaker_id": 0,
      "is_user": true,
      "start": 0.0,
      "end": 5.0
    }
  ],
  "created_at": "2025-11-01T..."
}
```

**Response to OMI**:
```json
{
  "status": "received",
  "memory_id": "mem_789",
  "detected_concepts": ["ikigai"],
  "annotation": "📖 Ikigai (生き甲斐)\n...",
  "timestamp": "2025-11-01T..."
}
```

## Trigger Keywords

Satomi responds to these keywords and phrases:

### Direct Concept Names
- ikigai, wabi-sabi, kaizen, kintsugi
- mono no aware, omotenashi, gaman, shouganai
- ichi-go ichi-e, komorebi, yugen, shibui
- And more...

### Question Phrases
- "What is..."
- "Explain..."
- "Tell me about..."
- "Meaning of..."
- "Define..."
- "Japanese concept..."
- "Japanese philosophy..."

## Response Format

All responses follow this structure:

```
🇯🇵 [Concept Name with Japanese Characters]

✨ Meaning:
[Clear, accessible explanation]

📜 Origin:
[Historical and cultural context]

💡 How to Apply:
[Practical applications for daily life]

---
A beautifully explained Japanese concept from Satomi 🎌
```

### Response Characteristics

- **Length**: 3-minute read (~500-700 words)
- **Tone**: Warm, conversational, respectful
- **Format**: Structured with emojis for scannability
- **Content**: Quotable wisdom, shareable insights
- **Accuracy**: Curated to avoid "ikigai-washing"

## Testing Your Integration

### Using webhook.site

For quick testing without deployment:

1. Go to https://webhook.site
2. Copy your unique URL
3. Test locally:

```bash
curl -X POST https://webhook.site/your-id \
  -H "Content-Type: application/json" \
  -d '{
    "transcript": "What is ikigai?",
    "session_id": "test_123"
  }'
```

### Using ngrok

For testing with your local Satomi instance:

```bash
# Start Satomi
pnpm dev

# In another terminal, expose via ngrok
ngrok http 3000

# Use ngrok URL in OMI app
https://abc123.ngrok.io/api/omi/webhook
```

### Testing Script

Create `test-omi.sh`:

```bash
#!/bin/bash

WEBHOOK_URL="https://your-domain.com/api/omi/webhook"

# Test 1: Basic concept query
curl -X POST $WEBHOOK_URL \
  -H "Content-Type: application/json" \
  -d '{
    "transcript": "What is ikigai?",
    "session_id": "test_1"
  }'

# Test 2: Different concept
curl -X POST $WEBHOOK_URL \
  -H "Content-Type: application/json" \
  -d '{
    "transcript": "Explain wabi-sabi",
    "session_id": "test_2"
  }'

# Test 3: Non-concept query
curl -X POST $WEBHOOK_URL \
  -H "Content-Type: application/json" \
  -d '{
    "transcript": "What is the weather today?",
    "session_id": "test_3"
  }'
```

## Configuration

### Environment Variables

Required:
```bash
OPENAI_API_KEY=sk-proj-your-key-here
```

Optional:
```bash
# OMI specific settings
OMI_RATE_LIMIT_ENABLED=true
OMI_MAX_REQUESTS_PER_MINUTE=10
```

### Customization

Edit `lib/omi/config.ts` to customize:

```typescript
export const OMI_CONFIG = {
  app: {
    name: 'Your App Name',
    description: 'Your description',
    // ...
  },
  
  response: {
    maxLength: 1500,
    includeEmoji: true,
    includeOrigin: true,
    includeApplication: true,
  },
};
```

## Monitoring and Analytics

### Logging

All OMI webhooks are logged:

```typescript
console.log('OMI webhook received:', {
  transcript,
  sessionId,
  userId,
  timestamp: new Date().toISOString(),
});
```

### Metrics to Track

1. **Request Volume**: Number of OMI webhook calls
2. **Concept Queries**: Most asked concepts
3. **Response Times**: Average OpenAI processing time
4. **Error Rates**: Failed requests and reasons
5. **User Engagement**: Repeat queries per session

### Analytics Implementation

Add analytics to `app/api/omi/webhook/route.ts`:

```typescript
// Track concept query
await analytics.track({
  event: 'japanese_concept_queried',
  properties: {
    concept_name: result.concept.name,
    user_id: userId,
    session_id: sessionId,
  },
});
```

## Advanced Features

### 1. Conversation Context

Maintain conversation history across multiple queries:

```typescript
// Store in Redis or database
const conversationHistory = await getConversationHistory(sessionId);

const result = await explainJapaneseConcept({
  query: transcript,
  conversationHistory,
});

await saveConversationHistory(sessionId, result);
```

### 2. Personalized Responses

Adapt responses based on user preferences:

```typescript
const userProfile = await getUserProfile(userId);

const prompt = buildPersonalizedPrompt(transcript, userProfile);
```

### 3. Multi-Language Support

Support multiple languages (future):

```typescript
const language = detectLanguage(transcript);
const translatedResponse = await translateResponse(response, language);
```

## Deployment Checklist

Before going live:

- [ ] Deploy Satomi to production (Vercel/AWS/etc.)
- [ ] Set `OPENAI_API_KEY` in production environment
- [ ] Test all OMI webhook endpoints
- [ ] Configure webhook URL in OMI app
- [ ] Test with real OMI device
- [ ] Monitor logs for errors
- [ ] Set up analytics tracking
- [ ] Test rate limiting
- [ ] Verify response formatting on OMI
- [ ] Create OMI app submission (if going public)

## Publishing Your OMI App

### Private App (Testing)

1. Create app in OMI mobile app
2. Add webhook URL
3. Only you can use it (owner/tester)

### Public App (Distribution)

1. Test thoroughly with private app
2. Submit app via OMI mobile app:
   - Go to "My Apps" → "Submit App"
   - Fill in app details
   - Provide webhook URL
   - Add screenshots/examples
3. Wait for OMI team review
4. Once approved, available in OMI app store

### App Submission Checklist

- [ ] Clear app name and description
- [ ] Working webhook URL (public)
- [ ] Privacy policy (if collecting data)
- [ ] Terms of service
- [ ] Example queries documented
- [ ] Screenshots or demo video
- [ ] Contact information

## Troubleshooting

### "App not responding"

**Cause**: Webhook URL not reachable
**Solution**: 
- Verify deployment is live
- Test webhook URL directly with curl
- Check firewall/security settings

### "Empty responses"

**Cause**: OpenAI API key not set or invalid
**Solution**:
- Check `OPENAI_API_KEY` in environment
- Verify key is valid at OpenAI dashboard
- Check OpenAI API quota/billing

### "Rate limit errors"

**Cause**: Too many requests to OpenAI
**Solution**:
- Implement caching for common queries
- Add rate limiting per user
- Upgrade OpenAI plan if needed

### "Webhook timeout"

**Cause**: OpenAI processing taking too long
**Solution**:
- Optimize prompts for faster responses
- Increase webhook timeout in OMI settings
- Implement async processing with callbacks

## Example Use Cases

### 1. Daily Wisdom

User asks OMI for a random Japanese concept each morning:
- "Tell me a Japanese concept"
- Satomi picks and explains a concept

### 2. Cultural Learning

User learning Japanese culture through conversation:
- Progressive questioning
- Context-aware follow-ups
- Building knowledge over time

### 3. Mindfulness Practice

User asks about concepts related to mindfulness:
- Wabi-sabi for acceptance
- Mono no aware for appreciation
- Ichi-go ichi-e for presence

### 4. Content Creation

User gathering ideas for blog/social media:
- Ask about multiple concepts
- Get quotable wisdom
- Share formatted responses

## Support and Resources

- **OMI Documentation**: https://docs.omi.me
- **Satomi Docs**: `/docs` folder
- **GitHub**: BasedHardware/omi
- **Community**: OMI Discord/Forum

## Future Enhancements

### Planned Features

- [ ] Voice responses (audio format)
- [ ] Image generation (concept illustrations)
- [ ] Daily concept subscriptions
- [ ] Conversation analytics dashboard
- [ ] Multi-language support
- [ ] Concept quizzes and learning paths
- [ ] Social sharing integration
- [ ] Premium concepts (paid tier)

### Integration Ideas

- Calendar reminders with daily concepts
- Social media auto-posting
- Note-taking app integration
- Podcast episode generation
- Email newsletter compilation

## Conclusion

The OMI integration transforms Satomi into a conversational Japanese concept learning platform that users can access hands-free through their wearable device. Perfect for:

- Building a media brand around Japanese culture
- Engaging audience through conversation
- Delivering quotable, shareable content
- Scaling to premium features and monetization

**Ready to go live!** Deploy Satomi, configure your OMI webhook, and start delivering beautifully explained Japanese concepts. 🇯🇵✨

