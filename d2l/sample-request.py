import requests

# OAuth token obtained from Brightspace
access_token = 'YOUR_ACCESS_TOKEN'

# The API endpoint you want to access
api_url = 'https://yourinstitution.brightspace.com/d2l/api/...'

# Headers for the request
headers = {
    'Authorization': f'Bearer {access_token}',
    'Content-Type': 'application/json'
}

# Make the API request
response = requests.get(api_url, headers=headers)

# Process the response
data = response.json()
