import json
import urllib.request
import re

USER = "Mohsena1990"
API_URL = f"https://github.com{USER}/repos?sort=updated&per_page=10"

try:
    req = urllib.request.Request(API_URL, headers={"User-Agent": "Python-Script"})
    with urllib.request.urlopen(req) as response:
        repos = json.loads(response.read().decode())
    
    table_rows = ["| 📁 Repository | 📝 Description | 📅 Started On |", "| :--- | :--- | :--- |"]
    for repo in repos:
        if repo["name"] == USER:  
            continue
            
        name = f"**[{repo['name']}]({repo['html_url']})**"
        desc = repo["description"] if repo["description"] else "No description provided."
        
        # FIX: Extracting the first element index [0] to keep it as a clean text string
        start_date = repo["created_at"].split("T")[0]
        
        table_rows.append(f"| {name} | {desc} | {start_date} |")
        
    table_content = "\n".join(table_rows)

    with open("README.md", "r", encoding="utf-8") as f:
        readme = f.read()

    pattern = r"<!-- START_PROJECTS -->.*?<!-- END_PROJECTS -->"
    replacement = f"<!-- START_PROJECTS -->\n{table_content}\n<!-- END_PROJECTS -->"
    updated_readme = re.sub(pattern, replacement, readme, flags=re.DOTALL)

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(updated_readme)
        
    print("README.md updated with project start dates successfully!")

except Exception as e:
    print(f"Error updating README: {e}")
