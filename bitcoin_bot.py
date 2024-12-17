import requests
import os
from datetime import datetime

def get_bitcoin_price():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd&include_24hr_change=true"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        price = data['bitcoin']['usd']
        change = data['bitcoin']['usd_24h_change']
        return price, change
    else:
        print("Error fetching Bitcoin price:", response.status_code)
        return None, None

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

        # Generer post-innhold
        movement = "📈 Rising" if change > 0 else "📉 Dropping"
        content = {
            "repo": handle,
            "collection": "app.bsky.feed.post",
            "record": {
                "text": f"{movement}\n💵 Current price: USD ${price:,.2f}\n📊 24h Change: {change:.2f}%\n\n#Bitcoin #BTC #Crypto",
                "createdAt": datetime.now().isoformat()
            }
        }

        print("Attempting to send post...")
        response = requests.post(url, headers=headers, json=content)

        if response.status_code == 200:
            print("Successfully posted to Bluesky!")
        else:
            print("Error posting:", response.text)
    else:
        print("Login failed:", login_response.text)

if __name__ == "__main__":
    price, change = get_bitcoin_price()
    if price is not None and change is not None:
        post_to_bluesky(price, change)
