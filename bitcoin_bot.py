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

    # Formatere pris og endring
    formatted_price = f"${int(price):,}"  # Tusenskilletegn og ingen desimaler
    formatted_change = f"{change:.2f}%"

    # Tekstinnholdet
    text = (
        f"Bitcoin Price: {formatted_price}\n"
        f"24h Change: {formatted_change}\n\n"
        "#bitcoin #btc #crypto"
    )

    # Beregn posisjon for hashtags
    hashtags = ["#bitcoin", "#btc", "#crypto"]
    facets = []
    for tag in hashtags:
        start = text.find(tag)
        end = start + len(tag)
        facets.append({
            "index": {"byteStart": start, "byteEnd": end},
            "features": [{"$type": "app.bsky.richtext.facet#link", "uri": f"https://bsky.app/tag/{tag[1:]}"}]
        })

    # Innhold til posten
    content = {
        "repo": handle,
        "collection": "app.bsky.feed.post",
        "record": {
            "text": text,
            "facets": facets,
            "createdAt": date
