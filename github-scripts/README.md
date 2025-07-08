# GitHub Scripts

## Setup
Get your GitHub personal access token here:
https://github.com/settings/tokens

### invite_script.py - invite github usernames to organization
1. update `users_to_invite.txt` with github username per line
2. run with `python invite_script.py`
3. view `invite_log_YYYYMMDD.csv`

### pending_invites.py - view pending invites in organization
1. run with `python pending_invites.py`