import requests
import os
from datetime import datetime

def fetch_bitcoin_price():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd&include_24hr_change=true"
    response = requests.get(url)
    data = response.json()
    price = data["bitcoin"]["usd"]
    change = data["bitcoin"]["usd_24h_change"]
    return price, round(change, 2)

def post_to_bluesky(price, change):
    # Velger emoji basert på prisendring
    emoji = "📈" if change > 0 else "📉"

    # Formaterer posten
    content = f"{emoji} Bitcoin Price: ${price:,.0f} ({change:+.2f}%)\n\n#bitcoin #btc #crypto"

    print("Sending post content:")
    print(content)

    # Bluesky API-oppsett
    url = "https://bsky.social/xrpc/com.atproto.repo.createRecord"
    headers = {"Content-Type": "application/json"}

    handle = os.getenv("BLUESKY_HANDLE")
    password = os.getenv("BLUESKY_PASSWORD")

    # Logger inn og får token
    login_response = requests.post(
        "https://bsky.social/xrpc/com.atproto.server.createSession",
        json={"identifier": handle, "password": password}
    )

    if login_response.status_code == 200:
        access_token = login_response.json().get("accessJwt")
        headers["Authorization"] = f"Bearer {access_token}"
    else:
        print("Login failed:", login_response.text)
        return

    # Oppretter selve posten
    content_json = {
        "repo": handle,
        "collection": "app.bsky.feed.post",
        "record": {
            "text": content,
            "createdAt": datetime.now().isoformat() + "Z"
        }
    }

    post_response = requests.post(url, headers=headers, json=content_json)

    if post_response.status_code == 200:
        print("Successfully posted to Bluesky!")
    else:
        print("Error posting:", post_response.text)

if __name__ == "__main__":
    try:
        price, change = fetch_bitcoin_price()
        post_to_bluesky(price, change)
    except Exception as e:
        print("Error:", e)
