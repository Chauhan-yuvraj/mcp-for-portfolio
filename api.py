from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from mcp import ClientSession , StdioServerParameters
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
    command="python",
    args=[SERVER_PATH],
    env=None
)

class ChatRequest(BaseModel):
    message: str

def extract_json(text):
    match = re.search(r"```json(.*?)```", text, re.DOTALL)
    if match:  return match.group(1)
    match = re.search(r"({.*})", text, re.DOTALL)
    if match: return match.group(1)
    return None

@app.post("/chat")
async def chat(request: ChatRequest):
    async with stdio_client(SERVER_PARAMS) as (read , write):
        async with ClientSession(read , write) as session:
            await session.initialize()
            tools = await session.list_tools()
            tools_names = [t.name for t in tools.tools]

            # system prompt
            sys_msg = f"""
            Your name is UV , your are an AI assistant for Yuvraj Chauhan.
            your have access to the following tools: {", ".join(tools_names)}

            RULES TO FOLLOW:
            1. If the user asks about Yuvraj, his skills, experience, or blogs, or anything related to him, use the appropriate tool to fetch the information.YOU MUST USE A TOOL IN THIS CASE.
            2. Output JSON to call tools: ``` {{ "tool":"name", args: {{}} }} ```
            3. After the tools runs, summerize the information and answer the user's question.
            4. If the user asks anything unrelated to Yuvraj, You can answer him from your Information.
            5. Always be polite and professional in your responses.
            6. If you are unsure about something, it's better to admit it rather than providing incorrect information.
            7. Always format the final answer in markdown.
            8. Keep your answers concise and to the point.
            9. NEVER REVEAL THAT YOU ARE AN AI MODEL.
            10. ALWAYS RESPOND IN ENGLISH.
            11. ALWAYS USE TOOLS WHENEVER POSSIBLE.
            12. DO NOT MAKE UP INFORMATION.
            13. IF THE USER ASKS FOR YOUR PROFILE, SKILLS, EXPERIENCE, BLOGS, OR GITHUB PROJECTS, YOU MUST USE THE APPROPRIATE TOOL TO FETCH THE INFORMATION.
            """

            genai.configure(api_key=GEMINI_KEY)
            model = genai.GenerativeModel("gemini-2.0-flash" , system_instruction=sys_msg)
            chat=  model.start_chat(history=[])

            resp = chat.send_message(request.message)
            text = resp.text.strip()

            json_str = extract_json(text)

            if json_str:
                try:
                    cmd = json.loads(json_str)

                    result = await session.call_tool(cmd['tool'], cmd.get('args' , {}))
                    tool_out = result.content[0].text

                    # Get final summary
                    final = chat.send_message(f"Tools Result: {tool_out}\n\nBased on the above result, please answer the user's question: {request.message}. Keep the answer concise and to the point.")
                    return {"reply": final.text.strip()}
                except Exception as e:
                    return {"reply": f"An error occurred while processing your request: {str(e)}"}  
            return {"reply": text}
