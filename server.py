import os
import httpx
from mcp.server.fastmcp import FastMCP
from github import Github
from dotenv import load_dotenv

load_dotenv()

mcp = FastMCP("Yuvraj-Portfolio-Server")

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_USERNAME = os.getenv("GITHUB_USERNAME")

DEV_TO_USER = os.getenv("DEV_TO_USER")
DEV_TO_URL = f"https://dev.to/api/articles?username={DEV_TO_USER}"
PROFILE_PATH = "my_profile.txt"


# Get Resume
@mcp.tool()
def get_my_profile() -> str:
    """
    Read Yuvraj's personal profile, skills, and exerience from the local file.
    Use this when the user asks about your profile, skills, and experience.
    """
    try:
        if not os.path.exists(PROFILE_PATH):
            return "Profile file not found."
        with open(PROFILE_PATH, "r" , encoding="utf-8") as file:
            return file.read()
    except Exception as e:
        return f"An error occurred while reading the profile: {str(e)}"
    
# Get GitHub Projects
@mcp.tool()
def get_github_repositories() -> str:
    """
    Fetches Yuvraj's GitHub repositories.
    Use this when the user asks about your projects or GitHub repositories.
    """
    try:
        g  = Github(GITHUB_TOKEN) if GITHUB_TOKEN else Github()
        user = g.get_user(GITHUB_USERNAME)

        repo_list = []

        for repo in user.get_repos(sort="updated" , direction="desc"):
                        repo_list.append(f"📦 {repo.name}: {repo.description} (⭐ {repo.stargazers_count}) - {repo.html_url}")
                        if len(repo_list) >= 5:
                            break
        return "\n".join(repo_list)
    except Exception as e:
        return f"An error occurred while fetching GitHub repositories: {str(e)}"

# TOOL 3: Get Blog Posts
@mcp.tool()
def get_latest_blogs() -> str:
    """
    Fetches the latest blog posts from Dev.to.
    Use this when user asks about 'Articles', 'Blogs', or 'Writing'.
    """
    try:
        with httpx.Client() as client:
            response = client.get(f"{DEV_TO_URL}")
            data = response.json()
            
        blogs = []
        for article in data[:3]: # Get top 3
            blogs.append(f"✍️ {article['title']} ({article['readable_publish_date']})\n🔗 {article['url']}")
            
        return "\n".join(blogs)
    except Exception as e:
        return f"Error fetching blogs: {str(e)}"
    
if __name__ == "__main__":
    mcp.run()