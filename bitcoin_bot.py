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

    # Logg inn for å få token
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

    # Formatere prisen med tusenskilletegn
    formatted_price = f"${int(price):,}"  # Konverterer til int for å fjerne cent og legger til komma

    # Velge riktig emoji for prisendring
    direction = "📈" if change > 0 else "📉" if change < 0 else "➖"

    # Teksten til posten
    text = (
        f"{direction} Bitcoin Price: {formatted_price}\n"
        f"📊 24h Change: {change:.2f}%\n\n"
        "#bitcoin#btc#crypto"  # Ingen mellomrom her
    )

    # Dynamisk beregne posisjon for hashtags
    bitcoin_pos = text.index("#bitcoin")
    btc_pos = text.index("#btc")
    crypto_pos = text.index("#crypto")

    # Definer facets for hashtags
    facets = [
        {
            "index": {"byteStart": bitcoin_pos, "byteEnd": bitcoin_pos + len("#bitcoin")},
            "features": [{"$type": "app.bsky.richtext.facet#link", "uri": "https://bsky.app/tag/bitcoin"}],
        },
        {
            "index": {"byteStart": btc_pos, "byteEnd": btc_pos + len("#btc")},
            "features": [{"$type": "app.bsky.richtext.facet#link", "uri": "https://bsky.app/tag/btc"}],
        },
        {
            "index": {"byteStart": crypto_pos, "byteEnd": crypto_pos + len("#crypto")},
            "features": [{"$type": "app.bsky.richtext.facet#link", "uri": "https://bsky.app/tag/crypto"}],
        },
    ]

    # Innhold til posten
    content = {
        "repo": handle,
        "collection": "app.bsky.feed.post",
        "record": {
            "text": text,
            "facets": facets,  # Legger til facets for hashtags
            "createdAt": datetime.now(timezone.utc).isoformat(),
        },
    }

    # Forsøke å sende post
    print("Attempting to send post...")
    response = requests.post(url, headers=headers, json=content)

    if response.status_code == 200:
        print("Successfully posted to Bluesky!")
    else:
        print("Error posting:", response.text)

# Eksempel for testing
if __name__ == "__main__":
    bitcoin_price = 106956  # Eksempelverdi
    change_24h = 3.18  # Eksempelverdi
    post_to_bluesky(bitcoin_price, change_24h)
