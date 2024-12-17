import requests
import os
from datetime import datetime

def fetch_bitcoin_price():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd&include_24hr_change=true"
    response = requests.get(url)
    data = response.json()
    price = data["bitcoin"]["usd"]
    change = data["bitcoin"]["usd_24h_change"]
    return price, change

def post_to_bluesky(price, change):
    # Velg emoji basert på endringen
    if change > 0:
        emoji = "📈"
    elif change < 0:
        emoji = "📉"
    else:
        emoji = "📊"

    # Formater meldingen med linjeskift før hashtags
    message = (
        f"{emoji} Bitcoin Price: ${price:,.0f} ({change:.2f}%)\n\n"
        "#bitcoin #btc #crypto"
    )

    # Bluesky API-endepunkt og innlogging
    url = "https://bsky.social/xrpc/com.atproto.repo.createRecord"
    headers = {"Content-Type": "application/json"}
    handle = os.getenv("BLUESKY_HANDLE")
    password = os.getenv("BLUESKY_PASSWORD")

    print("Starting login...")
    login_response = requests.post(
        "https://bsky.social/xrpc/com.atproto.server.createSession",
        json={"identifier": handle, "password": password}
    )

    if login_response.status_code == 200:
        access_token = login_response.json().get("accessJwt")
        headers["Authorization"] = f"Bearer {access_token}"
        print("Login successful. Sending post...")

        content = {
            "repo": handle,
            "collection": "app.bsky.feed.post",
            "record": {
                "text": message,
                "createdAt": datetime.now().isoformat() + "Z"
            }
        }

        post_response = requests.post(url, headers=headers, json=content)

        if post_response.status_code == 200:
            print("Successfully posted to Bluesky!")
        else:
            print("Error posting:", post_response.text)
    else:
        print("Login failed:", login_response.text)

if __name__ == "__main__":
    print("Fetching Bitcoin price...")
    price, change = fetch_bitcoin_price()
    post_to_bluesky(price, change)
