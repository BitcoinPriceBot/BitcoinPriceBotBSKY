import requests
import os
from datetime import datetime

def get_bitcoin_price():
    """
    Henter Bitcoin-prisen fra CoinGecko API og beregner 24-timers prosentendring.
    """
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd&include_24hr_change=true"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        price = data["bitcoin"]["usd"]
        change = data["bitcoin"]["usd_24h_change"]
        return price, round(change, 2)
    else:
        print("Error fetching Bitcoin price:", response.status_code)
        return None, None

def post_to_bluesky(price, change):
    """
    Poster Bitcoin-prisen og prosentendringen til Bluesky.
    """
    # BLUESKY-login
    handle = os.getenv("BLUESKY_HANDLE")
    password = os.getenv("BLUESKY_PASSWORD")
    url_login = "https://bsky.social/xrpc/com.atproto.server.createSession"

    print(f"Logging in with handle: {handle}")
    login_response = requests.post(url_login, json={"identifier": handle, "password": password})
    
    if login_response.status_code == 200:
        print("Login successful!")
        access_token = login_response.json().get("accessJwt")

        # Formaterer posten basert på endring i prisen
        if change > 0:
            trend = "📈 Bitcoin is rising!"
        elif change < 0:
            trend = "📉 Bitcoin is slipping."
        else:
            trend = "🔍 Bitcoin price remains stable."

        message = (
            f"{trend}\n\n"
            f"💲 Current price: ${price:,.2f}\n"
            f"📊 24h Change: {change}%\n\n"
            f"#bitcoin #btc #crypto"
        )

        # Send posten til Bluesky
        headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
        url_post = "https://bsky.social/xrpc/com.atproto.repo.createRecord"

        post_data = {
            "repo": handle,
            "collection": "app.bsky.feed.post",
            "record": {
                "text": message,
                "createdAt": datetime.utcnow().isoformat() + "Z"
            }
        }

        response = requests.post(url_post, headers=headers, json=post_data)
        if response.status_code == 200:
            print("Post successfully sent to Bluesky!")
        else:
            print("Error posting:", response.text)
    else:
        print("Login failed:", login_response.text)

def main():
    price, change = get_bitcoin_price()
    if price is not None and change is not None:
        post_to_bluesky(price, change)
    else:
        print("Could not retrieve Bitcoin price.")

if __name__ == "__main__":
    main()
