import requests
import os
import json
from datetime import datetime

def fetch_bitcoin_price():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd&include_24hr_change=true"
    response = requests.get(url)
    data = response.json()
    price = data["bitcoin"]["usd"]
    change = data["bitcoin"]["usd_24h_change"]
    return price, change

def post_to_bluesky(price, change):
    handle = os.getenv("BLUESKY_HANDLE")
    password = os.getenv("BLUESKY_PASSWORD")

    print("Starting login...")
    login_response = requests.post(
        "https://bsky.social/xrpc/com.atproto.server.createSession",
        json={"identifier": handle, "password": password}
    )
    if login_response.status_code != 200:
        print("Login failed:", login_response.text)
        return

    access_token = login_response.json().get("accessJwt")
    headers = {"Authorization": f"Bearer {access_token}"}
    print("Login successful.")

    # Emoji for price movement
    emoji = "📉" if change < 0 else "📈"
    formatted_price = f"${price:,.0f}"
    formatted_change = f"{change:.2f}%"

    # Post content: ensuring line breaks and spaces
    content = (
        f"{emoji} Bitcoin Price: {formatted_price} ({formatted_change})\n\n"
        f"#bitcoin #btc #crypto"
    )

    print("Sending post...")
    post_data = {
        "repo": handle,
        "collection": "app.bsky.feed.post",
        "record": {
            "text": content,
            "createdAt": datetime.now().isoformat() + "Z"
        }
    }

    post_response = requests.post(
        "https://bsky.social/xrpc/com.atproto.repo.createRecord",
        headers=headers, json=post_data
    )

    if post_response.status_code == 200:
        print("Successfully posted to Bluesky!")
    else:
        print("Error posting:", post_response.text)

def main():
    price, change = fetch_bitcoin_price()
    post_to_bluesky(price, change)

if __name__ == "__main__":
    main()
