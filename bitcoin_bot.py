import requests
import os
from datetime import datetime

# Hent Bitcoin-pris og prosentendring fra CoinGecko
def fetch_bitcoin_price():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd&include_24hr_change=true"
    response = requests.get(url)
    data = response.json()
    price = data["bitcoin"]["usd"]
    change = data["bitcoin"]["usd_24h_change"]
    return price, round(change, 2)

# Post til Bluesky
def post_to_bluesky():
    handle = os.getenv("BLUESKY_HANDLE")
    password = os.getenv("BLUESKY_PASSWORD")
    
    price, change = fetch_bitcoin_price()

    # Velg emoji basert på endring
    if change > 0:
        emoji = "📈"
    elif change < 0:
        emoji = "📉"
    else:
        emoji = "📊"

    # Formater meldingen med sikre mellomrom og korrekte hashtags
    message = (
        f"{emoji} Bitcoin Price: ${price:,} ({change:+.2f}%)\n\n"
        f"#bitcoin #btc #crypto"
    )

    print("Sending post...")
    
    # Logg inn og hent access token
    login_response = requests.post(
        "https://bsky.social/xrpc/com.atproto.server.createSession",
        json={"identifier": handle, "password": password},
    )
    
    if login_response.status_code != 200:
        print("Login failed:", login_response.text)
        return
    
    access_token = login_response.json().get("accessJwt")
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    
    # Send posten til Bluesky
    content = {
        "repo": handle,
        "collection": "app.bsky.feed.post",
        "record": {
            "text": message,
            "createdAt": datetime.now().isoformat() + "Z",
        }
    }
    
    post_response = requests.post(
        "https://bsky.social/xrpc/com.atproto.repo.createRecord",
        headers=headers,
        json=content,
    )

    if post_response.status_code == 200:
        print("Successfully posted to Bluesky!")
    else:
        print("Error posting:", post_response.text)

if __name__ == "__main__":
    post_to_bluesky()
