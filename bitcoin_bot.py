import requests
import os
import json
from datetime import datetime

def post_to_bluesky_direct(price):
    # Bluesky API-endepunkt og innlogging
    url = "https://bsky.social/xrpc/com.atproto.repo.createRecord"
    headers = {"Content-Type": "application/json"}

    handle = os.getenv("BLUESKY_HANDLE")
    password = os.getenv("BLUESKY_PASSWORD")

    print(f"Using handle: {handle}")
    print("Starting login...")

    # Logg inn for å få token
    login_response = requests.post(
        "https://bsky.social/xrpc/com.atproto.server.createSession",
        json={"identifier": handle, "password": password},
    )
    print("Login response:", login_response.status_code, login_response.text)

    if login_response.status_code == 200:
        access_token = login_response.json().get("accessJwt")
        headers["Authorization"] = f"Bearer {access_token}"
        print("Login successful. Access token acquired.")
    else:
        print("Login failed:", login_response.text)
        return

    # Innhold til posten med riktig `createdAt`-format
    content = {
        "repo": handle,
        "collection": "app.bsky.feed.post",
        "record": {
            "text": f"Bitcoin price: ${price:,}\n\n#btc #crypto #blockchain",
            "createdAt": datetime.now().isoformat(timespec="seconds") + "Z",
        },
    }

    print("Attempting to send post...")
    response = requests.post(url, headers=headers, json=content)
    print("Post response:", response.status_code, response.text)

    if response.status_code == 200:
        print("Successfully posted to Bluesky!")
    else:
        print("Error posting:", response.text)

def main():
    # Hent Bitcoin-prisen fra CoinGecko
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
    response = requests.get(url)

    if response.status_code == 200:
        price = response.json()["bitcoin"]["usd"]
        print(f"Current Bitcoin Price: ${price:,}")
        post_to_bluesky_direct(price)
    else:
        print("Error fetching Bitcoin price:", response.text)

if __name__ == "__main__":
    main()
