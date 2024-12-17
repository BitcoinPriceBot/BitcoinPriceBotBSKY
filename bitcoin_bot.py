import requests
import os
import json
from datetime import datetime

def post_to_bluesky_direct(price):
    # Bluesky API-endepunkt og innlogging
    url = "https://bsky.social/xrpc/com.atproto.repo.createRecord"
    headers = {"Content-Type": "application/json"}

    # Hent tokens fra Secrets
    handle = os.getenv("BLUESKY_HANDLE")
    password = os.getenv("BLUESKY_PASSWORD")

    # Logg inn for å få auth token
    login_response = requests.post(
        "https://bsky.social/xrpc/com.atproto.server.createSession",
        json={"identifier": handle, "password": password},
    )
    if login_response.status_code == 200:
        access_token = login_response.json()["accessJwt"]
        headers["Authorization"] = f"Bearer {access_token}"
    else:
        print("Error logging in:", login_response.text)
        return

    # Post-innhold med hashtags riktig formatert
    content = {
        "repo": handle,
        "collection": "app.bsky.feed.post",
        "record": {
            "text": f"Bitcoin price: ${price:,}\n\n#btc #crypto #blockchain",
            "createdAt": datetime.now().isoformat(),
        },
    }

    # Send posten
    response = requests.post(url, headers=headers, json=content)
    if response.status_code == 200:
        print("Successfully posted to Bluesky!")
    else:
        print("Error posting:", response.text)
