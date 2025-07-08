import os
import requests
from dotenv import load_dotenv

# Load .env variables
load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
ORG = os.getenv("ORG_NAME")

headers = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}

def get_pending_invitations(org):
    url = f"https://api.github.com/orgs/{org}/invitations"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        invites = response.json()
        if not invites:
            print("✅ No pending invitations.")
            return
        print(f"📬 Pending invitations for org '{org}':\n")
        for invite in invites:
            user = invite.get("login") or invite.get("email", "(unknown email)")
            role = invite.get("role", "member")
            print(f"- {user} ({role})")
    else:
        print(f"❌ Error {response.status_code}: {response.json().get('message', 'Unknown error')}")

if __name__ == "__main__":
    get_pending_invitations(ORG)
