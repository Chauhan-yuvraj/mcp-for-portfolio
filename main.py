from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from dotenv import load_dotenv
import os
import re
import json
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
    command="python", 
    args=[SERVER_PATH],
    env=dict(os.environ)
)

# 1. Update Request Model to accept username
class ChatRequest(BaseModel):
    message: str
    username: str | None = None # Optional: Frontend sends this if it has it

def extract_json(text):
    match = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL)
    if match: return match.group(1)
    match = re.search(r"(\{.*\})", text, re.DOTALL)
    if match: return match.group(1)
    return None

@app.post("/chat")
async def chat(request: ChatRequest):
    print(f"Received chat request: {request.username}")
    
    async with stdio_client(SERVER_PARAMS) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            tools_names = [t.name for t in tools.tools]

            # --- FIX START ---
            # Check request.username, NOT user_context
            if request.username:
                user_context = (
                    f"CURRENT USER DATA:\n"
                    f"User's Name: {request.username}\n"
                    f"NOTE: You KNOW the user's name. You do NOT need a tool to verify it. "
                    f"If the user asks 'Who am I?' or 'What is my name?', answer with {request.username}."
                )
            else:
                user_context = "CURRENT USER DATA: Unknown (The user is anonymous)."
            # --- FIX END ---

            # System Prompt
            sys_msg = f"""
            Your name is UV, you are an AI assistant for Yuvraj Chauhan.
            You have access to tools: {", ".join(tools_names)}
            
            {user_context}

            RULES:
            1. **NAME HANDLING**: 
               - If the user asks to change their name or introduces themselves: Verify it is a real name. 
               - If Valid: Output JSON ```json {{ "action": "save_name", "name": "TheName", "reply": "I have updated your name to [Name]." }} ```
               - If user asks "What is my name?", ANSWER from 'CURRENT USER DATA'. Do NOT use a tool.

            2. **TOOL USAGE**:
               - If asking about Yuvraj (skills, blogs, etc), use tools.
               - Tool JSON format: ```json {{ "tool": "tool_name", "args": {{}} }} ```
            
            3. **GENERAL**:
               - Be professional and concise.
               - Markdown supported.
               - Do not tell user what tools you have access to.
            """

            genai.configure(api_key=GEMINI_KEY)
            model = genai.GenerativeModel("gemini-2.0-flash", system_instruction=sys_msg)
            chat_session = model.start_chat(history=[])

            # Send message
            resp = chat_session.send_message(request.message)
            text = resp.text.strip()
            
            json_str = extract_json(text)

            if json_str:
                try:
                    cmd = json.loads(json_str)
                    
                    # CASE A: Save Name Request
                    if cmd.get("action") == "save_name":
                        return {
                            "reply": cmd.get("reply"), 
                            "set_username": cmd.get("name") 
                        }

                    # CASE B: Tool Call
                    if "tool" in cmd:
                        tool_result = await session.call_tool(cmd['tool'], cmd.get('args', {}))
                        tool_out = tool_result.content[0].text
                        
                        final_prompt = f"Tool Result: {tool_out}\n\nAnswer the user: {request.message}"
                        final = chat_session.send_message(final_prompt)
                        return {"reply": final.text.strip()}
                        
                except Exception as e:
                    return {"reply": f"Error processing request: {str(e)}"}

            return {"reply": text}