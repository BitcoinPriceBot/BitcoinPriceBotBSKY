import requests
import os
import json
from datetime import datetime, timezone

# Fetch Bitcoin price and 24h change from CoinGecko API
def fetch_bitcoin_price():
    response = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd&include_24hr_change=true")
    data = response.json()
    price = data["bitcoin"]["usd"]
    change = data["bitcoin"]["usd_24h_change"]
    return price, change

# Post to Bluesky
def post_to_bluesky(price, change):
    # Determine emoji based on price movement
    emoji = "📈" if change > 0 else "📉"
    change_formatted = f"{change:.2f}%"
    price_formatted = f"${price:,.0f}"

    # Final message text
    message = (
        f"{emoji} Bitcoin Price: {price_formatted} ({change_formatted})\n\n"
        "#bitcoin #btc #crypto"
    )
    
    print("Final message being sent to Bluesky:")
    print(message)

    # Login details
    handle = os.getenv("BLUESKY_HANDLE")
    password = os.getenv("BLUESKY_PASSWORD")
    
    login_response = requests.post(
        "https://bsky.social/xrpc/com.atproto.server.createSession",
        json={"identifier": handle, "password": password}
    )

    if login_response.status_code != 200:
        print("Login failed:", login_response.text)
        return

    access_token = login_response.json().get("accessJwt")
    headers = {"Authorization": f"Bearer {access_token}"}

    # Post message to Bluesky
    post_data = {
        "repo": handle,
        "collection": "app.bsky.feed.post",
        "record": {
            "text": message,
            "createdAt": datetime.now(timezone.utc).isoformat()
        }
    }

    response = requests.post(
        "https://bsky.social/xrpc/com.atproto.repo.createRecord",
        headers=headers,
        json=post_data
    )

    if response.status_code == 200:
        print("Successfully posted to Bluesky!")
    else:
        print("Error posting:", response.text)

# Main function
if __name__ == "__main__":
    print("Fetching Bitcoin price...")
    price, change = fetch_bitcoin_price()
    print("Starting login...")
    post_to_bluesky(price, change)
