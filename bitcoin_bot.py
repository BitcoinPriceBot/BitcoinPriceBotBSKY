from datetime import datetime, timezone

def post_to_bluesky_direct(price, change):
    import requests
    import os
    import json

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

    # Tidsformat i ISO-8601 (UTC)
    created_at = datetime.now(timezone.utc).isoformat()

    # Innhold til posten
    content = {
        "repo": handle,
        "collection": "app.bsky.feed.post",
        "record": {
            "text": f"📈 Bitcoin Price: ${price:,.0f}\n📊 24h Change: {change:.2f}%\n\n#bitcoin #btc #crypto",
            "createdAt": created_at,
        },
    }

    # Forsøk å sende post
    print("Attempting to send post...")
    response = requests.post(url, headers=headers, json=content)
    print("Post response:", response.status_code, response.text)

    if response.status_code == 200:
        print("Successfully posted to Bluesky!")
    else:
        print("Error posting:", response.text)
