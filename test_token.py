import os
import requests
from dotenv import load_dotenv

# We load the .env file
load_dotenv()

# We read the token and apply .strip() in case there's any invisible whitespace when copying
token = os.getenv("MELI_ACCESS_TOKEN")

if not token:
    print(
        "ERROR: Python not found the .env file or the variable MELI_ACCESS_TOKEN is empty."
    )
    exit()

# We clean the token of invisible spaces or line breaks
token = token.strip()
print(f"Testing token that starts with: {token[:12]}...")

# We will consult the /users/me endpoint, which returns the data of the token owner
url = "https://api.mercadolibre.com/users/me"
headers = {"Authorization": f"Bearer {token}"}

response = requests.get(url, headers=headers)

print(f"\nStatus Code of response: {response.status_code}")

if response.status_code == 200:
    print("¡SUCCESSFULL! Your token is 100% valid and works perfectly.")
    print("The problem is in the search endpoint (MLA1055).")
else:
    print("TOKEN ERROR: Mercado Libre returned an error.")
    print(f"Error detail: {response.text}")
