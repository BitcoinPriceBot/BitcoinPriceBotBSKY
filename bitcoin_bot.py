import requests
import os
from datetime import datetime

def fetch_bitcoin_price():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd&include_24hr_change=true"
    response = requests.get(url)
    data = response.json()

    # Henter pris og 24-timers endring
    try:
        price = data["bitcoin"]["usd"]
        change = data["bitcoin"]["usd_24h_change"]
        return price, round(change, 2)
    except KeyError:
        print("Error: Could not fetch price or change.")
        print("API Response:", data)
        return None, None

def post_to_bluesky():
    # Logger inn i Bluesky API
    url = "https://bsky.social/xrpc/com.atproto.repo.createRecord"
    headers = {"Content-Type": "application/json"}

    handle = os.getenv("BLUESKY_HANDLE")
    password = os.getenv("BLUESKY_PASSWORD")

    print(f"Using handle: {handle}")
    print("Starting login...")

    # Henter en access token
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

    # Henter Bitcoin data
    price, change = fetch_bitcoin_price()
    if price is None or change is None:
        print("Failed to fetch Bitcoin data.")
        return

    # Velger emoji basert på endring
    emoji = "📈" if change > 0 else "📉"

    # Oppretter innhold til posten
    content = {
        "repo": handle,
        "collection": "app.bsky.feed.post",
        "record": {
            "text": f"{emoji} Bitcoin Price: ${price:,}\n📊 24h Change: {change}%\n\n#bitcoin #btc #crypto",
            "createdAt": datetime.utcnow().isoformat() + "Z",
        },
    }

    print("Attempting to send post...")
    response = requests.post(url, headers=headers, json=content)

    if response.status_code == 200:
        print("Successfully posted to Bluesky!")
    else:
        print("Error posting:", response.text)

def main():
    post_to_bluesky()

if __name__ == "__main__":
    main()
