<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>
```
# This URL has no default content configured. <a href="https://webhook.site/#!/edit/aee1972e-9a6e-47d3-b9a8-aa6ed4929c04">Change response in Webhook.site</a>.
```

The URL you referenced at Webhook.site has no default content configured. This means that when accessing the webhook URL, no specific response content is set to be returned by default.

If you want to customize or add content for this webhook URL, you can do so by visiting the Webhook.site edit page linked here: https://webhook.site/\#!/edit/aee1972e-9a6e-47d3-b9a8-aa6ed4929c04

There, you can configure the default HTTP response, add scripting, or set transformations and workflows for incoming requests.

If you need help with how to configure this or what kind of response to set up, let me know!
<span style="display:none">[^1_1]</span>

<div align="center">⁂</div>

[^1_1]: https://webhook.site


---

# [https://docs.omi.me/doc/developer/apps/Introduction](https://docs.omi.me/doc/developer/apps/Introduction)

The document from the OMI developer site provides an introduction to creating and using OMI Apps, which are modular extensions enhancing the OMI app's core capabilities. Here's a summary of the key points:

## OMI Apps Overview

OMI Apps enable:

- Custom AI personalities and knowledge bases
- Extraction of specific info from conversations
- Task automation and third-party service integration
- Real-time conversation analysis and insights


## Main App Types

1. **Prompt-Based Apps**: Modify how OMI processes and responds to information, customizing AI behavior.
2. **Integration Apps**: Connect OMI to external systems, enabling real-time data processing and interaction.

### Examples of Integration Apps Include:

- Memory Creation Triggers: Automate updates to project management, social platforms, or knowledge graphs based on conversations.
- Real-Time Transcript Processors: Provide live conversation coaching, manage reminders, perform web searches, analyze emotions, and control smart devices from conversational cues.
- Integration Actions: Sync data, generate memories from external sources, import conversation data, schedule logging, and more.


## Getting Started:

- Use webhook.site to create webhooks and connect them to OMI.
- Choose the appropriate app type and follow the guidance to build and test.
- Submit your app via the OMI mobile app.

The page also links to code examples for practical uses such as mentorship, Zapier integration, GitHub, Twitter, Slack, and RingCentral integrations.

If you want, I can help you with steps or code examples to create a specific OMI app or integration. Let me know!
<span style="display:none">[^2_1]</span>

<div align="center">⁂</div>

[^2_1]: https://docs.omi.me/doc/developer/apps/Introduction


---

# i wanna build app, but i have no idea how to build

To build an OMI app from scratch, here’s a simple guide to get started even if you have no prior experience with OMI apps:

## Basic Steps to Build Your First OMI App

1. **Understand App Types**
Decide what kind of app you want:
    - Prompt-Based App: Customize how OMI responds
    - Integration App: Connect OMI to external services or automate tasks
2. **Create a Webhook URL**
Use a service like webhook.site to create a URL that OMI can send data to. This URL will receive conversation data or commands from OMI.
3. **Set Up Your Development Environment**
You can build the app logic in any language or platform you prefer (Node.js, Python, etc.). Your app will:
    - Receive POST requests from OMI via your webhook URL
    - Process the incoming data according to your app’s purpose
    - Optionally send back responses or trigger actions elsewhere
4. **Basic Example: Real-Time Transcript Processing**
Start by capturing speech-to-text transcripts sent from OMI to your webhook, then log or analyze them.
5. **Test Your App**
Connect the webhook URL to OMI by pasting it in the "Create an App" section in the OMI app interface. Start speaking, and you will see your app receive data in real time.
6. **Enhance Your App**
Once comfortable, add custom features:
    - Set reminders from phrases
    - Trigger notifications
    - Integrate with other APIs (calendar, social media, smart home)
7. **Submit Your App**
After testing, submit on the OMI platform to share with the community.

## Resources \& Recommendations

- Follow the OMI Prompt-Based and Integration App guides linked in the docs.
- Check OMI code examples for inspiration.
- Use simple tools like webhook.site initially.
- Experiment with basic scripts to handle incoming webhooks.

If you'd like, I can help you create a minimal example app step-by-step tailored to your programming skills. Just tell me your preferred programming language!

---

# help me build nodejs app

Here’s a simple step-by-step guide to build a basic Node.js app that receives real-time transcripts from OMI via a webhook and logs them:

## Step 1: Set Up Your Node.js Project

1. Make sure you have Node.js installed.
2. Create a new folder for your app and open a terminal in it.
3. Run:

```bash
npm init -y
npm install express body-parser
```


## Step 2: Create a Basic Express Server

Create a file named `app.js` with this content:

```js
const express = require('express');
const bodyParser = require('body-parser');

const app = express();
const PORT = process.env.PORT || 3000;

// Parse JSON bodies
app.use(bodyParser.json());

// Endpoint to receive webhook from OMI
app.post('/webhook', (req, res) => {
  const transcript = req.body.transcript || req.body.text || 'No transcript data';
  console.log('Received transcript:', transcript);

  // Respond OK to OMI
  res.status(200).send('Received');
});

app.listen(PORT, () => {
  console.log(`Server listening on port ${PORT}`);
});
```


## Step 3: Run Your Server

In the terminal, run:

```bash
node app.js
```

The server will listen on port 3000.

## Step 4: Use ngrok or Another Tunnel Service

Since webhook.site is just for testing and OMI needs to reach your local server, use [ngrok](https://ngrok.com/) to expose your localhost:

```bash
ngrok http 3000
```

This will give you a public URL like `https://abcd1234.ngrok.io`.

## Step 5: Connect to OMI

- In the OMI app, go to "Create an App" → “Integration App”
- Paste your ngrok URL with the webhook path: `https://abcd1234.ngrok.io/webhook`
- Start speaking and check your Node.js server console to see the transcripts logged.

***

If you want, I can help you add features like auto-responses or integration with other APIs next. Just let me know!

---

# [https://github.com/BasedHardware/omi](https://github.com/BasedHardware/omi)

are you sure?

Yes, the GitHub repository BasedHardware/omi is the official open-source project for Omi, the AI wearable that captures conversations, transcribes them, and offers summaries and action items. It is actively maintained with many contributors and releases in 2025. The repo includes the device firmware, app, AI personas, SDKs, and documentation to help build integrations and apps. The project is well-documented with quick start guides and community support.

The Omi AI wearable system supports creating apps via webhooks, and you can build Node.js or other language apps that connect to it using webhook URLs, exactly as described in the docs and examples I shared earlier.

This confirms the authenticity and activity of the Omi open-source AI wearable project on GitHub by BasedHardware.[^5_1][^5_2][^5_3]

If you want, I can help guide you through using this repo, its SDKs, or building custom apps to interface with Omi using Node.js. Let me know!
<span style="display:none">[^5_10][^5_11][^5_12][^5_13][^5_14][^5_15][^5_16][^5_17][^5_18][^5_19][^5_20][^5_4][^5_5][^5_6][^5_7][^5_8][^5_9]</span>

<div align="center">⁂</div>

[^5_1]: https://github.com/BasedHardware

[^5_2]: https://raw.githubusercontent.com/BasedHardware/omi/main/README.md

[^5_3]: https://docs.omi.me/doc/developer/apps/Introduction

[^5_4]: https://github.com/BasedHardware/omi

[^5_5]: https://github.com/BasedHardware/Friend/releases

[^5_6]: https://github.com/BasedHardware/omi-community-certs

[^5_7]: https://www.linkedin.com/posts/langchain_omi-ai-wearable-an-open-source-device-activity-7316928106072526848-moaD

[^5_8]: https://www.omi.me

[^5_9]: https://www.omi.me/blogs/ai-enhanced-therapy/firmware-guides

[^5_10]: https://docs.webhook.site/index.html

[^5_11]: https://github.com/sponsors/BasedHardware

[^5_12]: https://www.odinhalvorson.com/omi-ai-is-not-your-friend/

[^5_13]: https://webhook.site

[^5_14]: https://www.omi.me/products/omi

[^5_15]: https://www.youtube.com/watch?v=OOjWeGhuLeY

[^5_16]: https://www.theverge.com/2025/1/8/24338750/omi-ai-wearable-friend-companion

[^5_17]: https://www.omi.me/blogs/api-guides/how-to-receive-webhook-notifications-from-github-api-in-node-js

[^5_18]: https://docs.omi.me/getstartedwithomi

[^5_19]: https://www.youtube.com/watch?v=jDlDWpGmEXw

[^5_20]: https://www.reddit.com/r/ArtificialInteligence/comments/1fuepwz/my_review_after_using_friend_omi_by_based/


---

# okay help me build python app that is part of omi app

To build a Python app integrated with Omi that processes real-time conversation data, here’s a step-by-step simple guide:

## Step 1: Set up Python Environment

1. Make sure Python 3 is installed.
2. Create a new folder for your app.
3. Install Flask to create a web server and requests to handle HTTP if needed:
```bash
pip install flask
```


## Step 2: Create a Basic Flask Webhook Server

Create a file called `app.py` with the following content to receive webhook POST requests from Omi:

```python
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    transcript = data.get('transcript') or data.get('text') or 'No transcript received'
    print(f"Received transcript: {transcript}")

    # Add your processing logic here (e.g., save to DB, trigger actions)

    return jsonify({"status": "received"}), 200

if __name__ == '__main__':
    app.run(port=3000)
```


## Step 3: Run Your Python Server

In your terminal inside the project folder, run:

```bash
python app.py
```

The server will listen on port 3000 by default.

## Step 4: Make Your Local Server Public

Use a tunneling tool like [ngrok](https://ngrok.com/) to expose your localhost for Omi to send data:

```bash
ngrok http 3000
```

Copy the public URL provided by ngrok.

## Step 5: Connect the Webhook URL to Omi

- In the Omi app, go to "Create an App" → "Integration App" or whichever app type is suitable.
- Paste your ngrok URL with the `/webhook` path, e.g., `https://abcd1234.ngrok.io/webhook`.
- Start speaking into Omi; you will see real-time transcripts logged in your Python app console.

***

If you want, I can help you add more features such as saving transcripts, responding automatically, or integrating with other APIs inside your Python app. Just ask!

---

# can i build it comletely with webhook.site

Yes, you can build and test your Python app entirely using webhook.site, especially for initial development and debugging. Webhook.site provides a unique URL where you can send and receive webhook data without the need to host your own server.

## How to Use webhook.site for Your Python App Development:

1. **Create a Webhook URL**
    - Go to [webhook.site](https://webhook.site/)
    - Copy your unique webhook URL provided on the homepage.
2. **Configure Omi to Send Data**
    - In the Omi app, set this webhook URL as your webhook destination.
    - When you speak or trigger actions, Omi will send data to this URL.
3. **Observe Data on webhook.site**
    - The site will display incoming webhook requests, including conversation transcripts or other data.
    - You can inspect the payload directly.
4. **Simulate or Automate Responses**
    - Although webhook.site isn't a server, you can see data and manually respond by copying the payload to test how your code would handle it.
    - For more advanced automation, you might connect webhook.site to your local or cloud server for processing (e.g., using ngrok).

## Limitations

- Webhook.site is excellent for testing and inspecting payloads.
- It **cannot** run backend logic or process data dynamically like a server would.
- For implementing a full, interactive app, you will eventually need to host your Python app on a server or local machine and expose it via ngrok or cloud hosting.


## Summary

- Use webhook.site for easy, quick testing of incoming webhook payloads.
- For full functionality, develop your Python app locally or on a server, then connect with webhook.site for testing purposes.

Would you like me to help you set up a Python app that works with webhook.site, or guide you through transitioning from webhook.site to a full server?

---

# give me step by step tutorial for dummy, i have no idea how webhook work neither omi app

Here is a simple, step-by-step tutorial for a beginner to understand how to use a webhook with the Omi app, using webhook.site for testing. No coding or server setup needed at first.

***

## Step 1: Understand What a Webhook Is

- A webhook is like a phone number where an app (like Omi) sends information automatically.
- When something happens in Omi (e.g., you speak), it sends data (transcription) to this webhook URL immediately.
- The webhook URL receives and shows this data for you to see or use.

***

## Step 2: Create a Webhook URL with webhook.site

1. Go to [https://webhook.site](https://webhook.site).
2. When the page loads, you automatically get a unique URL at the top — this is your webhook URL.
3. Copy this URL (it looks like `https://webhook.site/unique-id`).

***

## Step 3: Connect the Webhook URL in Your Omi App

1. Open your Omi app on your phone or device.
2. Look for a section like **“Explore” > “Create an App”** or **“Connect Device”**.
3. Choose “Create an App”.
4. Select **Integration App** or similar.
5. Paste your webhook.site URL in the field for webhook or API endpoint.
6. Install or activate the app.

***

## Step 4: Start Speaking to Omi

- Speak into your Omi device.
- The Omi app will send what you say as text to the webhook URL.

***

## Step 5: See Your Real-Time Transcript on webhook.site

- Go back to your webhook.site page.
- Under “Requests,” you’ll see live updates showing the data sent by Omi.
- This data usually includes your spoken words transcribed into text.

***

## Step 6 (Optional): Understand the Data

- Click on the most recent request on webhook.site.
- You will see details like headers and JSON content.
- The JSON will likely have fields like `"transcript"` or `"text"` containing what you spoke.

***

## What You Have Done So Far

- Created a webhook endpoint URL using webhook.site.
- Connected Omi to send speech transcripts to this webhook.
- Verified that the webhook receives and shows your speech data in real time.

***

## What’s Next?

- Once you’re comfortable, you might want to build a small program (in Python or Node.js) that listens on your own server (instead of webhook.site) to:
    - Save transcripts to a file or database.
    - Perform actions like reminders based on what you say.
    - Respond back to Omi or other services.
- I can guide you step-by-step to build this simple server app next!

***

If you want, say: **"Ready for the next step"** and I’ll help you build a basic app that processes your Omi transcripts automatically.

---

# omi doenst let me use private apps?

OMI does allow creating apps, but there are some restrictions on private apps:

- Private apps can only be enabled by the app owner or designated testers. They are not publicly accessible to all users.
- To enable and use a private app, you must authenticate via OMI's OAuth flow and pass setup checks.
- Paid or subscription-based apps also have additional verification before enabling.
- If your app is private, only selected users can install and use it; general users cannot browse or install it from the public app store within OMI.
- Public apps are accessible to all users and can be installed freely.

This means that if you create a private app during development or testing, you must be listed as the owner or tester to use it. Otherwise, to make apps widely available, you need to publish them as public apps with proper setup and approval.

If you are running into restrictions on using private apps, this is likely why. You can still test apps privately yourself by following the proper registration and OAuth process, but others won't see them until made public.

If you want, I can guide you through the process of setting up and testing a private app properly or help with publishing to public use.

References: OMI OAuth and App Enablement docs.[^9_1]
<span style="display:none">[^9_10][^9_11][^9_12][^9_13][^9_14][^9_15][^9_16][^9_17][^9_18][^9_19][^9_2][^9_20][^9_3][^9_4][^9_5][^9_6][^9_7][^9_8][^9_9]</span>

<div align="center">⁂</div>

[^9_1]: https://docs.omi.me/doc/developer/apps/Oauth

[^9_2]: https://docs.omi.me/doc/developer/AppSetup

[^9_3]: https://omi.sg/terms

[^9_4]: https://apps.apple.com/my/app/omi-date-meet-friends/id1347676495

[^9_5]: https://docs.aveva.com/bundle/sp-install/page/298263.html

[^9_6]: https://www.youtube.com/watch?v=OOjWeGhuLeY

[^9_7]: https://docs.aveva.com/bundle/sp-omi/page/337770.html

[^9_8]: https://omiapps.com/terms

[^9_9]: https://www.youtube.com/watch?v=jDlDWpGmEXw

[^9_10]: https://www.tiktok.com/discover/how-to-download-omi-tv-if-it-says-it’s-banned-in-your-region

[^9_11]: https://play.google.com/store/apps/details?id=sg.omi\&hl=en_US

[^9_12]: https://help.omi.me/en/articles/10401566-build-publish-and-earn-with-omi-apps

[^9_13]: https://omi.sg/privacy/

[^9_14]: https://www.androidenterprise.community/discussions/conversations/regarding-on-private-app-management/4512

[^9_15]: https://docs.aveva.com/bundle/sp-omi/page/563787.html

[^9_16]: https://www.omi.me/pages/privacy

[^9_17]: https://omi.sg/help

[^9_18]: https://omi.devpost.com/project-gallery

[^9_19]: https://www.reddit.com/r/accessibility/comments/1idl3gb/how_to_enable_accessibility_permission_for/

[^9_20]: https://help.omi.so/en/articles/6796344-to-start-add-a-product-on-omi


---

# okay, lets build nextjs server action typescript when writting any [readme.me](http://readme.me/) file or license file, make sure not include placeholder, always make it versatile

-use pnpm

- use app route only
- OPENAI_API_KEY only
- Language: Typescript
- Back-end: [Next.js](http://next.js/) Server Actions
- Node: pnpm
- use pnpm add openai only for any AI

very simple app

give me prompt to build it?

Here is a clear, versatile prompt you can use to build a simple Next.js app with TypeScript using server actions. It listens for file writes (like readme.me or license files), excludes placeholders, and integrates OpenAI via pnpm with only OPENAI_API_KEY:

***

**Prompt:**
"Build a minimal Next.js app in TypeScript using app directory routes and server actions only. Use pnpm as a package manager, and install only the `openai` package via `pnpm add openai` to interact with OpenAI API. The app should:

- Detect when a file named `readme.me` or any license file is written (simulate or accept input accordingly).
- Process file content on the server using Next.js server actions.
- Ensure any placeholder text is removed or excluded from processing.
- The app should be very simple and versatile, focusing on backend only (no frontend UI required).
- Use the environment variable `OPENAI_API_KEY` to authenticate requests to OpenAI.
- Provide a backend API route or server action handling that accepts text content for processing by OpenAI.
- Use TypeScript strictly and follow Next.js 14+ app route conventions.
- Include clear modular code suitable for straightforward extension or integration.
- No additional dependencies except `openai` installed via pnpm.

Please generate the full Next.js server action code for this app setup."

***

Let me know if you want me to generate the actual TypeScript code for you next!
<span style="display:none">[^10_1]</span>

<div align="center">⁂</div>

[^10_1]: http://readme.me


---

# The Opportunity: Western audiences are fascinated by Japanese culture. We love their food, get Japanese characters tattooed on our skin and binge watch anime late into the night. And who doesn’t love an ancient Japanese concept? Kintsugi. Kaizen. Wabi-Sabi. Mugenkai. The list is endless (particularly since I totally made up one of those…). TikTok videos tagged \#Ikigai have amassed over 180M views, and Google searches for “Wabi-Sabi” have doubled in the past 5 years. Which got us thinking, why not create a media brand around this concept? Here’s what we’re thinking.

The Solution:
In a line: Feedback delivering one beautifully explained Japanese concept per conversation.
Product:
🧠 Each response focuses on a single Japanese idea, what it means, where it comes from, and how to apply it.
✍️ The ressponse is a simple, 3-minute read, with quotable wisdom that begs to be forwarded or screenshotted.
🇯🇵 The content is curated by Japanese researchers, translators, or advisors to avoid “ikigai-washing” and ensure accuracy
📈 You use this as the basis of a media brand which could expand into other mediums over time
Business Model: Free conversation response and monetize through selling ads
End Goal: Hold onto the response for distribution purposes, build an audience over time and launch other products to that audience

The Opportunity: Western audiences are fascinated by Japanese culture. We love their food, get Japanese characters tattooed on our skin and binge watch anime late into the night. And who doesn’t love an ancient Japanese concept? Kintsugi. Kaizen. Wabi-Sabi. Mugenkai. The list is endless (particularly since I totally made up one of those…). TikTok videos tagged \#Ikigai have amassed over 180M views, and Google searches for “Wabi-Sabi” have doubled in the past 5 years. Which got us thinking, why not create a media brand around this concept? Here’s what we’re thinking.
The Solution:
In a line: Feedback delivering one beautifully explained Japanese concept per conversation.
Product:
🧠 Each response focuses on a single Japanese idea, what it means, where it comes from, and how to apply it.
✍️ The ressponse is a simple, 3-minute read, with quotable wisdom that begs to be forwarded or screenshotted.
🇯🇵 The content is curated by Japanese researchers, translators, or advisors to avoid “ikigai-washing” and ensure accuracy
📈 You use this as the basis of a media brand which could expand into other mediums over time
Business Model: Free conversation response and monetize through selling ads
End Goal: Hold onto the response for distribution purposes, build an audience over time and launch other products to that audience

