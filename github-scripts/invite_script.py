import requests
import os
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()


# ====== CONFIG ======
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
ORG = os.getenv("ORG_NAME")
INPUT_FILE = "users_to_invite.txt"  # one GitHub username per line
LOG_FILE = f"invite_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
DEFAULT_ROLE = "direct_member"  # or 'admin'

headers = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}

# ====== LOAD USERS FROM TXT ======
def load_usernames(file_path):
    with open(file_path, "r") as f:
        return [line.strip() for line in f if line.strip()]

# ====== LOOK UP USER ID ======
def get_user_id(username):
    url = f"https://api.github.com/users/{username}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json().get("id"), None
    else:
        return None, f"{response.status_code} - {response.json().get('message', 'Unknown error')}"

# ====== INVITE USER BY ID ======
def invite_user_by_id(user_id):
    url = f"https://api.github.com/orgs/{ORG}/invitations"
    data = {
        "invitee_id": user_id,
        "role": DEFAULT_ROLE
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 201:
        return True, "✅ Invitation sent"
    else:
        return False, f"{response.status_code} - {response.json().get('message', 'Unknown error')}"

# ====== MAIN SCRIPT ======
def main():
    usernames = load_usernames(INPUT_FILE)
    log_lines = ["Username,Status,Message\n"]

    for username in usernames:
        print(f"🔍 Looking up user: {username}")
        user_id, lookup_error = get_user_id(username)
        if user_id:
            success, message = invite_user_by_id(user_id)
        else:
            success, message = False, f"User lookup failed: {lookup_error}"

        print(f"{username}: {message}")
        log_lines.append(f"{username},{'Success' if success else 'Failed'},{message}\n")

    with open(LOG_FILE, "w") as log_file:
        log_file.writelines(log_lines)

    print(f"\n📄 Invitation log saved to: {LOG_FILE}")

if __name__ == "__main__":
    main()
