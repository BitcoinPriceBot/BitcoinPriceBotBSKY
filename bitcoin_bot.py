import requests
import os
from datetime import datetime

def fetch_bitcoin_price():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd&include_24hr_change=true"
    response = requests.get(url)
    data = response.json()

    try:
        price = data["bitcoin"]["usd"]
        change = data["bitcoin"]["usd_24h_change"]
        return price, round(change, 2)
    except KeyError:
        print("Error: Could not fetch price or change.")
        return None, None

def post_to_bluesky():
    url = "https://bsky.social/xrpc/com.atproto.repo.createRecord"
    headers = {"Content-Type": "application/json"}

    handle = os.getenv("BLUESKY_HANDLE")
    password = os.getenv("BLUESKY_PASSWORD")

    print(f"Using handle: {handle}")
    print("Starting login...")

    login_response = requests.post(
        "https://bsky.social/xrpc/com.atproto.server.createSession",
        json={"identifier": handle, "password": password},
    )

    if login_response.status_code == 200:
        access_token = login_response.json().get("accessJwt")
        headers["Authorization"] = f"Bearer {access_token}"
        print("Login successful.")
    else:
        print("Login failed:", login_response.text)
        return

    price, change = fetch_bitcoin_price()
    if price is None or change is None:
        print("Failed to fetch Bitcoin data.")
        return

    emoji = "📈" if change > 0 else "📉"

    text = f"{emoji} Bitcoin Price: ${price:,}\n📊 24h Change: {change}%\n\n#bitcoin #btc #crypto"

    # Dynamisk beregning av facetter
    facets = []
    hashtags = ["#bitcoin", "#btc", "#crypto"]

    for hashtag in hashtags:
        start = text.find(hashtag)
        end = start + len(hashtag)
        facets.append({
            "index": {"byteStart": start, "byteEnd": end},
            "features": [{"$type": "app.bsky.richtext.facet#link", "uri": f"https://bsky.app/hashtag/{hashtag[1:]}"}]
        })

    content = {
        "repo": handle,
        "collection": "app.bsky.feed.post",
        "record": {
            "text": text,
            "facets": facets,
            "createdAt": datetime.utcnow().isoformat() + "Z",
        },
    }

    print("Sending post...")
    response = requests.post(url, headers=headers, json=content)

    if response.status_code == 200:
        print("Successfully posted to Bluesky!")
    else:
        print("Error posting:", response.text)

def main():
    post_to_bluesky()

if __name__ == "__main__":
    main()
