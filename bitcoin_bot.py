import requests
import os
import json
from datetime import datetime, timezone

def fetch_bitcoin_price():
    # Hent bitcoin-pris og 24t endring fra CoinGecko API
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {"ids": "bitcoin", "vs_currencies": "usd", "include_24hr_change": "true"}
    response = requests.get(url)
    data = response.json()
    price = data["bitcoin"]["usd"]
    change = round(data["bitcoin"]["usd_24h_change"], 2)
    return price, change

def post_to_bluesky():
    # Hent pris og prosentendring
    price, change = fetch_bitcoin_price()

    # Bygg posten med riktig format og hashtags
    text = (
        f"📉 Bitcoin Price: ${price:,.0f}\n"
        f"📊 24h Change: {change}%\n\n"
        "#bitcoin #btc #crypto"
    )

    # Bluesky API-endepunkt
    url = "https://bsky.social/xrpc/com.atproto.repo.createRecord"
    handle = os.getenv("BLUESKY_HANDLE")
    password = os.getenv("BLUESKY_PASSWORD")

    # Login for å få access token
    login_response = requests.post(
        "https://bsky.social/xrpc/com.atproto.server.createSession",
        json={"identifier": handle, "password": password},
    )
    access_token = login_response.json().get("accessJwt")

    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    content = {
        "repo": handle,
        "collection": "app.bsky.feed.post",
        "record": {
            "text": text,
            "createdAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "facets": [
                {"index": {"byteStart": 60, "byteEnd": 68}, "features": [{"$type": "app.bsky.richtext.facet#link", "uri": "#bitcoin"}]},
                {"index": {"byteStart": 69, "byteEnd": 73}, "features": [{"$type": "app.bsky.richtext.facet#link", "uri": "#btc"}]},
                {"index": {"byteStart": 74, "byteEnd": 81}, "features": [{"$type": "app.bsky.richtext.facet#link", "uri": "#crypto"}]},
            ],
        },
    }

    # Forsøk å poste
    response = requests.post(url, headers=headers, json=content)
    if response.status_code == 200:
        print("Postet vellykket til Bluesky!")
    else:
        print(f"Feil ved posting: {response.text}")

if __name__ == "__main__":
    post_to_bluesky()
