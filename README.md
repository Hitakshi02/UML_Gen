```markdown
## 🧠 Dialogflow Integration Setup

This branch focuses on integrating Dialogflow with the UML Generator backend to enable conversational interactions for diagram generation.

### 🛠 Prerequisites

- ✅ [Ngrok](https://ngrok.com/) installed (for local HTTPS tunneling)
- ✅ `FastAPI` backend running (with webhook logic)

---

### ⚙️ Steps to Run Locally

1. **Start your FastAPI server**:
   Make sure your backend is running and listening on a POST endpoint (e.g., `/webhook`).

   ```bash
   uvicorn main:app --reload
   ```

2. **Start Ngrok to tunnel your local server**:
   Use ngrok to expose your local FastAPI server to the internet:

   ```bash
   ngrok http 8000
   ```

   This will generate a public HTTPS URL like `https://xyz123.ngrok.io`

3. **Connect Webhook in Dialogflow**:
   - Go to Dialogflow Console
   - Navigate to **Fulfillment** → **Enable Webhook**
   - Paste the ngrok URL followed by your endpoint (e.g., `https://xyz123.ngrok.io/webhook`)
   - Save and **Enable Webhook for Intents**

---

### 🔗 How the Flow Works

1. User inputs a trained phrase in Dialogflow.
2. Dialogflow triggers an intent and sends a **POST request** to your webhook.
3. The FastAPI server processes it and returns a structured response.
4. This is used to guide UML generation.

---

### ⚠️ Known Limitations

- 🚫 Only **trained phrases** will trigger intents correctly.
- ❗ Free-tier ngrok URLs expire after 8 hours; regenerate and update Dialogflow if needed.

