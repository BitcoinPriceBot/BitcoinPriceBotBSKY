import requests
import os
import json
from datetime import datetime, timezone

def post_to_bluesky(price, change):
    # Bluesky API-endepunkt og nødvendige data
    url = "https://bsky.social/xrpc/com.atproto.repo.createRecord"
    headers = {"Content-Type": "application/json"}

    # Henter miljøvariabler for innlogging
    handle = os.getenv("BLUESKY_HANDLE")
    password = os.getenv("BLUESKY_PASSWORD")
    
    print(f"Using handle: {handle}")
    print("Starting login...")

    # Trinn 1: Logg inn for å få en token
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

    # Trinn 2: Innhold til posten
    created_at = datetime.now(timezone.utc).isoformat()  # Riktig ISO 8601 format for tidsstempel
    content = {
        "repo": handle,
        "collection": "app.bsky.feed.post",
        "record": {
            "text": (
                f"📈 Bitcoin Price: ${price:,.0f}\n"
                f"📊 24h Change: {change:.2f}%\n\n"
                "#bitcoin #btc #crypto"
            ),
            "createdAt": created_at,
        },
    }

    # Debug: Skriv ut innholdet som sendes til Bluesky
    print("DEBUG: Content being sent to Bluesky:")
    print(json.dumps(content, indent=2))

    # Trinn 3: Send posten til Bluesky
    response = requests.post(url, headers=headers, json=content)

    if response.status_code == 200:
        print("Successfully posted to Bluesky!")
    else:
        print(f"Error posting: {response.text}")

def main():
    # Dummydata for testing
    bitcoin_price = 106956  # Eksempelpris
    change_percentage = 3.18  # Eksempelprosent

    # Kall funksjonen for å poste til Bluesky
    post_to_bluesky(bitcoin_price, change_percentage)

if __name__ == "__main__":
    main()
