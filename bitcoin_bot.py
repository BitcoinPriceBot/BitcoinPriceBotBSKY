import requests
import os
import json
from datetime import datetime

def fetch_bitcoin_data():
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids": "bitcoin",
        "vs_currencies": "usd",
        "include_24hr_change": "true"
    }
    response = requests.get(url, params=params)
    data = response.json()
    price = data["bitcoin"]["usd"]
    change = round(data["bitcoin"]["usd_24h_change"], 2)
    return price, change

def post_to_bluesky():
    # Fetch updated Bitcoin data
    price, change = fetch_bitcoin_data()

    # Bluesky API details
    url = "https://bsky.social/xrpc/com.atproto.repo.createRecord"
    headers = {"Content-Type": "application/json"}
    handle = os.getenv("BLUESKY_HANDLE")
    password = os.getenv("BLUESKY_PASSWORD")

    # Login to get access token
    login_response = requests.post(
        "https://bsky.social/xrpc/com.atproto.server.createSession",
        json={"identifier": handle, "password": password}
    )
    access_token = login_response.json().get("accessJwt")

    # Post content
    headers["Authorization"] = f"Bearer {access_token}"
    content = {
        "repo": handle,
        "collection": "app.bsky.feed.post",
        "record": {
            "text": f"📉 Bitcoin Price: ${price:,}\n📊 24h Change: {change}%\n\n#bitcoin #btc #crypto",
            "createdAt": datetime.utcnow().isoformat() + "Z"
        }
    }

    response = requests.post(url, headers=headers, json=content)
    if response.status_code == 200:
        print("Successfully posted to Bluesky!")
    else:
        print("Error posting:", response.text)

if __name__ == "__main__":
    post_to_bluesky()
