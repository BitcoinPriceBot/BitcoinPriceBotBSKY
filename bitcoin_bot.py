import requests
import os
import json
from datetime import datetime

def post_to_bluesky_direct(price, change):
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

    # Bestem om endringen er positiv eller negativ
    sign = "+" if change >= 0 else ""
    text = f"Bitcoin Price: ${price:,} ({sign}{change:.2f}%)\n\n#bitcoin #btc #crypto"
    facets = [
        {"index": {"byteStart": text.index("#bitcoin"), "byteEnd": text.index("#bitcoin") + 8}, "features": [{"$type": "app.bsky.richtext.facet#tag", "tag": "bitcoin"}]},
        {"index": {"byteStart": text.index("#btc"), "byteEnd": text.index("#btc") + 4}, "features": [{"$type": "app.bsky.richtext.facet#tag", "tag": "btc"}]},
        {"index": {"byteStart": text.index("#crypto"), "byteEnd": text.index("#crypto") + 7}, "features": [{"$type": "app.bsky.richtext.facet#tag", "tag": "crypto"}]},
    ]

    # Innhold til posten med facets
    content = {
        "repo": handle,
        "collection": "app.bsky.feed.post",
        "record": {
            "text": text,
            "facets": facets,
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
    # Hent Bitcoin-prisen og prosentendring fra CoinGecko
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd&include_24hr_change=true"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()["bitcoin"]
        price = data["usd"]
        change = data["usd_24h_change"]
        print(f"Current Bitcoin Price: ${price:,}, Change: {change:.2f}%")
        post_to_bluesky_direct(price, change)
    else:
        print("Error fetching Bitcoin price:", response.text)

if __name__ == "__main__":
    main()
