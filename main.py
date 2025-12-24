from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from dotenv import load_dotenv
import os
import re
import json
import sys
import google.generativeai as genai

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware, 
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)   

GEMINI_KEY = os.getenv("GOOGLE_API_KEY")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SERVER_PATH = os.path.join(BASE_DIR, "server.py")

SERVER_PARAMS = StdioServerParameters(
    command=sys.executable, 
    args=[SERVER_PATH],
    env=dict(os.environ)
)

class ChatRequest(BaseModel):
    message: str
    username: str | None = None 
    history: list[dict] = [] 

def extract_json(text):
    match = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL)
    if match: return match.group(1)
    match = re.search(r"(\{.*\})", text, re.DOTALL)
    if match: return match.group(1)
    return None

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        print(f"User: {request.username} | Message: {request.message}")
        
        async with stdio_client(SERVER_PARAMS) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                tools = await session.list_tools()
                tools_names = [t.name for t in tools.tools]

                if request.username:
                    user_context = (
                        f"CURRENT USER DATA:\n"
                        f"User's Name: {request.username}\n"
                        f"NOTE: You KNOW the user's name. Answer 'Who am I?' with {request.username}."
                    )
                else:
                    user_context = "CURRENT USER DATA: Unknown (The user is anonymous)."

                sys_msg = f"""
                Your name is UV, you are an AI assistant for Yuvraj Chauhan.
                You have access to tools: {", ".join(tools_names)}
                
                {user_context}

                RULES:
                1. **NAME HANDLING**: 
                   - Verify names. Output JSON: ```json {{ "action": "save_name", "name": "Name", "reply": "Saved." }} ```.
                   - Answer "What is my name?" from 'CURRENT USER DATA'.

                2. **TOOL USAGE**:
                   - **ALWAYS USE A TOOL** if the user asks about Yuvraj.
                   - If asking to **LIST REPOS** or "Show me code", use 'get_github_repos'.
                   - If asking about **STATS**, **STARS**, or **ACTIVITY**, use 'get_github_stats'.
                   - If asking about profile/skills, use 'get_about_me'.
                   - Tool JSON format: ```json {{ "tool": "tool_name", "args": {{}} }} ```
                
                3. **GENERAL**:
                   - Be professional and concise.
                   - Markdown supported.
                   - If a tool returns an error, TELL THE USER the specific error.
                """

                genai.configure(api_key=GEMINI_KEY)
                model = genai.GenerativeModel("gemini-2.0-flash", system_instruction=sys_msg)
                
                gemini_history = []
                for msg in request.history:
                    role = "user" if msg.get("role") == "user" else "model"
                    gemini_history.append({
                        "role": role,
                        "parts": [msg.get("content")]
                    })

                chat_session = model.start_chat(history=gemini_history)

                resp = chat_session.send_message(request.message)
                text = resp.text.strip()
                
                json_str = extract_json(text)

                if json_str:
                    try:
                        cmd = json.loads(json_str)
                        
                        if cmd.get("action") == "save_name":
                            return { "reply": cmd.get("reply"), "set_username": cmd.get("name") }

                        if "tool" in cmd:
                            tool_result = await session.call_tool(cmd['tool'], cmd.get('args', {}))
                            tool_out = tool_result.content[0].text
                            
                            final_prompt = f"Tool Result: {tool_out}\n\nBased on the above result, Answer the user: {request.message}"
                            final = chat_session.send_message(final_prompt)
                            return {"reply": final.text.strip()}
                            
                    except Exception as e:
                        return {"reply": f"Error processing request: {str(e)}"}

                return {"reply": text}
    except Exception as e:
        print(f"Critical Error: {str(e)}")
        return {"reply": f"System Error: {str(e)}"}