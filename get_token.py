import requests
import os
from dotenv import load_dotenv

load_dotenv()

client_id = os.getenv("STRAVA_CLIENT_ID")
client_secret = os.getenv("STRAVA_CLIENT_SECRET")

code = "ec2dc1ac7e4ed2d018d5cd42a64599248574509a"

url = "https://www.strava.com/oauth/token"

payload = {
    "client_id": client_id,
    "client_secret": client_secret,
    "code": code,
    "grant_type": "authorization_code"
}

res = requests.post(url, data=payload)
data = res.json()

print(data)