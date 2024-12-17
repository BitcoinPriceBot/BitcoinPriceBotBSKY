import requests
import os
from datetime import datetime

def fetch_bitcoin_price():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd&include_24hr_change=true"
    response = requests.get(url)
    data = response.json()

    try:
        price = data["bitcoin"]["usd"]
        change = round(data["bitcoin"]["usd_24h_change"], 2)
        return price, change
    except KeyError:
        print("Error: Could not fetch Bitcoin data.")
        return None, None

def generate_facets(text, tags):
    """Genererer facetter for hashtags som sikrer klikkbarhet."""
    facets = []
    for tag in tags:
        start = text.find(tag)
        end = start + len(tag)
        facets.append({
            "index": {"byteStart": start, "byteEnd": end},
            "features": [{"$type": "app.bsky.richtext.facet#tag", "tag": tag[1:]}]
        })
    return facets

def post_to_bluesky():
    url = "https://bsky.social/xrpc/com.atproto.repo.createRecord"
    headers = {"Content-Type": "application/json"}

    handle = os.getenv("BLUESKY_HANDLE")
    password = os.getenv("BLUESKY_PASSWORD")

    print(f"Using handle: {handle}")
    print("Starting login...")

    # Login request
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

    # Fetch Bitcoin price and change
    price, change = fetch_bitcoin_price()
    if price is None or change is None:
        print("Failed to fetch Bitcoin data.")
        return

    emoji = "📈" if change > 0 else "📉"
    hashtags = ["#bitcoin", "#btc", "#crypto"]
    text = f"{emoji} Bitcoin Price: ${price:,} ({change}%)\n\n{' '.join(hashtags)}"

    facets = generate_facets(text, hashtags)

    # Create content for Bluesky
    content = {
        "repo": handle,
        "collection": "app.bsky.feed.post",
        "record": {
            "text": text,
            "facets": facets,
            "createdAt": datetime.utcnow().isoformat() + "Z",
        },
    }

    # Send post
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
