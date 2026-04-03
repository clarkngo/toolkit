import requests
import os
import re
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

# Configuration from .env
ORG = os.getenv("ORG_NAME")
TOKEN = os.getenv("GITHUB_TOKEN")
COURSE_PREFIX = "dit635"

def is_protected_template(repo_name):
    """Protects DIT635-TT01 through DIT635-TT10."""
    pattern = r"^DIT635-TT(0[1-9]|10)$"
    return re.match(pattern, repo_name, re.IGNORECASE)

def fetch_and_verify():
    if not TOKEN or not ORG:
        print("Error: GITHUB_TOKEN or ORG_NAME not found in .env file.")
        return

    url = f"https://api.github.com/orgs/{ORG}/repos"
    headers = {
        "Authorization": f"token {TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # Using a loop to handle pagination in case you have > 100 repos
    targets = []
    page = 1
    
    print(f"--- Scanning Organization: {ORG} ---\n")

    while True:
        response = requests.get(url, headers=headers, params={"per_page": 100, "page": page})
        
        if response.status_code != 200:
            print(f"Error: {response.status_code} - {response.text}")
            break

        repos = response.json()
        if not repos:
            break

        for repo in repos:
            name = repo['name']
            
            # Check if it's a DIT635 repo
            if COURSE_PREFIX in name.lower():
                if is_protected_template(name) or repo.get('is_template', False):
                    print(f"[KEEP] Template: {name}")
                else:
                    print(f"[DELETE] Student: {name}")
                    targets.append(name)
        
        page += 1

    print(f"\n--- Summary ---")
    print(f"Total student repos found to delete: {len(targets)}")

if __name__ == "__main__":
    fetch_and_verify()