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
        json={"identifier": handle, "password": password}
    )

    if login_response.status_code == 200:
        access_token = login_response.json().get("accessJwt")
        headers["Authorization"] = f"Bearer {access_token}"
        print("Login successful. Access token acquired.")
    else:
        print("Login failed:", login_response.text)
        return

    # Innhold til posten
    content = {
        "repo": handle,
        "collection": "app.bsky.feed.post",
        "record": {
            "text": f"📉 Bitcoin Price: ${price}\n📊 Change (24h): {change}%\n\n#bitcoin #btc #crypto",
            "createdAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        }
    }

    # Send posten til Bluesky
    print("Attempting to send post...")
    response = requests.post(url, headers=headers, json=content)
    print("Post response:", response.status_code, response.text)

    if response.status_code == 200:
        print("Successfully posted to Bluesky!")
    else:
        print("Error posting:", response.text)

# Hent Bitcoin-prisen og endringen
def fetch_bitcoin_data():
    print("Fetching Bitcoin price...")
    try:
        response = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd&include_24hr_change=true")
        if response.status_code == 200:
            data = response.json()["bitcoin"]
            price = data["usd"]
            change = round(data["usd_24h_change"], 2)
            print(f"Current Bitcoin Price: ${price}")
            print(f"24h Change: {change}%")
            return price, change
        else:
            print("Failed to fetch data:", response.text)
            return None, None
    except Exception as e:
        print("Error fetching data:", str(e))
        return None, None

# Hovedfunksjon
if __name__ == "__main__":
    price, change = fetch_bitcoin_data()
    if price and change is not None:
        post_to_bluesky(price, change)
    else:
        print("Could not fetch Bitcoin data. Exiting...")
