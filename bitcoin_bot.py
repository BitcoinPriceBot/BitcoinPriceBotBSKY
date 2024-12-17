import requests
import os
import json
from datetime import datetime

def post_to_bluesky(price, change):
    url = "https://bsky.social/xrpc/com.atproto.repo.createRecord"
    headers = {"Content-Type": "application/json"}

    handle = os.getenv("BLUESKY_HANDLE")
    password = os.getenv("BLUESKY_PASSWORD")

    print(f"Using handle: {handle}")
    print("Starting login...")

    # Login for å få token
    login_response = requests.post(
        "https://bsky.social/xrpc/com.atproto.server.createSession",
        json={"identifier": handle, "password": password},
    )
    
    if login_response.status_code == 200:
        access_token = login_response.json().get("accessJwt")
        headers["Authorization"] = f"Bearer {access_token}"
        print("Login successful. Access token acquired.")
    else:
        print(f"Login failed: {login_response.text}")
        return

    # Innhold til posten
    content = {
        "repo": handle,
        "collection": "app.bsky.feed.post",
        "record": {
            "text": f"📉 Bitcoin Price: ${price:,}\n📊 24h Change: {change}%\n\n#bitcoin #btc #crypto",
            "createdAt": datetime.now().isoformat()
        }
    }

    # Forsøker å sende posten
    print("Attempting to send post...")
    response = requests.post(url, headers=headers, json=content)
    print("Post response:", response.status_code, response.text)

    if response.status_code == 200:
        print("Successfully posted to Bluesky!")
    else:
        print(f"Error posting: {response.text}")

def main():
    # Eksempeldata for testing (kan byttes med live API)
    bitcoin_price = 106956
    bitcoin_change = 3.18
    post_to_bluesky(bitcoin_price, bitcoin_change)

if __name__ == "__main__":
    main()
