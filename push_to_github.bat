@echo off
echo Initializing Git repository...
git init

echo Adding remote repository...
git remote add origin https://github.com/Chauhan-yuvraj/mcp-for-portfolio.git

echo Adding files...
git add .

echo Committing changes...
git commit -m "Initial commit: Portfolio AI backend with MCP server"

echo Pushing to GitHub...
git branch -M main
git push -u origin main

echo Done! Repository pushed to GitHub.
pause