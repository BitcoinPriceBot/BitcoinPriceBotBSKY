import requests
import os
import json
from datetime import datetime, timezone

# Hent Bitcoin-pris og 24-timers endring fra CoinGecko
def fetch_bitcoin_price():
    response = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd&include_24hr_change=true")
    data = response.json()
    price = data["bitcoin"]["usd"]
    change = data["bitcoin"]["usd_24h_change"]
    return price, change

# Post til Bluesky med klikkbare hashtags
def post_to_bluesky(price, change):
    # Velg emoji basert på prisendring
    emoji = "📈" if change > 0 else "📉"
    price_formatted = f"${price:,.0f}"
    change_formatted = f"{change:.2f}%"

    # Tekst til posten
    text = f"{emoji} Bitcoin Price: {price_formatted} ({change_formatted})\n\n#bitcoin #btc #crypto"
    print("Final message being sent to Bluesky:")
    print(text)

    # Definer facets for klikkbare hashtags
    facets = [
        {"index": {"byteStart": text.index("#bitcoin"), "byteEnd": text.index("#bitcoin") + 8}, "features": [{"$type": "app.bsky.richtext.facet#tag", "tag": "bitcoin"}]},
        {"index": {"byteStart": text.index("#btc"), "byteEnd": text.index("#btc") + 4}, "features": [{"$type": "app.bsky.richtext.facet#tag", "tag": "btc"}]},
        {"index": {"byteStart": text.index("#crypto"), "byteEnd": text.index("#crypto") + 7}, "features": [{"$type": "app.bsky.richtext.facet#tag", "tag": "crypto"}]},
    ]

    # Bluesky innlogging og API-endepunkt
    handle = os.getenv("BLUESKY_HANDLE")
    password = os.getenv("BLUESKY_PASSWORD")
    url = "https://bsky.social/xrpc/com.atproto.repo.createRecord"
    headers = {"Content-Type": "application/json"}

    # Logg inn for å få tilgangstoken
    login_response = requests.post(
        "https://bsky.social/xrpc/com.atproto.server.createSession",
        json={"identifier": handle, "password": password},
    )

    if login_response.status_code == 200:
        access_token = login_response.json().get("accessJwt")
        headers["Authorization"] = f"Bearer {access_token}"
        print("Login successful. Access token acquired.")
    else:
        print("Login failed:", login_response.text)
        return

    # Send posten med facets for hashtags
    content = {
        "repo": handle,
        "collection": "app.bsky.feed.post",
        "record": {
            "text": text,
            "facets": facets,
            "createdAt": datetime.now(timezone.utc).isoformat()
        },
    }

    print("Sending post to Bluesky...")
    response = requests.post(url, headers=headers, json=content)

    if response.status_code == 200:
        print("Successfully posted to Bluesky!")
    else:
        print("Error posting:", response.text)

# Hovedfunksjon
if __name__ == "__main__":
    print("Fetching Bitcoin price...")
    price, change = fetch_bitcoin_price()
    print("Starting Bluesky bot...")
    post_to_bluesky(price, change)
