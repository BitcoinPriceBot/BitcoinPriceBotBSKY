import requests
import os
import json
from datetime import datetime, timezone

def post_to_bluesky(price, change):
    # Bluesky API-endepunkt og innlogging
    url = "https://bsky.social/xrpc/com.atproto.repo.createRecord"
    headers = {"Content-Type": "application/json"}
    
    handle = os.getenv("BLUESKY_HANDLE")
    password = os.getenv("BLUESKY_PASSWORD")
    
    print(f"Using handle: {handle}")
    print("Starting login...")

    # Logg inn for å få en token
    login_response = requests.post(
        "https://bsky.social/xrpc/com.atproto.server.createSession",
        json={"identifier": handle, "password": password},
    )

    if login_response.status_code == 200:
        print("Login successful. Access token acquired.")
        access_token = login_response.json().get("accessJwt")
        headers["Authorization"] = f"Bearer {access_token}"
    else:
        print(f"Login failed: {login_response.text}")
        return

    # Lag riktig tidsstempel
    created_at = datetime.now(timezone.utc).isoformat()

    # Postens tekst
    text = (
        f"📈 Bitcoin Price: ${price:,.0f}\n"
        f"📊 24h Change: {change:.2f}%\n\n"
        "#bitcoin #btc #crypto"
    )

    # Facets for hashtags – Dette gjør dem klikkbare!
    facets = [
        {"index": {"byteStart": 53, "byteEnd": 61}, "features": [{"$type": "app.bsky.richtext.facet#tag", "tag": "bitcoin"}]},
        {"index": {"byteStart": 62, "byteEnd": 66}, "features": [{"$type": "app.bsky.richtext.facet#tag", "tag": "btc"}]},
        {"index": {"byteStart": 67, "byteEnd": 74}, "features": [{"$type": "app.bsky.richtext.facet#tag", "tag": "crypto"}]},
    ]

    # Innhold til posten
    content = {
        "repo": handle,
        "collection": "app.bsky.feed.post",
        "record": {
            "text": text,
            "facets": facets,
            "createdAt": created_at,
        },
    }

    # Send posten til Bluesky
    response = requests.post(url, headers=headers, json=content)

    if response.status_code == 200:
        print("Successfully posted to Bluesky!")
    else:
        print(f"Error posting: {response.text}")

def main():
    # Eksempeldata
    bitcoin_price = 106956
    change_percentage = 3.18

    post_to_bluesky(bitcoin_price, change_percentage)

if __name__ == "__main__":
    main()
