import requests
import os
from datetime import datetime

def get_bitcoin_data():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd&include_24hr_change=true"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        price = data['bitcoin']['usd']
        change = round(data['bitcoin']['usd_24h_change'], 2)
        return price, change
    else:
        print("Error fetching Bitcoin data")
        return None, None

def post_to_bluesky(price, change):
    handle = os.getenv("BLUESKY_HANDLE")
    password = os.getenv("BLUESKY_PASSWORD")

    print(f"Using handle: {handle}")
    print("Starting login...")

    # Authenticate with Bluesky
    login_response = requests.post(
        "https://bsky.social/xrpc/com.atproto.server.createSession",
        json={"identifier": handle, "password": password}
    )

    if login_response.status_code == 200:
        access_token = login_response.json().get("accessJwt")
        headers = {"Authorization": f"Bearer {access_token}"}

        # Build the content
        text = f"📉 Bitcoin Price: ${price:,.2f}\n📊 Change (24h): {change}%\n\n#bitcoin #btc #crypto"

        content = {
            "repo": handle,
            "collection": "app.bsky.feed.post",
            "record": {
                "text": text,
                "createdAt": datetime.now().isoformat()
            }
        }

        print("Attempting to send post...")
        post_response = requests.post(
            "https://bsky.social/xrpc/com.atproto.repo.createRecord",
            headers=headers, json=content
        )

        if post_response.status_code == 200:
            print("Successfully posted to Bluesky!")
        else:
            print("Error posting:", post_response.text)
    else:
        print("Login failed:", login_response.text)

if __name__ == "__main__":
    bitcoin_price, price_change = get_bitcoin_data()
    if bitcoin_price is not None and price_change is not None:
        post_to_bluesky(bitcoin_price, price_change)
