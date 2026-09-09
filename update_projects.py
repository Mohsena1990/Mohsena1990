import json
import os
import re
import urllib.request

USER = "Mohsena1990"
TOKEN = os.environ.get("GH_PAT")
DESC_MAX_LEN = 100

# The public `/users/{USER}/repos` endpoint never returns private repos, even
# with a token. Listing private repos requires the authenticated `/user/repos`
# endpoint, which is only available when a PAT is supplied via GH_PAT.
if TOKEN:
    API_URL = "https://api.github.com/user/repos?affiliation=owner&sort=updated&per_page=100"
else:
    API_URL = f"https://api.github.com/users/{USER}/repos?sort=updated&per_page=100"


def fetch_all_repos():
    repos = []
    url = API_URL
    headers = {"User-Agent": "Python-Script", "Accept": "application/vnd.github+json"}
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"

    while url:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as response:
            repos.extend(json.loads(response.read().decode()))
            link_header = response.headers.get("Link", "")

        # Follow RFC 5988 pagination (rel="next") for accounts with >100 repos.
        next_match = re.search(r'<([^>]+)>;\s*rel="next"', link_header)
        url = next_match.group(1) if next_match else None

    return repos


def truncate(text, max_len):
    text = text.strip().replace("\n", " ").replace("|", "\\|")
    if len(text) <= max_len:
        return text
    return text[: max_len - 1].rstrip() + "…"


try:
    repos = fetch_all_repos()

    table_rows = ["| 📁 Repository | 📝 Description | 📅 Started On |", "| :--- | :--- | :--- |"]
    for repo in sorted(repos, key=lambda r: r["created_at"], reverse=True):
        if repo["name"] == USER or repo.get("fork"):
            continue

        icon = "🔒 " if repo.get("private") else ""
        name = f"**[{icon}{repo['name']}]({repo['html_url']})**"
        desc = truncate(repo["description"], DESC_MAX_LEN) if repo["description"] else "No description provided."
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

    print(f"README.md updated with {len(table_rows) - 2} project(s).")

except Exception as e:
    print(f"Error updating README: {e}")
