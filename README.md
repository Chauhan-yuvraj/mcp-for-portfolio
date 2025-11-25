Here are the professional **README.md** files for both your Backend and Frontend.

---

### 1. Backend README
**Location:** `my-portfolio-ai-backend/README.md`

```markdown
# 🧠 MCP AI Portfolio Backend

This is the intelligent backend for my personal portfolio website. It leverages **Google Gemini 2.0 Flash** and the **Model Context Protocol (MCP)** to create a "living" AI agent that knows everything about my professional background, GitHub stats, and blogs.

Built with **FastAPI** and **Python**, it acts as a bridge between the frontend and the LLM, enabling tool calling and real-time data fetching.

## 🚀 Features

- **MCP Architecture:** Uses Anthropic's Model Context Protocol to standardize tool usage.
- **Single Source of Truth:** Reads data dynamically from modular Markdown files (`data/`).
- **Live GitHub Stats:** Fetches real-time stars, repositories, and streak data using the GitHub API.
- **Context Aware:** Handles user history and remembers names across sessions.
- **Gemini 2.0 Flash:** Powered by Google's latest high-speed model.

## 📂 Project Structure

```text
/
├── main.py            # FastAPI entry point & Chat Logic
├── server.py          # MCP Server & Tool Definitions
├── data/              # The Knowledge Base (Markdown)
│   ├── about.md       # Bio, Contact, Skills
│   ├── experience.md  # Work History
│   ├── projects.md    # Static Projects List
│   └── blogs.md       # Blog Links
├── .env               # Secrets (Not on GitHub)
└── requirements.txt   # Dependencies
```

## 🛠️ Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone <repo-url>
   cd my-portfolio-ai-backend
   ```

2. **Create a virtual environment (Optional but recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up Environment Variables:**
   Create a `.env` file in the root directory:
   ```ini
   GOOGLE_API_KEY=your_gemini_api_key
   GITHUB_TOKEN=your_github_classic_token
   GITHUB_USERNAME=Chauhan-yuvraj
   DEV_TO_USER=uvizhere
   ```

5. **Run the Server:**
   ```bash
   uvicorn main:app --reload
   ```
   The API will be live at `http://127.0.0.1:8000/chat`.

## 📡 API Endpoint

**POST** `/chat`

**Payload:**
```json
{
  "message": "What is his GitHub streak?",
  "username": "Aditya",
  "history": [
    {"role": "user", "content": "Hi"},
    {"role": "model", "content": "Hello Aditya!"}
  ]
}
```

## ☁️ Deployment (Render)

1. Connect repo to Render.
2. Select **Python 3** Runtime.
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add Environment Variables from your `.env` file.

---
```

---

### 2. Frontend README
**Location:** `my-portfolio-frontend/README.md` (or your root folder)

```markdown
# 🎨 Yuvraj's Portfolio & AI Chatbot

A modern, highly interactive portfolio website built with **Next.js**, **TypeScript**, and **Tailwind CSS**. 

The highlight of this project is the integrated **AI Assistant (UV)**. Unlike standard chatbots, UV uses the **Model Context Protocol (MCP)** to fetch real-time data about my GitHub activity, read my resume, and answer questions about my specific tech stack.

## ✨ Key Features

- **🤖 AI Agent Integration:** Embeds a custom MCP-powered chatbot that can browse my projects and stats.
- **💾 Persistent Memory:** Remembers the user's name across sessions using LocalStorage.
- **📱 Responsive Design:** Features a dedicated mobile drawer for the chat interface.
- **🎭 Animations:** Smooth transitions and "dust" text effects using **Framer Motion**.
- **🖼️ Dynamic Avatars:** Generates custom pixel-art avatars for users via DiceBear API.

## 🛠️ Tech Stack

- **Framework:** Next.js 14 (App Router)
- **Language:** TypeScript
- **Styling:** Tailwind CSS
- **Animations:** Framer Motion
- **Icons:** Lucide React
- **Backend:** Python (FastAPI + MCP) [Hosted separately]

## 🚀 Getting Started

1. **Clone the repository:**
   ```bash
   git clone <repo-url>
   cd my-portfolio
   ```

2. **Install dependencies:**
   ```bash
   npm install
   # or
   yarn install
   ```

3. **Configure the Backend:**
   Open `src/services/chatService.ts` and update the `API_URL` to point to your backend:
   ```typescript
   const API_URL = "http://127.0.0.1:8000/chat"; // Local
   // OR
   const API_URL = "https://your-backend.onrender.com/chat"; // Production
   ```

4. **Run the development server:**
   ```bash
   npm run dev
   ```

5. Open [http://localhost:3000](http://localhost:3000) with your browser.

## 📂 Architecture Overview

1. **User asks a question** (e.g., *"List his repos"*).
2. **Frontend** sends the message + history to the **FastAPI Backend**.
3. **Backend** initializes the **Gemini 2.0 Agent** with a System Prompt.
4. **Gemini** decides it needs a tool (`get_github_repos`) and requests it.
5. **MCP Server** executes the Python function to fetch data from GitHub API.
6. **Gemini** summarizes the raw data and sends a natural response back to the **Frontend**.

## 📄 License

This project is open-source and available under the MIT License.
```