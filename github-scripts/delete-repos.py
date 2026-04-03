import requests
import os
import re
import time
from dotenv import load_dotenv

load_dotenv()

# Configuration
ORG = os.getenv("ORG_NAME")
TOKEN = os.getenv("GITHUB_TOKEN")
COURSE_PREFIX = "dit635"
DRY_RUN = False  # CHANGE TO False TO ACTUALLY DELETE

def is_protected_template(repo_name):
    # Matches DIT635-TT01 through DIT635-TT10 exactly
    pattern = r"^DIT635-TT(0[1-9]|10)$"
    return re.match(pattern, repo_name, re.IGNORECASE)

def run_cleanup():
    if not TOKEN:
        print("Error: GITHUB_TOKEN missing.")
        return

    headers = {
        "Authorization": f"token {TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    targets = []
    page = 1
    
    print(f"--- Starting Scan in {ORG} ---")
    
    while True:
        print(f"Scanning page {page}...")
        url = f"https://api.github.com/orgs/{ORG}/repos?per_page=100&page={page}"
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            print(f"Break: Stopped at page {page} ({response.status_code})")
            break

        repos = response.json()
        if not repos: # No more repos found
            break

        for repo in repos:
            name = repo['name']
            if COURSE_PREFIX in name.lower():
                if is_protected_template(name) or repo.get('is_template', False):
                    continue # Skip templates silently to keep logs clean
                else:
                    targets.append(name)
        
        page += 1

    print(f"\nScan Complete. Found {len(targets)} student repositories.")
    
    if not targets:
        print("Nothing to delete. Exiting.")
        return

    # Deletion Phase
    if DRY_RUN:
        print("--- DRY RUN MODE: No repos will be deleted ---")
        for t in targets:
            print(f"Would delete: {t}")
    else:
        confirm = input(f"CONFIRM: Delete {len(targets)} repos? (y/n): ")
        if confirm.lower() == 'y':
            for repo_name in targets:
                print(f"Deleting {repo_name}...", end=" ", flush=True)
                del_url = f"https://api.github.com/repos/{ORG}/{repo_name}"
                res = requests.delete(del_url, headers=headers)
                
                if res.status_code == 204:
                    print("✅ Done")
                else:
                    print(f"❌ Failed ({res.status_code})")
                
                # Small sleep to avoid hitting secondary rate limits during mass deletion
                time.sleep(0.5) 
        else:
            print("Deletion cancelled.")

if __name__ == "__main__":
    run_cleanup()