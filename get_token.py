import os
import requests
from dotenv import load_dotenv

# We charge the hidden variables from .env file
load_dotenv()

# We read the credentials securely
APP_ID = os.getenv("MELI_APP_ID")
CLIENT_SECRET = os.getenv("MELI_CLIENT_SECRET")
REDIRECT_URI = "https://www.google.com"
print(
    "⚠️ Remember to copy only the part of code that starts with TG- and ends before the &"
)
CODIGO_TG = input("Paste your authorization code here: ").strip()

url = "https://api.mercadolibre.com/oauth/token"

payload = {
    "grant_type": "authorization_code",
    "client_id": APP_ID,
    "client_secret": CLIENT_SECRET,
    "code": CODIGO_TG,
    "redirect_uri": REDIRECT_URI,
}

headers = {
    "accept": "application/json",
    "content-type": "application/x-www-form-urlencoded",
}

print("Exchanging code for Access Token...")
response = requests.post(url, headers=headers, data=payload)

if response.status_code == 200:
    data = response.json()
    print("\nSUCCESS! Here are your tokens:")
    print(f"Access Token: {data.get('access_token')}")
    print(f"Refresh Token: {data.get('refresh_token')}")
else:
    print(f"\nError {response.status_code}: {response.text}")
