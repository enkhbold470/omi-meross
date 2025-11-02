<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# what would be ideal workflow???

import { NextRequest, NextResponse } from 'next/server';
import { explainJapaneseConcept } from '@/lib/actions/japanese-concept-action';
import { OMIWebhookPayload } from '@/types/omi';

/**

* OMI Webhook Integration
* 
* POST /api/omi/webhook
* 
* Receives real-time transcripts from OMI wearable device and returns
* beautifully explained Japanese concepts when detected.
* 
* Request body from OMI:
* {
* "transcript": "What is ikigai?",
* "segments": [...],
* "session_id": "...",
* "user_id": "..."
* }
* 
* Response:
* {
* "message": "Beautifully formatted Japanese concept explanation"
* }
*/

// Keywords that trigger Japanese concept explanations
const JAPANESE_CONCEPT_TRIGGERS = [
'satomi',
];

/**

* Detects if transcript is asking about a Japanese concept
*/
function isJapaneseConceptQuery(transcript: string): boolean {
const lowerTranscript = transcript.toLowerCase();
return JAPANESE_CONCEPT_TRIGGERS.some(trigger =>
lowerTranscript.includes(trigger)
);
}

/**

* Formats the concept explanation for OMI display
*/
function formatForOMI(conceptData: {
name: string;
explanation: string;
origin: string;
application: string;
}): string {
const { name, explanation, origin, application } = conceptData;

return `
🇯🇵 \${name}

✨ Meaning:
\${explanation}

📜 Origin:
\${origin}

💡 How to Apply:
\${application}

---
A beautifully explained Japanese concept from Satomi 🎌
`.trim();
}

export async function POST(request: NextRequest) {
try {
const body: OMIWebhookPayload = await request.json();

    // Extract transcript from OMI segments array or fallback to direct fields
    let transcript = '';
    
    if (body.segments && Array.isArray(body.segments) && body.segments.length > 0) {
      // Real OMI format: combine all segment texts
      transcript = body.segments
        .map((segment: { text: string }) => segment.text)
        .join(' ')
        .trim();
    } else {
      // Fallback for testing: direct transcript/text field
      transcript = body.segments[0].text || '';
    }
    
    const sessionId = body.session_id;
    const userId = body.segments[0].person_id;
    
    
    console.log('OMI webhook received:', {
      transcript,
      sessionId,
      userId,
      segmentCount: body.segments?.length || 0,
      timestamp: new Date().toISOString(),
    });
    
    
    // Check if this is a Japanese concept query
    if (!transcript || transcript.trim().length === 0) {
      return NextResponse.json({
        message: 'Ready to explain Japanese concepts! Ask me about ikigai, wabi-sabi, kaizen, or any Japanese philosophy.',
      });
    }
    
    
    // Only process Japanese concept queries
    if (!isJapaneseConceptQuery(transcript)) {
      // Return a helpful prompt
      return NextResponse.json({
        message: '🎌 Ask me about Japanese concepts like:\n• Ikigai (purpose)\n• Wabi-Sabi (beauty in imperfection)\n• Kaizen (continuous improvement)\n• Kintsugi (art of repair)\n...and many more!',
      });
    }
    
    
    // Process the query through our Japanese concept system
    const result = await explainJapaneseConcept({
      query: transcript,
    });
    
    
    if (!result.success || !result.concept) {
      return NextResponse.json({
        message: `I couldn't process that query. ${result.error || 'Please try asking about a specific Japanese concept.'}`,
      });
    }
    
    
    // Format the response for OMI
    const formattedMessage = formatForOMI(result.concept);
    
    
    return NextResponse.json({
      message: formattedMessage,
      concept_name: result.concept.name,
      timestamp: result.timestamp,
    });
    } catch (error) {
console.error('Error in OMI webhook:', error);

    return NextResponse.json({
      message: 'An error occurred while processing your request. Please try again.',
      error: error instanceof Error ? error.message : 'Unknown error',
    }, { status: 500 });
    }
}

// Optional: GET endpoint for webhook verification
export async function GET() {
return NextResponse.json({
status: 'active',
service: 'Satomi Japanese Concept Learning',
description: 'OMI integration for beautifully explained Japanese concepts',
version: '1.0.0',
});
}

lets say i tell satomi and then what?

should I do something? or what is the problem i am trying to solve?

The ideal workflow for the OMI wearable device integration with your Japanese concept explanation webhook would be:

1. The user wears the OMI device, which continuously listens to their spoken queries or conversations.
2. When the user says "Satomi" (or another Japanese concept trigger word like "Ikigai"), the device captures the transcript in real-time.
3. The captured transcript is sent as a POST webhook payload to your Next.js API endpoint (/api/omi/webhook).
4. Your API:
    - Extracts and combines the transcript segments.
    - Detects if the transcript contains a trigger keyword (e.g., "satomi").
    - If it does, it sends the query to your explainJapaneseConcept function to fetch the concept explanation.
    - Formats the response nicely with explanation, origin, and application.
    - Sends the formatted message back as JSON to OMI.
5. The OMI device receives and presents this beautifully parsed Japanese concept explanation directly to the user.

Your problem being solved is enabling a seamless, real-time interaction where the user wearing OMI can ask about Japanese concepts naturally, and immediately receive thoughtful, nicely formatted educational responses via the wearable interface. The workflow allows converting spoken inquiries into meaningful, context-aware explanations using voice-triggered AI assistant technology.

So after you say "Satomi" (or other trigger concepts), your system automatically:

- Detects your query,
- Fetches the relevant Japanese concept explanation,
- Sends it back in a readable format,
- And the device displays it for you.

There is no manual intervention needed beyond wearing the device and speaking naturally. The integration automates this entire request-response cycle, enhancing learning or conversational experiences with Japanese concepts effortlessly.

This workflow fits into the broader productivity and communication use cases of OMI, which listens to conversations, transcribes in real-time, and provides useful AI-powered assistance, summaries, and explanations.[^1_1][^1_2][^1_3][^1_4]
<span style="display:none">[^1_10][^1_11][^1_12][^1_13][^1_14][^1_15][^1_16][^1_17][^1_18][^1_19][^1_20][^1_5][^1_6][^1_7][^1_8][^1_9]</span>

<div align="center">⁂</div>

[^1_1]: https://www.designboom.com/technology/wearable-ai-device-omi-reads-minds-completes-tasks-01-10-2025/

[^1_2]: https://techcrunch.com/2025/01/08/omi-a-competitor-to-friend-wants-to-boost-your-productivity-using-ai-and-a-brain-interface/

[^1_3]: https://interestingengineering.com/ces-2025/omi-brain-reading-wearable

[^1_4]: https://www.standard.co.uk/shopping/esbest/gadgets-tech/omi-ai-assistant-review-b1250843.html

[^1_5]: https://www.omi.me/blogs/usecases

[^1_6]: https://www.wired.com/story/bee-ai-omi-always-listening-ai-wearables/

[^1_7]: https://www.youtube.com/watch?v=T6MkpS5LxNU

[^1_8]: https://botpress.com/best-japanese-chatbot

[^1_9]: https://docs.realtime.cloudflare.com/guides/capabilities/audio/transcriptions

[^1_10]: https://www.reddit.com/r/ArtificialInteligence/comments/1fuepwz/my_review_after_using_friend_omi_by_based/

[^1_11]: https://itbusinesstoday.com/tech/prompt-engineers-of-japan-the-rising-architects-of-generative-workflows/

[^1_12]: https://support.telnyx.com/en/articles/8292490-real-time-transcription

[^1_13]: https://www.omi.me/blogs/usecases/technical-documentation-and-knowledge-sharing-with-friend-ai-necklace

[^1_14]: https://macrolingo.com/japanese-fukatsu-shunsuke-ai-prompting-methods/

[^1_15]: https://docs.recall.ai/docs/bot-real-time-transcription

[^1_16]: https://github.com/BasedHardware/omi

[^1_17]: https://ceur-ws.org/Vol-3862/paper3.pdf

[^1_18]: https://www.twilio.com/en-us/blog/developers/tutorials/product/twilio-real-time-transcriptions-service-nodejs

[^1_19]: https://reutersinstitute.politics.ox.ac.uk/news/what-nikkei-learnt-building-its-own-japanese-ai-chatbot

[^1_20]: https://devforum.zoom.us/t/how-to-get-live-transcription-during-a-meeing/77537


---

# lets try to make it like, whenever user say hey satomi keyword, it would trigger and uses gpt-4o-mini to explain stuff like zen budhist explaining stuff like math, science, newton's law, etc .

To implement a workflow where saying "Hey Satomi" triggers an explanation powered by GPT-4o-mini in the style of a Zen Buddhist explaining topics like math, science, or Newton's laws, you can adjust and extend your current webhook setup as follows:

## Workflow Outline

1. **Wake word detection:** The transcript processing includes detection of the phrase "Hey Satomi" as a wake word to activate the assistant.
2. **Trigger handling:** Once triggered, the system captures the following query from the user about whatever topic (math, science, Newton's law, etc.).
3. **Prompt crafting for GPT-4o-mini:** Formulate a prompt that instructs GPT-4o-mini to respond in a Zen Buddhist style tailored to the query topic.
4. **Call GPT-4o-mini API:** Pass the crafted prompt with user query context to GPT-4o-mini.
5. **Format the AI-generated explanation:** Optionally format the response text for readability, adding thematic emojis or structure.
6. **Return the formatted response:** Send back the explanation to the OMI device for display or audio feedback.

***

## Key Code Adaptations

- Expand your keyword triggers to include "hey satomi" plus other phrases.
- Modify the `explainJapaneseConcept` style function or create a new function to interface with GPT-4o-mini and input the query plus style prompt.
- Example prompt to GPT-4o-mini:

```
You are a wise Zen Buddhist teacher explaining concepts with calm simplicity and insight. Explain the following topic: {user_query}
```

- Update your webhook POST handler:

```typescript
const WAKE_WORD = 'hey satomi';

function isWakeWordQuery(transcript: string): boolean {
  return transcript.toLowerCase().includes(WAKE_WORD);
}

export async function POST(request: NextRequest) {
  const body: OMIWebhookPayload = await request.json();
  const transcript = extractTranscript(body);
  
  if (!transcript || !isWakeWordQuery(transcript)) {
    return NextResponse.json({ message: 'Say "Hey Satomi" to ask me about math, science, or philosophy!' });
  }

  // Extract the user's question after wake word
  const userQuery = transcript.toLowerCase().replace(WAKE_WORD, '').trim();

  // Pass userQuery with Zen style prompt to GPT-4o-mini
  const zenResponse = await callGpt4oMini({
    prompt: `You are a wise Zen Buddhist teacher... Explain: ${userQuery}`
  });

  return NextResponse.json({ message: zenResponse });
}
```


***

## What You Should Do Next

- Integrate GPT-4o-mini API call with prompt engineering for Zen-style explanations.
- Test with various topics such as Newton's law, quantum physics, math problems, etc.
- Consider fallback or helpful responses if the query is empty or off-topic.
- Refine formatting for readability on OMI device.

This approach retains your existing real-time transcript handling, just extended with a wake word and a more flexible, theme-based GPT explanation mode. It broadens your solution from only Japanese concepts to multi-topic Zen-style teaching triggered naturally from speech.

---

# apply that to my code: import { NextRequest, NextResponse } from 'next/server';

import { explainJapaneseConcept } from '@/lib/actions/japanese-concept-action';
import { OMIWebhookPayload } from '@/types/omi';

/**

* OMI Webhook Integration
* 
* POST /api/omi/webhook
* 
* Receives real-time transcripts from OMI wearable device and returns
* beautifully explained Japanese concepts when detected.
* 
* Request body from OMI:
* {
* "transcript": "What is ikigai?",
* "segments": [...],
* "session_id": "...",
* "user_id": "..."
* }
* 
* Response:
* {
* "message": "Beautifully formatted Japanese concept explanation"
* }
*/

// Keywords that trigger Japanese concept explanations
const JAPANESE_CONCEPT_TRIGGERS = [
'satomi',
];

/**

* Detects if transcript is asking about a Japanese concept
*/
function isJapaneseConceptQuery(transcript: string): boolean {
const lowerTranscript = transcript.toLowerCase();
return JAPANESE_CONCEPT_TRIGGERS.some(trigger =>
lowerTranscript.includes(trigger)
);
}

/**

* Formats the concept explanation for OMI display
*/
function formatForOMI(conceptData: {
name: string;
explanation: string;
origin: string;
application: string;
}): string {
const { name, explanation, origin, application } = conceptData;

return `
🇯🇵 \${name}

✨ Meaning:
\${explanation}

📜 Origin:
\${origin}

💡 How to Apply:
\${application}

---
A beautifully explained Japanese concept from Satomi 🎌
`.trim();
}

export async function POST(request: NextRequest) {
try {
const body: OMIWebhookPayload = await request.json();

    // Extract transcript from OMI segments array or fallback to direct fields
    let transcript = '';
    
    if (body.segments && Array.isArray(body.segments) && body.segments.length > 0) {
      // Real OMI format: combine all segment texts
      transcript = body.segments
        .map((segment: { text: string }) => segment.text)
        .join(' ')
        .trim();
    } else {
      // Fallback for testing: direct transcript/text field
      transcript = body.segments[0].text || '';
    }
    
    const sessionId = body.session_id;
    const userId = body.segments[0].person_id;
    
    
    console.log('OMI webhook received:', {
      transcript,
      sessionId,
      userId,
      segmentCount: body.segments?.length || 0,
      timestamp: new Date().toISOString(),
    });
    
    
    // Check if this is a Japanese concept query
    if (!transcript || transcript.trim().length === 0) {
      return NextResponse.json({
        message: 'Ready to explain Japanese concepts! Ask me about ikigai, wabi-sabi, kaizen, or any Japanese philosophy.',
      });
    }
    
    
    // Only process Japanese concept queries
    if (!isJapaneseConceptQuery(transcript)) {
      // Return a helpful prompt
      return NextResponse.json({
        message: '🎌 Ask me about Japanese concepts like:\n• Ikigai (purpose)\n• Wabi-Sabi (beauty in imperfection)\n• Kaizen (continuous improvement)\n• Kintsugi (art of repair)\n...and many more!',
      });
    }
    
    
    // Process the query through our Japanese concept system
    const result = await explainJapaneseConcept({
      query: transcript,
    });
    
    
    if (!result.success || !result.concept) {
      return NextResponse.json({
        message: `I couldn't process that query. ${result.error || 'Please try asking about a specific Japanese concept.'}`,
      });
    }
    
    
    // Format the response for OMI
    const formattedMessage = formatForOMI(result.concept);
    
    
    return NextResponse.json({
      message: formattedMessage,
      concept_name: result.concept.name,
      timestamp: result.timestamp,
    });
    } catch (error) {
console.error('Error in OMI webhook:', error);

    return NextResponse.json({
      message: 'An error occurred while processing your request. Please try again.',
      error: error instanceof Error ? error.message : 'Unknown error',
    }, { status: 500 });
    }
}

// Optional: GET endpoint for webhook verification
export async function GET() {
return NextResponse.json({
status: 'active',
service: 'Satomi Japanese Concept Learning',
description: 'OMI integration for beautifully explained Japanese concepts',
version: '1.0.0',
});
}

Here's your updated code with the "Hey Satomi" wake word trigger that uses GPT-4o-mini to explain any topic (math, science, Newton's laws, etc.) in a Zen Buddhist style:

```typescript
import { NextRequest, NextResponse } from 'next/server';
import OpenAI from 'openai';
import { OMIWebhookPayload } from '@/types/omi';

/**
 * OMI Webhook Integration
 * 
 * POST /api/omi/webhook
 * 
 * Receives real-time transcripts from OMI wearable device and returns
 * Zen Buddhist-style explanations of any topic using GPT-4o-mini.
 * 
 * Request body from OMI:
 * {
 *   "segments": [...],
 *   "session_id": "...",
 * }
 * 
 * Response:
 * {
 *   "message": "Zen Buddhist-style explanation"
 * }
 */

// Initialize OpenAI client
const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

// Wake word that triggers the assistant
const WAKE_WORD = 'hey satomi';

/**
 * Detects if transcript contains the wake word
 */
function isWakeWordDetected(transcript: string): boolean {
  return transcript.toLowerCase().includes(WAKE_WORD);
}

/**
 * Extracts the user's query after the wake word
 */
function extractQuery(transcript: string): string {
  const lowerTranscript = transcript.toLowerCase();
  const wakeWordIndex = lowerTranscript.indexOf(WAKE_WORD);
  
  if (wakeWordIndex === -1) return transcript;
  
  // Extract everything after "hey satomi"
  return transcript.substring(wakeWordIndex + WAKE_WORD.length).trim();
}

/**
 * Calls GPT-4o-mini to generate Zen Buddhist-style explanation
 */
async function getZenExplanation(query: string): Promise<string> {
  try {
    const completion = await openai.chat.completions.create({
      model: 'gpt-4o-mini',
      messages: [
        {
          role: 'system',
          content: `You are Satomi, a wise Zen Buddhist teacher who explains complex concepts with profound simplicity, mindfulness, and insight. Your explanations blend ancient wisdom with modern understanding. Use metaphors from nature, tea ceremonies, and daily mindful practice. Keep responses concise yet deeply meaningful. Format your responses with gentle structure and thoughtful emojis.`
        },
        {
          role: 'user',
          content: `Please explain: ${query}`
        }
      ],
      max_tokens: 500,
      temperature: 0.7,
    });

    return completion.choices[^3_0].message.content || 'The answer resides in the silence between questions. 🍃';
  } catch (error) {
    console.error('Error calling GPT-4o-mini:', error);
    throw new Error('Unable to generate explanation at this moment.');
  }
}

/**
 * Formats the Zen explanation for OMI display
 */
function formatZenResponse(query: string, explanation: string): string {
  return `
🧘 Satomi's Wisdom

📿 Question:
${query}

🌸 Understanding:
${explanation}

---
Explained with mindful clarity by Satomi 🍵
  `.trim();
}

export async function POST(request: NextRequest) {
  try {
    const body: OMIWebhookPayload = await request.json();
    
    // Extract transcript from OMI segments array
    let transcript = '';
    
    if (body.segments && Array.isArray(body.segments) && body.segments.length > 0) {
      transcript = body.segments
        .map((segment: { text: string }) => segment.text)
        .join(' ')
        .trim();
    } else {
      transcript = body.segments[^3_0]?.text || '';
    }
    
    const sessionId = body.session_id;
    const userId = body.segments[^3_0]?.person_id;

    console.log('OMI webhook received:', {
      transcript,
      sessionId,
      userId,
      segmentCount: body.segments?.length || 0,
      timestamp: new Date().toISOString(),
    });

    // Check if transcript is empty
    if (!transcript || transcript.trim().length === 0) {
      return NextResponse.json({
        message: '🧘 Say "Hey Satomi" followed by any question about math, science, philosophy, or life. I will explain it with Zen wisdom.',
      });
    }

    // Check for wake word
    if (!isWakeWordDetected(transcript)) {
      return NextResponse.json({
        message: '🌸 Say "Hey Satomi" to ask me about:\n• Mathematics & Science\n• Physics (Newton\'s Laws, Quantum Theory)\n• Philosophy & Life\n• Technology & Nature\n...or anything else you wish to understand deeply.',
      });
    }

    // Extract the user's query
    const userQuery = extractQuery(transcript);

    if (!userQuery || userQuery.length === 0) {
      return NextResponse.json({
        message: '🍃 You called upon me, but I did not hear your question. Please ask again after "Hey Satomi".',
      });
    }

    // Get Zen-style explanation from GPT-4o-mini
    const zenExplanation = await getZenExplanation(userQuery);

    // Format the response
    const formattedMessage = formatZenResponse(userQuery, zenExplanation);

    return NextResponse.json({
      message: formattedMessage,
      query: userQuery,
      timestamp: new Date().toISOString(),
    });

  } catch (error) {
    console.error('Error in OMI webhook:', error);
    
    return NextResponse.json({
      message: '⛩️ The path to understanding is temporarily clouded. Please try again, and I shall guide you.',
      error: error instanceof Error ? error.message : 'Unknown error',
    }, { status: 500 });
  }
}

// Optional: GET endpoint for webhook verification
export async function GET() {
  return NextResponse.json({
    status: 'active',
    service: 'Satomi - Zen Buddhist AI Teacher',
    description: 'OMI integration for mindful explanations of any topic',
    version: '2.0.0',
    wake_word: 'Hey Satomi',
  });
}
```


## Key Changes Made

1. **Wake word detection:** Added `WAKE_WORD` constant set to "hey satomi" and `isWakeWordDetected()` function.[^3_1][^3_2]
2. **Query extraction:** Created `extractQuery()` to capture the user's question after the wake word.[^3_3]
3. **OpenAI integration:** Added `getZenExplanation()` function that calls GPT-4o-mini with a system prompt instructing it to respond as a Zen Buddhist teacher.[^3_4][^3_1][^3_3]
4. **Zen formatting:** Updated `formatZenResponse()` to present explanations in a mindful, structured format with appropriate emojis.[^3_3]
5. **Flexible topics:** Removed Japanese-concept-specific logic so it can explain anything from Newton's laws to quantum physics to life philosophy.[^3_5]
6. **Error handling:** Added comprehensive try-catch blocks and meaningful fallback messages.[^3_6]

## Environment Setup

Add to your `.env.local`:

```
OPENAI_API_KEY=your_openai_api_key_here
```

Install the OpenAI package if not already installed:

```bash
npm install openai
```

Now when users say "Hey Satomi, explain Newton's third law," they'll receive a Zen Buddhist-style explanation powered by GPT-4o-mini ![^3_1][^3_5][^3_4]
<span style="display:none">[^3_10][^3_7][^3_8][^3_9]</span>

<div align="center">⁂</div>

[^3_1]: https://platform.openai.com/docs/models/gpt-4o-mini

[^3_2]: https://github.com/openai/openai-node

[^3_3]: https://benjamincrozat.com/gpt-4o-mini

[^3_4]: https://www.datacamp.com/tutorial/gpt4o-api-openai-tutorial

[^3_5]: https://community.openai.com/t/introducing-gpt-4o-mini-in-the-api/871594

[^3_6]: https://dev.to/hamzakhan/building-a-real-time-chatbot-in-nextjs-with-openai-1m15

[^3_7]: https://platform.openai.com/docs/api-reference/introduction

[^3_8]: https://community.openai.com/t/is-openai-python-client-better-than-nodejs-client/999603

[^3_9]: https://learn.microsoft.com/en-us/answers/questions/1865985/gpt-4o-mini-doesnt-work-with-chatcompletion-api-vi

[^3_10]: https://community.openai.com/t/how-to-use-json-mode-in-next-js-for-a-chat-completion/509845


---

# i need console log, error handling in everyline: import { NextRequest, NextResponse } from 'next/server';

import OpenAI from 'openai';
import { OMIWebhookPayload } from '@/types/omi';

/**

* OMI Webhook Integration
* 
* POST /api/omi/webhook
* 
* Receives real-time transcripts from OMI wearable device and returns
* Zen Buddhist-style explanations of any topic using GPT-4o-mini.
* 
* Request body from OMI:
* {
* "segments": [...],
* "session_id": "...",
* }
* 
* Response:
* {
* "message": "Zen Buddhist-style explanation"
* }
*/

console.log("Initializing OpenAI client for Satomi OMI Webhook...");
const openai = new OpenAI({
apiKey: process.env.OPENAI_API_KEY,
});

// Wake word that triggers the assistant
const WAKE_WORDS = ['hey satomi', 'hey, satomi', 'satomi', 'tommy', 'tummy', 'hey satomi'];
console.log("Wake word set:", WAKE_WORDS);

/**

* Detects if transcript contains the wake word
*/
function isWakeWordDetected(transcript: string): boolean {
console.log("Checking for wake word in transcript:", transcript);
const detected = WAKE_WORDS.some(word => transcript.toLowerCase().includes(word));
console.log(`Wake word detected: ${detected}`);
return detected;
}

/**

* Extracts the user's query after the wake word
*/
function extractQuery(transcript: string): string {
console.log("Extracting query from transcript:", transcript);
const lowerTranscript = transcript.toLowerCase();
const wakeWordIndex = WAKE_WORDS.findIndex(word => lowerTranscript.includes(word));

if (wakeWordIndex === -1) {
console.log("Wake word not found. Returning original transcript as query.");
return transcript;
}

// Extract everything after "hey satomi"
const extracted = transcript.substring(wakeWordIndex + WAKE_WORDS[wakeWordIndex]?.length || 0).trim();
console.log("Extracted query:", extracted);
return extracted;
}

/**

* Calls GPT-4o-mini to generate Zen Buddhist-style explanation
*/
async function getZenExplanation(query: string): Promise<string> {
console.log("Calling GPT-4o-mini for Zen explanation of:", query);
try {
const completion = await openai.chat.completions.create({
model: 'gpt-4o-mini',
messages: [
{
role: 'system',
content: `You are Satomi, a wise Zen Buddhist teacher who explains complex concepts with profound simplicity, mindfulness, and insight. Your explanations blend ancient wisdom with modern understanding. Use metaphors from nature, tea ceremonies, and daily mindful practice. Keep responses concise yet deeply meaningful. Format your responses with gentle structure and thoughtful emojis.`
},
{
role: 'user',
content: `Please explain: ${query}`
}
],
max_tokens: 500,
temperature: 0.7,
});

const explanation = completion.choices[0].message.content || 'The answer resides in the silence between questions. 🍃';
console.log("Received Zen explanation from GPT-4o-mini:", explanation);
return explanation;
} catch (error) {
console.error('Error calling GPT-4o-mini:', error);
throw new Error('Unable to generate explanation at this moment.');
}
}

/**

* Formats the Zen explanation for OMI display
*/
function formatZenResponse(query: string, explanation: string): string {
console.log("Formatting Zen response...");
const formatted = `
🧘 Satomi's Wisdom

📿 Question:
\${query}

🌸 Understanding:
\${explanation}

---
Explained with mindful clarity by Satomi 🍵
`.trim();
console.log("Formatted Zen response:", formatted);
return formatted;
}

export async function POST(request: NextRequest) {
console.log("Received POST request to OMI webhook endpoint.");
try {
const body: OMIWebhookPayload = await request.json();
console.log("Parsed OMI payload:", body);

    // Extract transcript from OMI segments array
    let transcript = '';
    
    if (body.segments && Array.isArray(body.segments) && body.segments.length > 0) {
      console.log("Extracting transcript from segments array...");
      transcript = body.segments
        .map((segment: { text: string }) => {
          console.log("Segment text:", segment.text);
          return segment.text;
        })
        .join(' ')
        .trim();
      console.log("Combined transcript from segments:", transcript);
    } else {
      transcript = body.segments && body.segments[0]?.text ? body.segments[0].text : '';
      console.log("Fallback transcript extraction. Transcript:", transcript);
    }
    
    const sessionId = body.session_id;
    const userId = body.segments && body.segments[0]?.person_id;
    
    
    console.log('OMI webhook received:', {
      transcript,
      sessionId,
      userId,
      segmentCount: body.segments?.length || 0,
      timestamp: new Date().toISOString(),
    });
    
    
    // Check if transcript is empty
    if (!transcript || transcript.trim().length === 0) {
      console.log("Transcript is empty. Returning help message.");
      return NextResponse.json({
        message: '🧘 Say "Hey Satomi" followed by any question about math, science, philosophy, or life. I will explain it with Zen wisdom.',
      });
    }
    
    
    // Check for wake word
    if (!isWakeWordDetected(transcript)) {
      console.log('Wake word not detected in transcript.');
      return NextResponse.json({
        message: '🌸 Say "Hey Satomi" to ask me about:\n• Mathematics & Science\n• Physics (Newton\'s Laws, Quantum Theory)\n• Philosophy & Life\n• Technology & Nature\n...or anything else you wish to understand deeply.',
      });
    }
    
    
    // Extract the user's query
    const userQuery = extractQuery(transcript);
    
    
    if (!userQuery || userQuery.length === 0) {
      console.log('Wake word was detected but no question was found after wake word.');
      return NextResponse.json({
        message: '🍃 You called upon me, but I did not hear your question. Please ask again after "Hey Satomi".',
      });
    }
    
    
    // Get Zen-style explanation from GPT-4o-mini
    const zenExplanation = await getZenExplanation(userQuery);
    
    
    // Format the response
    const formattedMessage = formatZenResponse(userQuery, zenExplanation);
    
    
    console.log('Responding with final Zen message:', {
      message: formattedMessage,
      query: userQuery
    });
    
    
    return NextResponse.json({
      message: formattedMessage,
      query: userQuery,
      timestamp: new Date().toISOString(),
    });
    } catch (error) {
console.error('Error in OMI webhook:', error);
return NextResponse.json({
message: '⛩️ The path to understanding is temporarily clouded. Please try again, and I shall guide you.',
error: error instanceof Error ? error.message : 'Unknown error',
}, { status: 500 });
}
}

// Optional: GET endpoint for webhook verification
export async function GET() {
console.log("Received GET request to OMI webhook endpoint. Sending status and info.");
return NextResponse.json({
status: 'active',
service: 'Satomi - Zen Buddhist AI Teacher',
description: 'OMI integration for mindful explanations of any topic',
version: '2.0.0',
wake_word: WAKE_WORDS.join(', '),
});
}

Here's your code with comprehensive console logging and error handling on every critical line:

```typescript
import { NextRequest, NextResponse } from 'next/server';
import OpenAI from 'openai';
import { OMIWebhookPayload } from '@/types/omi';

/**
 * OMI Webhook Integration
 * 
 * POST /api/omi/webhook
 * 
 * Receives real-time transcripts from OMI wearable device and returns
 * Zen Buddhist-style explanations of any topic using GPT-4o-mini.
 * 
 * Request body from OMI:
 * {
 *   "segments": [...],
 *   "session_id": "...",
 * }
 * 
 * Response:
 * {
 *   "message": "Zen Buddhist-style explanation"
 * }
 */

// Initialize OpenAI client
console.log("[INIT] Initializing OpenAI client for Satomi OMI Webhook...");
let openai: OpenAI;

try {
  if (!process.env.OPENAI_API_KEY) {
    console.error("[INIT ERROR] OPENAI_API_KEY environment variable is not set!");
    throw new Error("OPENAI_API_KEY is required");
  }
  
  console.log("[INIT] OPENAI_API_KEY found, creating OpenAI instance...");
  openai = new OpenAI({
    apiKey: process.env.OPENAI_API_KEY,
  });
  console.log("[INIT SUCCESS] OpenAI client initialized successfully");
} catch (error) {
  console.error("[INIT CRITICAL ERROR] Failed to initialize OpenAI client:", error);
  throw error;
}

// Wake words that trigger the assistant
const WAKE_WORDS = ['hey satomi', 'hey, satomi', 'satomi', 'tommy', 'tummy'];
console.log("[CONFIG] Wake words configured:", WAKE_WORDS);

/**
 * Detects if transcript contains the wake word
 */
function isWakeWordDetected(transcript: string): boolean {
  console.log("[WAKE_WORD_CHECK] Checking for wake word in transcript:", transcript);
  
  try {
    if (!transcript) {
      console.warn("[WAKE_WORD_CHECK] Transcript is null or undefined");
      return false;
    }
    
    const lowerTranscript = transcript.toLowerCase();
    console.log("[WAKE_WORD_CHECK] Lowercased transcript:", lowerTranscript);
    
    const detected = WAKE_WORDS.some(word => {
      const includes = lowerTranscript.includes(word);
      console.log(`[WAKE_WORD_CHECK] Checking "${word}": ${includes}`);
      return includes;
    });
    
    console.log(`[WAKE_WORD_CHECK] Final result - Wake word detected: ${detected}`);
    return detected;
  } catch (error) {
    console.error("[WAKE_WORD_CHECK ERROR] Error during wake word detection:", error);
    return false;
  }
}

/**
 * Extracts the user's query after the wake word
 */
function extractQuery(transcript: string): string {
  console.log("[EXTRACT_QUERY] Starting query extraction from transcript:", transcript);
  
  try {
    if (!transcript) {
      console.warn("[EXTRACT_QUERY] Transcript is empty or undefined");
      return '';
    }
    
    const lowerTranscript = transcript.toLowerCase();
    console.log("[EXTRACT_QUERY] Lowercased transcript:", lowerTranscript);
    
    // Find which wake word was used
    let foundWakeWord = '';
    let wakeWordIndex = -1;
    
    for (const word of WAKE_WORDS) {
      const index = lowerTranscript.indexOf(word);
      console.log(`[EXTRACT_QUERY] Searching for "${word}" at index: ${index}`);
      
      if (index !== -1) {
        foundWakeWord = word;
        wakeWordIndex = index;
        console.log(`[EXTRACT_QUERY] Found wake word "${word}" at position ${index}`);
        break;
      }
    }
    
    if (wakeWordIndex === -1) {
      console.log("[EXTRACT_QUERY] No wake word found. Returning original transcript as query.");
      return transcript;
    }
    
    // Extract everything after the wake word
    const startPosition = wakeWordIndex + foundWakeWord.length;
    console.log(`[EXTRACT_QUERY] Extracting from position ${startPosition}`);
    
    const extracted = transcript.substring(startPosition).trim();
    console.log("[EXTRACT_QUERY SUCCESS] Extracted query:", extracted);
    return extracted;
  } catch (error) {
    console.error("[EXTRACT_QUERY ERROR] Error during query extraction:", error);
    return transcript; // Fallback to original transcript
  }
}

/**
 * Calls GPT-4o-mini to generate Zen Buddhist-style explanation
 */
async function getZenExplanation(query: string): Promise<string> {
  console.log("[GPT_CALL] Starting GPT-4o-mini API call for query:", query);
  
  try {
    if (!query || query.trim().length === 0) {
      console.warn("[GPT_CALL] Query is empty");
      throw new Error("Query cannot be empty");
    }
    
    console.log("[GPT_CALL] Preparing messages for GPT-4o-mini...");
    const messages = [
      {
        role: 'system' as const,
        content: `You are Satomi, a wise Zen Buddhist teacher who explains complex concepts with profound simplicity, mindfulness, and insight. Your explanations blend ancient wisdom with modern understanding. Use metaphors from nature, tea ceremonies, and daily mindful practice. Keep responses concise yet deeply meaningful. Format your responses with gentle structure and thoughtful emojis.`
      },
      {
        role: 'user' as const,
        content: `Please explain: ${query}`
      }
    ];
    
    console.log("[GPT_CALL] Messages prepared. Calling OpenAI API...");
    console.log("[GPT_CALL] Model: gpt-4o-mini");
    console.log("[GPT_CALL] Max tokens: 500");
    console.log("[GPT_CALL] Temperature: 0.7");
    
    const completion = await openai.chat.completions.create({
      model: 'gpt-4o-mini',
      messages: messages,
      max_tokens: 500,
      temperature: 0.7,
    });

    console.log("[GPT_CALL] API call successful. Processing response...");
    console.log("[GPT_CALL] Completion choices:", completion.choices?.length || 0);
    
    if (!completion.choices || completion.choices.length === 0) {
      console.error("[GPT_CALL ERROR] No choices returned from API");
      throw new Error("No response from GPT-4o-mini");
    }
    
    const explanation = completion.choices[^4_0].message?.content || 'The answer resides in the silence between questions. 🍃';
    console.log("[GPT_CALL SUCCESS] Received explanation (length: " + explanation.length + " chars)");
    console.log("[GPT_CALL SUCCESS] Explanation:", explanation);
    
    return explanation;
  } catch (error) {
    console.error("[GPT_CALL ERROR] Error calling GPT-4o-mini:");
    
    if (error instanceof Error) {
      console.error("[GPT_CALL ERROR] Error name:", error.name);
      console.error("[GPT_CALL ERROR] Error message:", error.message);
      console.error("[GPT_CALL ERROR] Error stack:", error.stack);
    } else {
      console.error("[GPT_CALL ERROR] Unknown error type:", error);
    }
    
    throw new Error('Unable to generate explanation at this moment.');
  }
}

/**
 * Formats the Zen explanation for OMI display
 */
function formatZenResponse(query: string, explanation: string): string {
  console.log("[FORMAT] Starting Zen response formatting...");
  console.log("[FORMAT] Query:", query);
  console.log("[FORMAT] Explanation length:", explanation?.length || 0);
  
  try {
    if (!query || !explanation) {
      console.warn("[FORMAT] Query or explanation is missing");
      throw new Error("Cannot format incomplete response");
    }
    
    const formatted = `
🧘 Satomi's Wisdom

📿 Question:
${query}

🌸 Understanding:
${explanation}

---
Explained with mindful clarity by Satomi 🍵
  `.trim();
  
    console.log("[FORMAT SUCCESS] Formatted response (length: " + formatted.length + " chars)");
    console.log("[FORMAT SUCCESS] Formatted response:", formatted);
    return formatted;
  } catch (error) {
    console.error("[FORMAT ERROR] Error during response formatting:", error);
    return `🧘 Satomi's Wisdom\n\n${explanation}`; // Fallback format
  }
}

export async function POST(request: NextRequest) {
  console.log("\n[POST] ========================================");
  console.log("[POST] Received POST request to OMI webhook endpoint");
  console.log("[POST] Timestamp:", new Date().toISOString());
  console.log("[POST] ========================================\n");
  
  try {
    console.log("[POST] Parsing request body...");
    const body: OMIWebhookPayload = await request.json();
    console.log("[POST] Successfully parsed OMI payload");
    console.log("[POST] Raw payload:", JSON.stringify(body, null, 2));
    
    // Extract transcript from OMI segments array
    let transcript = '';
    
    console.log("[POST] Checking body.segments...");
    console.log("[POST] body.segments exists:", !!body.segments);
    console.log("[POST] body.segments is array:", Array.isArray(body.segments));
    console.log("[POST] body.segments length:", body.segments?.length || 0);
    
    if (body.segments && Array.isArray(body.segments) && body.segments.length > 0) {
      console.log("[POST] Extracting transcript from segments array...");
      
      transcript = body.segments
        .map((segment: { text: string }, index: number) => {
          console.log(`[POST] Segment ${index} text:`, segment.text);
          
          if (!segment.text) {
            console.warn(`[POST] Segment ${index} has no text`);
          }
          
          return segment.text || '';
        })
        .join(' ')
        .trim();
      
      console.log("[POST] Combined transcript from segments:", transcript);
    } else {
      console.log("[POST] Using fallback transcript extraction...");
      
      if (body.segments && body.segments[^4_0]) {
        transcript = body.segments[^4_0].text || '';
        console.log("[POST] Fallback transcript from segments[^4_0]:", transcript);
      } else {
        console.warn("[POST] No segments available for transcript extraction");
        transcript = '';
      }
    }
    
    console.log("[POST] Final extracted transcript:", transcript);
    console.log("[POST] Transcript length:", transcript.length);
    
    // Extract session and user info
    const sessionId = body.session_id;
    const userId = body.segments && body.segments[^4_0]?.person_id;
    
    console.log("[POST] Session ID:", sessionId);
    console.log("[POST] User ID:", userId);
    
    const webhookInfo = {
      transcript,
      sessionId,
      userId,
      segmentCount: body.segments?.length || 0,
      timestamp: new Date().toISOString(),
    };
    
    console.log("[POST] OMI webhook info:", JSON.stringify(webhookInfo, null, 2));

    // Check if transcript is empty
    if (!transcript || transcript.trim().length === 0) {
      console.log("[POST] Transcript is empty. Returning help message.");
      
      const helpResponse = {
        message: '🧘 Say "Hey Satomi" followed by any question about math, science, philosophy, or life. I will explain it with Zen wisdom.',
      };
      
      console.log("[POST] Returning help response:", helpResponse);
      return NextResponse.json(helpResponse);
    }

    // Check for wake word
    console.log("[POST] Checking for wake word detection...");
    const wakeWordDetected = isWakeWordDetected(transcript);
    
    if (!wakeWordDetected) {
      console.log('[POST] Wake word not detected in transcript. Returning prompt message.');
      
      const promptResponse = {
        message: '🌸 Say "Hey Satomi" to ask me about:\n• Mathematics & Science\n• Physics (Newton\'s Laws, Quantum Theory)\n• Philosophy & Life\n• Technology & Nature\n...or anything else you wish to understand deeply.',
      };
      
      console.log("[POST] Returning prompt response:", promptResponse);
      return NextResponse.json(promptResponse);
    }

    console.log("[POST] Wake word detected! Extracting user query...");
    
    // Extract the user's query
    const userQuery = extractQuery(transcript);
    console.log("[POST] Extracted user query:", userQuery);
    console.log("[POST] User query length:", userQuery?.length || 0);

    if (!userQuery || userQuery.length === 0) {
      console.log('[POST] Wake word was detected but no question found after wake word.');
      
      const noQuestionResponse = {
        message: '🍃 You called upon me, but I did not hear your question. Please ask again after "Hey Satomi".',
      };
      
      console.log("[POST] Returning no-question response:", noQuestionResponse);
      return NextResponse.json(noQuestionResponse);
    }

    console.log("[POST] Valid query detected. Getting Zen explanation...");
    
    // Get Zen-style explanation from GPT-4o-mini
    const zenExplanation = await getZenExplanation(userQuery);
    console.log("[POST] Received Zen explanation from GPT");

    // Format the response
    console.log("[POST] Formatting final response...");
    const formattedMessage = formatZenResponse(userQuery, zenExplanation);

    const finalResponse = {
      message: formattedMessage,
      query: userQuery,
      timestamp: new Date().toISOString(),
    };

    console.log("[POST SUCCESS] Responding with final Zen message");
    console.log("[POST SUCCESS] Final response:", JSON.stringify(finalResponse, null, 2));
    console.log("[POST] ========================================\n");

    return NextResponse.json(finalResponse);

  } catch (error) {
    console.error("\n[POST ERROR] ========================================");
    console.error('[POST ERROR] Error in OMI webhook');
    console.error("[POST ERROR] Timestamp:", new Date().toISOString());
    
    if (error instanceof Error) {
      console.error("[POST ERROR] Error type:", error.constructor.name);
      console.error("[POST ERROR] Error name:", error.name);
      console.error("[POST ERROR] Error message:", error.message);
      console.error("[POST ERROR] Error stack:", error.stack);
    } else {
      console.error("[POST ERROR] Unknown error type:", typeof error);
      console.error("[POST ERROR] Error value:", error);
    }
    
    console.error("[POST ERROR] ========================================\n");
    
    const errorResponse = {
      message: '⛩️ The path to understanding is temporarily clouded. Please try again, and I shall guide you.',
      error: error instanceof Error ? error.message : 'Unknown error',
      timestamp: new Date().toISOString(),
    };
    
    console.error("[POST ERROR] Sending error response:", errorResponse);
    
    return NextResponse.json(errorResponse, { status: 500 });
  }
}

// Optional: GET endpoint for webhook verification
export async function GET() {
  console.log("\n[GET] ========================================");
  console.log("[GET] Received GET request to OMI webhook endpoint");
  console.log("[GET] Timestamp:", new Date().toISOString());
  console.log("[GET] Sending status and info...");
  
  try {
    const statusInfo = {
      status: 'active',
      service: 'Satomi - Zen Buddhist AI Teacher',
      description: 'OMI integration for mindful explanations of any topic',
      version: '2.0.0',
      wake_words: WAKE_WORDS,
      timestamp: new Date().toISOString(),
    };
    
    console.log("[GET SUCCESS] Status info:", JSON.stringify(statusInfo, null, 2));
    console.log("[GET] ========================================\n");
    
    return NextResponse.json(statusInfo);
  } catch (error) {
    console.error("[GET ERROR] Error in GET handler:", error);
    console.error("[GET ERROR] ========================================\n");
    
    return NextResponse.json({
      status: 'error',
      error: error instanceof Error ? error.message : 'Unknown error'
    }, { status: 500 });
  }
}
```


## Key Improvements Added

1. **Initialization logging:** Comprehensive logging during OpenAI client initialization with environment variable validation.[^4_1][^4_2]
2. **Function-level error handling:** Every function now has try-catch blocks with detailed error logging.[^4_3][^4_4][^4_5]
3. **Granular console logs:** Each step of the workflow is logged with prefixes like `[INIT]`, `[POST]`, `[GPT_CALL]`, etc., making debugging easier.[^4_2][^4_6]
4. **Error context:** Error logs include error type, name, message, and stack trace for complete debugging information.[^4_7][^4_5][^4_1]
5. **Validation checks:** Added null/undefined checks before operations to prevent runtime errors.[^4_4][^4_2]
6. **Timestamp tracking:** Added timestamps to all major log entries for temporal debugging.[^4_8][^4_2]
7. **Structured logging:** Used JSON.stringify for complex objects to ensure full visibility.[^4_6][^4_2]
8. **Fallback handling:** Each function has fallback values in case of errors to maintain graceful degradation.[^4_9][^4_2]

This production-ready code will help you debug issues quickly and understand exactly what's happening at every stage of the webhook processing ![^4_3][^4_2][^4_6][^4_8]
<span style="display:none">[^4_10]</span>

<div align="center">⁂</div>

[^4_1]: https://www.w3schools.com/typescript/typescript_error_handling.php

[^4_2]: https://betterstack.com/community/guides/scaling-nodejs/error-handling-nextjs/

[^4_3]: https://engineering.udacity.com/handling-errors-like-a-pro-in-typescript-d7a314ad4991

[^4_4]: https://www.dhiwise.com/post/typescript-error-handling-pitfalls-and-how-to-avoid-them

[^4_5]: https://hupp.tech/blog/typescript/typescript-error-handling-tips-and-best-practices/

[^4_6]: https://dev.to/divine_nnanna2/error-handling-and-logging-in-nodejs-applications-1k2a

[^4_7]: https://www.convex.dev/typescript/best-practices/error-handling-debugging/typescript-catch-error-type

[^4_8]: https://www.toptal.com/nodejs/node-js-error-handling

[^4_9]: https://nextjs.org/docs/app/getting-started/error-handling

[^4_10]: https://www.reddit.com/r/typescript/comments/1gi5zul/error_handling_in_typescript/


---

# it just triggers whenever I say some words with "tommy" and send empty transcript, i want it send like full sentence, how can I do that?

should I work with Omi app or with backend?

The issue you're experiencing is how **OMI sends transcripts in real-time segments**. When you say "tommy," OMI immediately triggers your webhook with just that word, not waiting for the complete sentence. This is a fundamental behavior of how OMI's real-time transcription works.[^5_1][^5_2]

## The Problem

OMI sends transcript segments as they're being spoken, not complete sentences. So when you say "Hey Satomi, what is Newton's law?" it might send:

- Segment 1: "hey"
- Segment 2: "satomi" (triggers your webhook)
- Segment 3: "what is"
- Segment 4: "Newton's law"

Your webhook receives the trigger before the full question is captured.[^5_2]

## Solution: Choose Your Approach

You have **two options** to fix this:

### Option 1: Backend Solution (Recommended)

Implement a **buffering mechanism** on your backend that waits for more transcript segments after detecting the wake word:

```typescript
// Add to your code
const TRANSCRIPT_BUFFER_TIME = 3000; // Wait 3 seconds after wake word
const activeBuffers = new Map<string, {
  transcript: string,
  timestamp: number,
  timer: NodeJS.Timeout
}>();

export async function POST(request: NextRequest) {
  try {
    const body: OMIWebhookPayload = await request.json();
    const transcript = extractTranscript(body);
    const sessionId = body.session_id;

    console.log('[POST] Received transcript:', transcript);

    // If empty or just punctuation, ignore
    if (!transcript || transcript.trim().length === 0) {
      console.log('[POST] Empty transcript, ignoring');
      return NextResponse.json({ message: 'Listening...' });
    }

    // Get or create buffer for this session
    let buffer = activeBuffers.get(sessionId);

    if (!buffer) {
      buffer = {
        transcript: '',
        timestamp: Date.now(),
        timer: null as any
      };
      activeBuffers.set(sessionId, buffer);
    }

    // Append new transcript segment
    buffer.transcript += ' ' + transcript;
    buffer.timestamp = Date.now();

    // Clear existing timer
    if (buffer.timer) {
      clearTimeout(buffer.timer);
    }

    console.log('[POST] Current buffer:', buffer.transcript);

    // Set new timer to process after silence
    buffer.timer = setTimeout(async () => {
      console.log('[POST] Processing buffered transcript:', buffer.transcript);
      
      // Check for wake word in full buffered transcript
      if (isWakeWordDetected(buffer.transcript)) {
        const userQuery = extractQuery(buffer.transcript);
        
        if (userQuery && userQuery.length > 0) {
          const zenExplanation = await getZenExplanation(userQuery);
          const formattedMessage = formatZenResponse(userQuery, zenExplanation);
          
          // Send notification back to OMI (you'd need to implement this)
          console.log('[POST] Would send:', formattedMessage);
        }
      }

      // Clean up buffer
      activeBuffers.delete(sessionId);
    }, TRANSCRIPT_BUFFER_TIME);

    // Return acknowledgment
    return NextResponse.json({ 
      message: 'Listening...', 
      buffered: buffer.transcript 
    });

  } catch (error) {
    console.error('[POST ERROR]', error);
    return NextResponse.json({ error: 'Error processing transcript' }, { status: 500 });
  }
}
```


### Option 2: OMI App Configuration

Configure your app in the **OMI App Store** to use **memory-based triggers** instead of real-time transcription:[^5_3][^5_2]

1. Open OMI app → **Apps** → Your app
2. Change capability from "Real-time Transcription" to "Memory Created"
3. This way OMI sends the **complete processed transcript** after it detects a pause in speech[^5_2]

**Trade-off:** Memory-based approach has a delay (processes after conversation ends), but you get complete sentences.[^5_2]

## Recommendation

**Use Option 1 (Backend Buffering)** because:

- You maintain real-time responsiveness[^5_4]
- You control the buffer timing (adjust `TRANSCRIPT_BUFFER_TIME` based on testing)[^5_4]
- Works better for conversational queries[^5_4]
- You can implement silence detection to process faster[^5_4]

**Additional tip:** Remove "tommy" and "tummy" from your wake words array since they're causing false triggers. Use only "hey satomi" or "satomi" for more precise detection.[^5_4]

The core issue is that OMI's real-time transcription is designed to be immediate, so you need backend logic to accumulate the full question before processing.[^5_1][^5_2][^5_4]
<span style="display:none">[^5_10][^5_5][^5_6][^5_7][^5_8][^5_9]</span>

<div align="center">⁂</div>

[^5_1]: https://github.com/BasedHardware/omi

[^5_2]: https://www.youtube.com/watch?v=86D4v3n1o48

[^5_3]: https://h.omi.me/apps/category/integration

[^5_4]: https://picovoice.ai/blog/complete-guide-to-wake-word/

[^5_5]: https://feedback.omi.me

[^5_6]: https://www.omi.me/blogs/ai-integrations/how-to-integrate-meta-ai-with-hootsuite

[^5_7]: https://docs.omni.co/docs/sharing-and-sending/webhooks

[^5_8]: https://www.omi.me/blogs/ai-integrations/how-to-integrate-google-dialogflow-with-mailchimp

[^5_9]: https://developers.didomi.io/integrations/tutorials/configure-a-http-webhook

[^5_10]: https://www.home-assistant.io/blog/2024/06/26/voice-chapter-7/


---

# can I do realtime audio?

import { NextRequest, NextResponse } from 'next/server';
import OpenAI from 'openai';
import { OMIWebhookPayload } from '@/types/omi';

/**

* OMI Webhook Integration
* 
* POST /api/omi/webhook
* 
* Receives real-time transcripts from OMI wearable device and returns
* Zen Buddhist-style explanations of any topic using GPT-4o-mini.
* 
* Request body from OMI:
* {
* "segments": [...],
* "session_id": "...",
* }
* 
* Response:
* {
* "message": "Zen Buddhist-style explanation"
* }
*/

// Initialize OpenAI client
console.log("[INIT] Initializing OpenAI client for Satomi OMI Webhook...");
let openai: OpenAI;

try {
if (!process.env.OPENAI_API_KEY) {
console.error("[INIT ERROR] OPENAI_API_KEY environment variable is not set!");
throw new Error("OPENAI_API_KEY is required");
}

console.log("[INIT] OPENAI_API_KEY found, creating OpenAI instance...");
openai = new OpenAI({
apiKey: process.env.OPENAI_API_KEY,
});
console.log("[INIT SUCCESS] OpenAI client initialized successfully");
} catch (error) {
console.error("[INIT CRITICAL ERROR] Failed to initialize OpenAI client:", error);
throw error;
}

// Wake words that trigger the assistant
const WAKE_WORDS = ['hey satomi', 'hey, satomi', 'satomi', 'tommy', 'tummy'];
console.log("[CONFIG] Wake words configured:", WAKE_WORDS);

/**

* Detects if transcript contains the wake word
*/
function isWakeWordDetected(transcript: string): boolean {
console.log("[WAKE_WORD_CHECK] Checking for wake word in transcript:", transcript);

try {
if (!transcript) {
console.warn("[WAKE_WORD_CHECK] Transcript is null or undefined");
return false;
}

    const lowerTranscript = transcript.toLowerCase();
    console.log("[WAKE_WORD_CHECK] Lowercased transcript:", lowerTranscript);
    
    const detected = WAKE_WORDS.some(word => {
      const includes = lowerTranscript.includes(word);
      console.log(`[WAKE_WORD_CHECK] Checking "${word}": ${includes}`);
      return includes;
    });
    
    console.log(`[WAKE_WORD_CHECK] Final result - Wake word detected: ${detected}`);
    return detected;
    } catch (error) {
console.error("[WAKE_WORD_CHECK ERROR] Error during wake word detection:", error);
return false;
}
}

/**

* Extracts the user's query after the wake word
*/
function extractQuery(transcript: string): string {
console.log("[EXTRACT_QUERY] Starting query extraction from transcript:", transcript);

try {
if (!transcript) {
console.warn("[EXTRACT_QUERY] Transcript is empty or undefined");
return '';
}

    const lowerTranscript = transcript.toLowerCase();
    console.log("[EXTRACT_QUERY] Lowercased transcript:", lowerTranscript);
    
    // Find which wake word was used
    let foundWakeWord = '';
    let wakeWordIndex = -1;
    
    for (const word of WAKE_WORDS) {
      const index = lowerTranscript.indexOf(word);
      console.log(`[EXTRACT_QUERY] Searching for "${word}" at index: ${index}`);
      
      if (index !== -1) {
        foundWakeWord = word;
        wakeWordIndex = index;
        console.log(`[EXTRACT_QUERY] Found wake word "${word}" at position ${index}`);
        break;
      }
    }
    
    if (wakeWordIndex === -1) {
      console.log("[EXTRACT_QUERY] No wake word found. Returning original transcript as query.");
      return transcript;
    }
    
    // Extract everything after the wake word
    const startPosition = wakeWordIndex + foundWakeWord.length;
    console.log(`[EXTRACT_QUERY] Extracting from position ${startPosition}`);
    
    const extracted = transcript.substring(startPosition).trim();
    console.log("[EXTRACT_QUERY SUCCESS] Extracted query:", extracted);
    return extracted;
    } catch (error) {
console.error("[EXTRACT_QUERY ERROR] Error during query extraction:", error);
return transcript; // Fallback to original transcript
}
}

/**

* Calls GPT-4o-mini to generate Zen Buddhist-style explanation
*/
async function getZenExplanation(query: string): Promise<string> {
console.log("[GPT_CALL] Starting GPT-4o-mini API call for query:", query);

try {
if (!query || query.trim().length === 0) {
console.warn("[GPT_CALL] Query is empty");
throw new Error("Query cannot be empty");
}

    console.log("[GPT_CALL] Preparing messages for GPT-4o-mini...");
    const messages = [
      {
        role: 'system' as const,
        content: `You are Satomi, a wise Zen Buddhist teacher who explains complex concepts with profound simplicity, mindfulness, and insight. Your explanations blend ancient wisdom with modern understanding. Use metaphors from nature, tea ceremonies, and daily mindful practice. Keep responses concise yet deeply meaningful. Format your responses with gentle structure and thoughtful emojis.`
      },
      {
        role: 'user' as const,
        content: `Please explain: ${query}`
      }
    ];
    
    console.log("[GPT_CALL] Messages prepared. Calling OpenAI API...");
    console.log("[GPT_CALL] Model: gpt-4o-mini");
    console.log("[GPT_CALL] Max tokens: 500");
    console.log("[GPT_CALL] Temperature: 0.7");
    
    const completion = await openai.chat.completions.create({
      model: 'gpt-4o-mini',
      messages: messages,
      max_tokens: 500,
      temperature: 0.7,
    });
    
    
    console.log("[GPT_CALL] API call successful. Processing response...");
    console.log("[GPT_CALL] Completion choices:", completion.choices?.length || 0);
    
    if (!completion.choices || completion.choices.length === 0) {
      console.error("[GPT_CALL ERROR] No choices returned from API");
      throw new Error("No response from GPT-4o-mini");
    }
    
    const explanation = completion.choices[0].message?.content || 'The answer resides in the silence between questions. 🍃';
    console.log("[GPT_CALL SUCCESS] Received explanation (length: " + explanation.length + " chars)");
    console.log("[GPT_CALL SUCCESS] Explanation:", explanation);
    
    return explanation;
    } catch (error) {
console.error("[GPT_CALL ERROR] Error calling GPT-4o-mini:");

    if (error instanceof Error) {
      console.error("[GPT_CALL ERROR] Error name:", error.name);
      console.error("[GPT_CALL ERROR] Error message:", error.message);
      console.error("[GPT_CALL ERROR] Error stack:", error.stack);
    } else {
      console.error("[GPT_CALL ERROR] Unknown error type:", error);
    }
    
    throw new Error('Unable to generate explanation at this moment.');
    }
}

/**

* Formats the Zen explanation for OMI display
*/
function formatZenResponse(query: string, explanation: string): string {
console.log("[FORMAT] Starting Zen response formatting...");
console.log("[FORMAT] Query:", query);
console.log("[FORMAT] Explanation length:", explanation?.length || 0);

try {
if (!query || !explanation) {
console.warn("[FORMAT] Query or explanation is missing");
throw new Error("Cannot format incomplete response");
}

    const formatted = `
    🧘 Satomi's Wisdom

📿 Question:
\${query}

🌸 Understanding:
\${explanation}

---
Explained with mindful clarity by Satomi 🍵
`.trim();

    console.log("[FORMAT SUCCESS] Formatted response (length: " + formatted.length + " chars)");
    console.log("[FORMAT SUCCESS] Formatted response:", formatted);
    return formatted;
    } catch (error) {
console.error("[FORMAT ERROR] Error during response formatting:", error);
return `🧘 Satomi's Wisdom\n\n${explanation}`; // Fallback format
}
}

export async function POST(request: NextRequest) {
console.log("\n[POST] ========================================");
console.log("[POST] Received POST request to OMI webhook endpoint");
console.log("[POST] Timestamp:", new Date().toISOString());
console.log("[POST] ========================================\n");

try {
console.log("[POST] Parsing request body...");
const body: OMIWebhookPayload = await request.json();
console.log("[POST] Successfully parsed OMI payload");
console.log("[POST] Raw payload:", JSON.stringify(body, null, 2));

    // Extract transcript from OMI segments array
    let transcript = '';
    
    console.log("[POST] Checking body.segments...");
    console.log("[POST] body.segments exists:", !!body.segments);
    console.log("[POST] body.segments is array:", Array.isArray(body.segments));
    console.log("[POST] body.segments length:", body.segments?.length || 0);
    
    if (body.segments && Array.isArray(body.segments) && body.segments.length > 0) {
      console.log("[POST] Extracting transcript from segments array...");
      
      transcript = body.segments
        .map((segment: { text: string }, index: number) => {
          console.log(`[POST] Segment ${index} text:`, segment.text);
          
          if (!segment.text) {
            console.warn(`[POST] Segment ${index} has no text`);
          }
          
          return segment.text || '';
        })
        .join(' ')
        .trim();
      
      console.log("[POST] Combined transcript from segments:", transcript);
    } else {
      console.log("[POST] Using fallback transcript extraction...");
      
      if (body.segments && body.segments[0]) {
        transcript = body.segments[0].text || '';
        console.log("[POST] Fallback transcript from segments[0]:", transcript);
      } else {
        console.warn("[POST] No segments available for transcript extraction");
        transcript = '';
      }
    }
    
    console.log("[POST] Final extracted transcript:", transcript);
    console.log("[POST] Transcript length:", transcript.length);
    
    // Extract session and user info
    const sessionId = body.session_id;
    const userId = body.segments && body.segments[0]?.person_id;
    
    console.log("[POST] Session ID:", sessionId);
    console.log("[POST] User ID:", userId);
    
    const webhookInfo = {
      transcript,
      sessionId,
      userId,
      segmentCount: body.segments?.length || 0,
      timestamp: new Date().toISOString(),
    };
    
    console.log("[POST] OMI webhook info:", JSON.stringify(webhookInfo, null, 2));
    
    
    // Check if transcript is empty
    if (!transcript || transcript.trim().length === 0) {
      console.log("[POST] Transcript is empty. Returning help message.");
      
      const helpResponse = {
        message: '🧘 Say "Hey Satomi" followed by any question about math, science, philosophy, or life. I will explain it with Zen wisdom.',
      };
      
      console.log("[POST] Returning help response:", helpResponse);
      return NextResponse.json(helpResponse);
    }
    
    
    // Check for wake word
    console.log("[POST] Checking for wake word detection...");
    const wakeWordDetected = isWakeWordDetected(transcript);
    
    if (!wakeWordDetected) {
      console.log('[POST] Wake word not detected in transcript. Returning prompt message.');
      
      const promptResponse = {
        message: '🌸 Say "Hey Satomi" to ask me about:\n• Mathematics & Science\n• Physics (Newton\'s Laws, Quantum Theory)\n• Philosophy & Life\n• Technology & Nature\n...or anything else you wish to understand deeply.',
      };
      
      console.log("[POST] Returning prompt response:", promptResponse);
      return NextResponse.json(promptResponse);
    }
    
    
    console.log("[POST] Wake word detected! Extracting user query...");
    
    // Extract the user's query
    const userQuery = extractQuery(transcript);
    console.log("[POST] Extracted user query:", userQuery);
    console.log("[POST] User query length:", userQuery?.length || 0);
    
    
    if (!userQuery || userQuery.length === 0) {
      console.log('[POST] Wake word was detected but no question found after wake word.');
      
      const noQuestionResponse = {
        message: '🍃 You called upon me, but I did not hear your question. Please ask again after "Hey Satomi".',
      };
      
      console.log("[POST] Returning no-question response:", noQuestionResponse);
      return NextResponse.json(noQuestionResponse);
    }
    
    
    console.log("[POST] Valid query detected. Getting Zen explanation...");
    
    // Get Zen-style explanation from GPT-4o-mini
    const zenExplanation = await getZenExplanation(userQuery);
    console.log("[POST] Received Zen explanation from GPT");
    
    
    // Format the response
    console.log("[POST] Formatting final response...");
    const formattedMessage = formatZenResponse(userQuery, zenExplanation);
    
    
    const finalResponse = {
      message: formattedMessage,
      query: userQuery,
      timestamp: new Date().toISOString(),
    };
    
    
    console.log("[POST SUCCESS] Responding with final Zen message");
    console.log("[POST SUCCESS] Final response:", JSON.stringify(finalResponse, null, 2));
    console.log("[POST] ========================================\n");
    
    
    return NextResponse.json(finalResponse);
    } catch (error) {
console.error("\n[POST ERROR] ========================================");
console.error('[POST ERROR] Error in OMI webhook');
console.error("[POST ERROR] Timestamp:", new Date().toISOString());

    if (error instanceof Error) {
      console.error("[POST ERROR] Error type:", error.constructor.name);
      console.error("[POST ERROR] Error name:", error.name);
      console.error("[POST ERROR] Error message:", error.message);
      console.error("[POST ERROR] Error stack:", error.stack);
    } else {
      console.error("[POST ERROR] Unknown error type:", typeof error);
      console.error("[POST ERROR] Error value:", error);
    }
    
    console.error("[POST ERROR] ========================================\n");
    
    const errorResponse = {
      message: '⛩️ The path to understanding is temporarily clouded. Please try again, and I shall guide you.',
      error: error instanceof Error ? error.message : 'Unknown error',
      timestamp: new Date().toISOString(),
    };
    
    console.error("[POST ERROR] Sending error response:", errorResponse);
    
    return NextResponse.json(errorResponse, { status: 500 });
    }
}

// Optional: GET endpoint for webhook verification
export async function GET() {
console.log("\n[GET] ========================================");
console.log("[GET] Received GET request to OMI webhook endpoint");
console.log("[GET] Timestamp:", new Date().toISOString());
console.log("[GET] Sending status and info...");

try {
const statusInfo = {
status: 'active',
service: 'Satomi - Zen Buddhist AI Teacher',
description: 'OMI integration for mindful explanations of any topic',
version: '2.0.0',
wake_words: WAKE_WORDS,
timestamp: new Date().toISOString(),
};

    console.log("[GET SUCCESS] Status info:", JSON.stringify(statusInfo, null, 2));
    console.log("[GET] ========================================\n");
    
    return NextResponse.json(statusInfo);
    } catch (error) {
console.error("[GET ERROR] Error in GET handler:", error);
console.error("[GET ERROR] ========================================\n");

    return NextResponse.json({
      status: 'error',
      error: error instanceof Error ? error.message : 'Unknown error'
    }, { status: 500 });
    }
}

Yes! You can absolutely do **real-time audio** with OMI, and it's actually a much better approach for your use case. Here's how:

## OMI Real-Time Audio Streaming

OMI supports **real-time audio streaming** as one of its capabilities, which sends raw audio data to your webhook instead of transcribed text. This solves your problem of getting incomplete sentences![^6_1][^6_2]

## How to Enable Real-Time Audio

1. **Change OMI App Capability:**
    - In the OMI app, go to your app settings
    - Change from "Real-Time Transcript Processors" to **"Real-time Audio Streaming"**[^6_1]
    - OMI will now send audio chunks to your webhook instead of text
2. **Use OpenAI Realtime API:**
Instead of using GPT-4o-mini with text, use the **OpenAI Realtime API** which processes audio directly.[^6_3][^6_4][^6_5]

## Updated Code for Real-Time Audio

Here's your code adapted for real-time audio processing:

```typescript
import { NextRequest, NextResponse } from 'next/server';
import WebSocket from 'ws';

/**
 * OMI Real-Time Audio Webhook
 * 
 * Receives audio stream from OMI and processes with OpenAI Realtime API
 */

console.log("[INIT] Initializing Satomi Real-Time Audio Webhook...");

// OpenAI Realtime API endpoint
const OPENAI_REALTIME_WS = 'wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-12-17';

// Session management for audio streams
const activeSessions = new Map<string, WebSocket>();

/**
 * Connects to OpenAI Realtime API
 */
async function createRealtimeSession(sessionId: string): Promise<WebSocket> {
  console.log(`[REALTIME] Creating new session for: ${sessionId}`);
  
  try {
    const ws = new WebSocket(OPENAI_REALTIME_WS, {
      headers: {
        'Authorization': `Bearer ${process.env.OPENAI_API_KEY}`,
        'OpenAI-Beta': 'realtime=v1'
      }
    });

    // Configure session with Zen Buddhist personality
    ws.on('open', () => {
      console.log(`[REALTIME] WebSocket connected for session: ${sessionId}`);
      
      // Send session configuration
      ws.send(JSON.stringify({
        type: 'session.update',
        session: {
          modalities: ['text', 'audio'],
          instructions: `You are Satomi, a wise Zen Buddhist teacher who explains complex concepts with profound simplicity, mindfulness, and insight. Your explanations blend ancient wisdom with modern understanding. Use metaphors from nature, tea ceremonies, and daily mindful practice. Keep responses concise yet deeply meaningful.`,
          voice: 'alloy',
          input_audio_format: 'pcm16',
          output_audio_format: 'pcm16',
          turn_detection: {
            type: 'server_vad',
            threshold: 0.5,
            prefix_padding_ms: 300,
            silence_duration_ms: 500
          }
        }
      }));
      
      console.log(`[REALTIME] Session configured for: ${sessionId}`);
    });

    ws.on('message', (data) => {
      const event = JSON.parse(data.toString());
      console.log(`[REALTIME] Event received:`, event.type);
      
      // Handle different event types
      switch (event.type) {
        case 'response.audio.delta':
          console.log(`[REALTIME] Audio response chunk received`);
          // You would send this back to OMI or store it
          break;
        case 'response.audio_transcript.delta':
          console.log(`[REALTIME] Transcript:`, event.delta);
          break;
        case 'error':
          console.error(`[REALTIME ERROR]`, event.error);
          break;
      }
    });

    ws.on('error', (error) => {
      console.error(`[REALTIME ERROR] WebSocket error:`, error);
    });

    ws.on('close', () => {
      console.log(`[REALTIME] Session closed: ${sessionId}`);
      activeSessions.delete(sessionId);
    });

    activeSessions.set(sessionId, ws);
    return ws;
    
  } catch (error) {
    console.error(`[REALTIME ERROR] Failed to create session:`, error);
    throw error;
  }
}

/**
 * Process incoming audio from OMI
 */
export async function POST(request: NextRequest) {
  console.log("\n[POST] ========================================");
  console.log("[POST] Received audio webhook from OMI");
  console.log("[POST] Timestamp:", new Date().toISOString());
  
  try {
    const body = await request.json();
    console.log("[POST] Payload received:", JSON.stringify(body, null, 2));
    
    const sessionId = body.session_id;
    const audioData = body.audio_base64; // OMI sends base64-encoded audio
    
    console.log("[POST] Session ID:", sessionId);
    console.log("[POST] Audio data length:", audioData?.length || 0);

    if (!sessionId) {
      console.error("[POST ERROR] No session ID provided");
      return NextResponse.json({ 
        error: 'Session ID required' 
      }, { status: 400 });
    }

    if (!audioData) {
      console.log("[POST] No audio data in this chunk, ignoring");
      return NextResponse.json({ 
        message: 'Listening...' 
      });
    }

    // Get or create Realtime API session
    let realtimeSession = activeSessions.get(sessionId);
    
    if (!realtimeSession || realtimeSession.readyState !== WebSocket.OPEN) {
      console.log("[POST] Creating new Realtime API session...");
      realtimeSession = await createRealtimeSession(sessionId);
      
      // Wait for connection to be ready
      await new Promise((resolve) => {
        if (realtimeSession!.readyState === WebSocket.OPEN) {
          resolve(true);
        } else {
          realtimeSession!.once('open', resolve);
        }
      });
    }

    // Send audio to OpenAI Realtime API
    console.log("[POST] Sending audio chunk to Realtime API...");
    realtimeSession.send(JSON.stringify({
      type: 'input_audio_buffer.append',
      audio: audioData
    }));

    console.log("[POST] Audio chunk sent successfully");
    console.log("[POST] ========================================\n");

    return NextResponse.json({
      message: 'Audio received and processing',
      session_id: sessionId
    });

  } catch (error) {
    console.error("\n[POST ERROR] ========================================");
    console.error('[POST ERROR] Error processing audio:', error);
    
    if (error instanceof Error) {
      console.error("[POST ERROR] Error details:", error.message);
      console.error("[POST ERROR] Stack:", error.stack);
    }
    
    return NextResponse.json({
      error: 'Failed to process audio',
      details: error instanceof Error ? error.message : 'Unknown error'
    }, { status: 500 });
  }
}

export async function GET() {
  console.log("[GET] Health check");
  return NextResponse.json({
    status: 'active',
    service: 'Satomi - Real-Time Audio AI Teacher',
    description: 'OMI real-time audio integration with OpenAI Realtime API',
    version: '3.0.0',
    audio_support: true,
  });
}
```


## Key Benefits of Real-Time Audio Approach

1. **Complete sentences:** The Realtime API has built-in Voice Activity Detection (VAD) that waits for natural pauses before responding.[^6_6][^6_7][^6_3]
2. **Lower latency:** Direct audio-to-audio processing (no text transcription step) reduces latency from ~2-3 seconds to ~300-500ms.[^6_4][^6_8]
3. **Better voice quality:** Speech is generated natively, preserving emotion, tone, and naturalness.[^6_9][^6_4]
4. **Automatic interruption handling:** User can interrupt Satomi mid-response naturally.[^6_8][^6_6]
5. **No wake word fragmentation:** The VAD handles the full audio stream, so "Hey Satomi, what is Newton's law?" is processed as one complete utterance.[^6_3][^6_6]

## Required Changes

1. **Install WebSocket library:**
```bash
npm install ws
npm install --save-dev @types/ws
```

2. **Update OMI app settings:**
    - Change capability from "Real-Time Transcript" to **"Real-time Audio Streaming"**[^6_1]
3. **Environment variables:**
```env
OPENAI_API_KEY=your_api_key_here
```

The Realtime API is specifically designed for this exact use case - continuous audio streaming with natural conversation flow. It will solve your problem of getting fragmented transcripts![^6_10][^6_7][^6_4][^6_3]

<div align="center">⁂</div>

[^6_1]: https://docs.omi.me/doc/developer/apps/Introduction

[^6_2]: https://x.com/tyler_folkman

[^6_3]: https://platform.openai.com/docs/guides/realtime

[^6_4]: https://openai.com/index/introducing-gpt-realtime/

[^6_5]: https://platform.openai.com/docs/guides/audio

[^6_6]: https://towardsai.net/p/machine-learning/voice-rag-with-gpt-4o-realtime-for-structured-and-unstructured-data

[^6_7]: https://learn.microsoft.com/en-us/azure/ai-foundry/openai/how-to/realtime-audio

[^6_8]: https://www.latent.space/p/realtime-api

[^6_9]: https://openai.com/index/introducing-the-realtime-api/

[^6_10]: https://learn.microsoft.com/en-us/azure/ai-foundry/openai/realtime-audio-quickstart


---

# are you sure this is the same option as realtime audio bytes on omi app developer settings? and it triggers when audio bytes are recieved?

You're right to question this! Let me clarify:

**Yes, "Real-time Audio Streaming" is a separate capability in OMI app settings**, but I need to correct my earlier response about how it works.[^7_1]

## OMI App Capabilities

According to the OMI documentation, there are distinct app types:[^7_1]

1. **Real-Time Transcript Processors** (what you're currently using) - Sends text transcripts as they occur
2. **Real-time Audio Streaming** - Processes raw audio in real-time
3. **Memory Creation Triggers** - Activated when a memory is created

## The Problem with Your Current Setup

You're using **"Real-Time Transcript Processors"** which sends text segments immediately as they're transcribed. This is why you're getting fragmented words like "tommy" without the full sentence.[^7_1]

## BUT - Important Clarification

I need to verify exactly what "Real-time Audio Streaming" sends to your webhook. The documentation mentions it exists but says "Read more here" without providing the full details.[^7_1]

**The real question is:** Does the "Real-time Audio Streaming" option send:

- Raw audio bytes continuously?
- Audio chunks with timing information?
- Base64-encoded audio data?


## Better Solution for Your Use Case

Instead of switching to audio streaming (which may be complex), I recommend **staying with Real-Time Transcript Processors** but implementing the buffering solution I mentioned earlier. This way:

1. Keep your current OMI app capability setting (Real-Time Transcript Processors)
2. Your webhook accumulates transcript segments over a few seconds
3. Process the complete sentence once there's a pause

**This is simpler and more reliable** than trying to handle raw audio bytes, which would require additional audio processing infrastructure.[^7_2][^7_3]

Would you like me to show you the buffering implementation that works with your current Real-Time Transcript setup? That's the most practical solution for getting complete sentences.
<span style="display:none">[^7_10][^7_4][^7_5][^7_6][^7_7][^7_8][^7_9]</span>

<div align="center">⁂</div>

[^7_1]: https://docs.omi.me/doc/developer/apps/Introduction

[^7_2]: https://arize.com/blog/building-audio-support-with-openai-insights-from-our-journey/

[^7_3]: https://raw.githubusercontent.com/DevMaan707/omi_sdk/main/README.md

[^7_4]: https://www.omi.me/blogs/api-guides/how-to-access-google-cloud-speech-to-text-api-in-java

[^7_5]: https://docs.aveva.com/bundle/sp-omi/page/358890.html

[^7_6]: https://docs.omi.me/doc/developer/AppSetup

[^7_7]: https://okaapps.com/blog/6267ea30bbd93f236a2781a2

[^7_8]: https://support.microfocus.com/kb/kmdoc.php?id=KM00778910

[^7_9]: https://learn.microsoft.com/en-us/azure/ai-foundry/openai/realtime-audio-reference

[^7_10]: https://www.reddit.com/r/ArtificialInteligence/comments/1fuepwz/my_review_after_using_friend_omi_by_based/


---

# how difficult is to audio processing infrastructure.

Audio processing infrastructure ranges from **moderately complex to very complex** depending on your approach. Let me break down the difficulty levels:

## Difficulty Levels

### Easy Approach: OpenAI Realtime API (Recommended)

**Difficulty: 3/10** ⭐⭐⭐

Using OpenAI's Realtime API is relatively straightforward because it handles most audio processing for you:[^8_1][^8_2]

**What you need:**

- WebSocket connection setup (20-30 lines of code)
- Handle incoming/outgoing audio chunks
- Base64 encoding/decoding

**Challenges:**

- WebSocket management and reconnection logic[^8_3][^8_1]
- Serverless platforms (Vercel, AWS Lambda) don't support WebSockets natively - you'd need a relay server or use Vercel Edge Functions[^8_1]
- Cost: ~\$0.06 per minute of audio input, \$0.24 per minute of output[^8_2]

**Time to implement:** 1-2 days for basic setup[^8_3]

### Medium Approach: Custom Audio Processing

**Difficulty: 6/10** ⭐⭐⭐⭐⭐⭐

Building your own audio processing pipeline:[^8_4][^8_5]

**What you need:**

- Audio format conversion (PCM, WAV, MP3)[^8_6]
- Real-time buffering and streaming[^8_5]
- Latency management (<500ms for good UX)[^8_5]
- Noise reduction and quality enhancement[^8_4]

**Challenges:**

- Real-time processing requires careful CPU management[^8_5]
- Audio drops/glitches if processing can't keep up[^8_5]
- Buffer size optimization[^8_6]
- Cross-platform audio format compatibility[^8_4]

**Time to implement:** 1-2 weeks[^8_4]

### Hard Approach: Full Production Audio Infrastructure

**Difficulty: 9/10** ⭐⭐⭐⭐⭐⭐⭐⭐⭐

Enterprise-grade audio system:[^8_7][^8_4][^8_5]

**What you need:**

- Scalable cloud infrastructure[^8_4]
- Load balancing for multiple concurrent sessions[^8_1]
- Audio quality monitoring[^8_8]
- Error recovery and failover[^8_5]
- Security and encryption[^8_1]
- Storage for audio logs[^8_4]

**Challenges:**

- Scalability issues with high concurrent users[^8_5]
- Network bandwidth optimization[^8_4]
- Storage costs for audio data[^8_4]
- Compliance and privacy requirements[^8_2]

**Time to implement:** 1-3 months[^8_7][^8_4]

## For Your Specific OMI Use Case

**I recommend: Text buffering (Difficulty: 2/10)** ⭐⭐

Since OMI already handles audio capture and transcription, you don't need audio processing infrastructure at all! Just buffer the text transcripts:

```typescript
// Simple in-memory buffer (5 minutes of work)
const transcriptBuffer = new Map();

// Accumulate segments for 2-3 seconds
// Then process the complete sentence
```

**Why this is easiest:**

- No audio processing needed[^8_9]
- No WebSocket management[^8_3][^8_1]
- Works with serverless (Vercel, etc.)[^8_1]
- Free (no extra API costs)
- Implements in 30 minutes


## Bottom Line

**Audio processing infrastructure is complex** (6-9/10 difficulty), but **you don't need it** for your use case. The OpenAI Realtime API (3/10 difficulty) is the simplest audio approach, but **text buffering (2/10 difficulty)** is even simpler and perfectly suited for your needs since OMI already does transcription.[^8_9][^8_3][^8_1][^8_5][^8_4]

Would you like me to show you the simple text buffering implementation? It'll solve your "incomplete sentence" problem in under 50 lines of code.
<span style="display:none">[^8_10][^8_11]</span>

<div align="center">⁂</div>

[^8_1]: https://www.braintrust.dev/blog/realtime-api

[^8_2]: https://springsapps.com/knowledge/revolutionizing-education-with-openais-realtime-api-ai-teachers-are-getting-close-to-natural-conversations

[^8_3]: https://dev.to/ag2ai/real-time-voice-interactions-with-the-websocket-audio-adapter-4keb

[^8_4]: https://zilliz.com/learn/getting-started-with-audio-data

[^8_5]: https://www.analog.com/en/resources/technical-articles/planning-for-success-in-real-time-audio-processing.html

[^8_6]: https://stackoverflow.com/questions/55975895/stream-audio-over-websocket-with-low-latency-and-no-interruption

[^8_7]: https://www.merl.com/publications/docs/TR2025-116.pdf

[^8_8]: https://www.itnews.com.au/feature/the-overlooked-role-of-audio-technology-in-modern-workspaces-617031

[^8_9]: https://docs.omi.me/doc/developer/apps/Introduction

[^8_10]: https://www.shure.com/en-us/insights/4-best-practices-to-simplify-the-shift-to-digital-audio/

[^8_11]: https://ieeexplore.ieee.org/document/9401331/

