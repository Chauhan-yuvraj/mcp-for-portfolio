import os
import httpx
from mcp.server.fastmcp import FastMCP
from github import Github
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime, timedelta, timezone

load_dotenv()

mcp = FastMCP("Yuvraj-Portfolio-Server")

# --- CONFIGURATION ---
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_USERNAME = os.getenv("GITHUB_USERNAME")
DEV_TO_USER = os.getenv("DEV_TO_USER")

# Define Data Paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"

# --- HELPER FUNCTIONS ---
def read_file(filename: str) -> str:
    """Helper to read markdown files safely from the data directory."""
    try:
        file_path = DATA_DIR / filename
        if not file_path.exists():
            return f"Error: The file '{filename}' was not found in the data directory."
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"

# --- STATIC DATA TOOLS ---

@mcp.tool()
def get_about_me() -> str:
    return read_file("about.md")

@mcp.tool()
def get_experience() -> str:
    return read_file("experience.md")

@mcp.tool()
def get_projects_static() -> str:
    return read_file("projects.md")

@mcp.tool()
def get_blogs_static() -> str:
    return read_file("blogs.md")

# --- DYNAMIC API TOOLS ---

@mcp.tool()
def get_github_repos() -> str:
    """
    Fetches a list of Yuvraj's recent public GitHub repositories.
    Use this when the user asks to "list repos", "show repositories", or "what code has he written?".
    """
    try:
        if not GITHUB_TOKEN or not GITHUB_USERNAME:
            return "GitHub credentials not configured."
            
        g = Github(GITHUB_TOKEN)
        user = g.get_user(GITHUB_USERNAME)

        repo_list = []
        # Get top 10 repos sorted by latest update
        repos = user.get_repos(sort="updated", direction="desc")
        
        for repo in repos:
            repo_list.append(f"📦 [{repo.name}]({repo.html_url}): {repo.description} (⭐ {repo.stargazers_count})")
            if len(repo_list) >= 10:
                break
        
        return "**Recently Updated Repositories:**\n" + "\n".join(repo_list)
    except Exception as e:
        return f"Error fetching repos: {str(e)}"

@mcp.tool()
def get_github_stats() -> str:
    """
    Fetches LIVE GitHub statistics: Commit streaks, Total Stars, Followers, and Recent Activity.
    Use this when the user asks about "Streaks", "GitHub Stats", "Activity", or "How active is he?".
    """
    try:
        if not GITHUB_TOKEN or not GITHUB_USERNAME:
            return "GitHub credentials not configured in .env."
            
        g = Github(GITHUB_TOKEN)
        user = g.get_user(GITHUB_USERNAME)

        # 1. Basic Stats
        total_repos = user.public_repos
        followers = user.followers
        account_created = user.created_at.strftime("%B %Y")
        
        # 2. Calculate Total Stars
        total_stars = 0
        repos = user.get_repos()
        for repo in repos:
            total_stars += repo.stargazers_count

        # 3. Get Recent Activity
        events = user.get_events()
        recent_activity = []
        last_active_date = None
        event_count_7_days = 0
        
        # Timezone aware comparison
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=7)

        for event in events:
            if event.created_at > cutoff_date:
                event_count_7_days += 1
                
            if len(recent_activity) < 3:
                date_str = event.created_at.strftime("%Y-%m-%d")
                readable_type = event.type.replace("Event", "")
                repo_name = event.repo.name if event.repo else "Unknown Repo"
                recent_activity.append(f"- {readable_type} on {date_str} (Repo: {repo_name})")
                
                if not last_active_date:
                    last_active_date = date_str

        stats_summary = f"""
        **GitHub Live Statistics for {GITHUB_USERNAME}**
        - 🌟 **Total Stars:** {total_stars}
        - 📦 **Public Repositories:** {total_repos}
        - 👥 **Followers:** {followers}
        - 🗓️ **Joined:** {account_created}
        
        **Recent Activity (Last 7 Days)**
        - **Total Actions:** {event_count_7_days}
        - **Last Active:** {last_active_date if last_active_date else "No recent activity"}
        
        **Latest Events:**
        {chr(10).join(recent_activity)}
        """
        return stats_summary

    except Exception as e:
        return f"Error fetching GitHub stats: {str(e)}"

@mcp.tool()
def get_latest_blogs_dynamic() -> str:
    """
    Fetches the absolutely latest articles from Dev.to API.
    """
    try:
        if DEV_TO_USER:
            url = f"https://dev.to/api/articles?username={DEV_TO_USER}"
            with httpx.Client() as client:
                resp = client.get(url)
                if resp.status_code == 200:
                    data = resp.json()
                    if not data: return "No blogs found on Dev.to."
                    blogs = [f"✍️ {a['title']} ({a['readable_publish_date']}) - {a['url']}" for a in data[:3]]
                    return "Latest Dev.to Articles:\n" + "\n".join(blogs)
        return "Dev.to username not configured."
    except Exception as e:
        return f"Error fetching blogs: {str(e)}"

if __name__ == "__main__":
    mcp.run()