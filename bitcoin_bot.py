import requests
import os
import json
from datetime import datetime

def get_bitcoin_price_and_change():
    # Hent pris og 24-timers endring
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd&include_24hr_change=true"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()['bitcoin']
        price = data['usd']
        change_24h = data['usd_24h_change']
        return price, change_24h
    else:
        print("Error fetching Bitcoin price.")
        return None, None

def post_to_bluesky(price, change_24h):
    # Bestem retning og ikon basert på 24-timers endring
    if change_24h > 0:
        icon = "📈"
    elif change_24h < 0:
        icon = "📉"
    else:
        icon = "🔹"

    message = f"{icon} Bitcoin Price: ${price:,}\n📊 Change (24h): {change_24h:.2f}%\n\n#bitcoin #btc #crypto"

    # Bluesky API-innlogging
    url = "https://bsky.social/xrpc/com.atproto.repo.createRecord"
    headers = {"Content-Type": "application/json"}
    handle = os.getenv("BLUESKY_HANDLE")
    password = os.getenv("BLUESKY_PASSWORD")
    
    # Logg inn for å få token
    login_response = requests.post(
        "https://bsky.social/xrpc/com.atproto.server.createSession",
        json={"identifier": handle, "password": password}
    )
    if login_response.status_code == 200:
        access_token = login_response.json().get("accessJwt")
        headers["Authorization"] = f"Bearer {access_token}"
        print("Login successful. Access token acquired.")

        # Innhold til posten
        content = {
            "repo": handle,
            "collection": "app.bsky.feed.post",
            "record": {
                "text": message,
                "createdAt": datetime.now().isoformat()
            }
        }

        # Send posten
        response = requests.post(url, headers=headers, json=content)
        if response.status_code == 200:
            print("Successfully posted to Bluesky!")
        else:
            print("Error posting:", response.text)
    else:
        print("Login failed:", login_response.text)

def main():
    price, change_24h = get_bitcoin_price_and_change()
    if price is not None and change_24h is not None:
        post_to_bluesky(price, change_24h)

if __name__ == "__main__":
    main()
