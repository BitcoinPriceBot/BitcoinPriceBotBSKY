import requests
import os
import json
from datetime import datetime

def fetch_bitcoin_price():
    # Hent Bitcoin-prisen fra CoinGecko
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd&include_24hr_change=true"
    response = requests.get(url)
    data = response.json()
    price = data["bitcoin"]["usd"]
    change = data["bitcoin"]["usd_24h_change"]
    return price, change

def post_to_bluesky():
    # Hent pris og endring
    price, change = fetch_bitcoin_price()

    # Velg emoji basert på endringen
    emoji = "📉" if change < 0 else "📈"

    # Formater meldingen med korrekt mellomrom og hashtags
    message = f"{emoji} Bitcoin Price: ${price:,.0f} ({change:.2f}%)\n\n#bitcoin #btc #crypto"

    # Skriv ut meldingen før den sendes
    print("Final message being sent to Bluesky:")
    print(repr(message))  # Bruk repr for å vise skjulte tegn

    # Bluesky API-innstillinger
    url = "https://bsky.social/xrpc/com.atproto.repo.createRecord"
    headers = {"Content-Type": "application/json"}
    handle = os.getenv("BLUESKY_HANDLE")
    password = os.getenv("BLUESKY_PASSWORD")

    # Logg inn og hent access token
    login_response = requests.post(
        "https://bsky.social/xrpc/com.atproto.server.createSession",
        json={"identifier": handle, "password": password},
    )
    access_token = login_response.json().get("accessJwt")
    headers["Authorization"] = f"Bearer {access_token}"

    # Opprett posten
    content = {
        "repo": handle,
        "collection": "app.bsky.feed.post",
        "record": {
            "text": message,
            "createdAt": datetime.utcnow().isoformat() + "Z",
        },
    }

    # Send posten
    response = requests.post(url, headers=headers, json=content)

    # Skriv ut respons fra API
    print("Response status code:", response.status_code)
    print("Response text:", response.text)

    if response.status_code == 200:
        print("Successfully posted to Bluesky!")
    else:
        print("Error posting:", response.text)

if __name__ == "__main__":
    post_to_bluesky()
