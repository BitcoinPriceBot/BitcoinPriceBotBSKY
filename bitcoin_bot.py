import requests
import os
import json
from datetime import datetime

def fetch_bitcoin_data():
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {"ids": "bitcoin", "vs_currencies": "usd", "include_24hr_change": "true"}
    response = requests.get(url, params=params)
    data = response.json()
    price = data["bitcoin"]["usd"]
    change = round(data["bitcoin"]["usd_24h_change"], 2)
    return price, change

def post_to_bluesky():
    # Hent Bitcoin data
    price, change = fetch_bitcoin_data()

    # Bluesky API detaljer
    url = "https://bsky.social/xrpc/com.atproto.repo.createRecord"
    headers = {"Content-Type": "application/json"}
    handle = os.getenv("BLUESKY_HANDLE")
    password = os.getenv("BLUESKY_PASSWORD")

    # Logg inn for å få access token
    login_response = requests.post(
        "https://bsky.social/xrpc/com.atproto.server.createSession",
        json={"identifier": handle, "password": password}
    )
    access_token = login_response.json().get("accessJwt")

    # Teksten til posten
    text = (
        f"📉 Bitcoin Price: ${price:,}\n"
        f"📊 24h Change: {change}%\n\n"
        f"#bitcoin #btc #crypto"
    )

    # Manuelle byteindekser for hashtags
    hashtags = ["#bitcoin", "#btc", "#crypto"]
    facets = [
        {
            "index": {"byteStart": text.index(tag), "byteEnd": text.index(tag) + len(tag)},
            "features": [{"$type": "app.bsky.richtext.facet#link", "uri": f"https://bsky.app/search?q=%23{tag[1:]}"}]
        }
        for tag in hashtags
    ]

    # Innholdet til posten
    content = {
        "repo": handle,
        "collection": "app.bsky.feed.post",
        "record": {
            "text": text,
            "facets": facets,
            "createdAt": datetime.utcnow().isoformat() + "Z"
        }
    }

    # Send forespørselen for å poste
    headers["Authorization"] = f"Bearer {access_token}"
    response = requests.post(url, headers=headers, json=content)
    if response.status_code == 200:
        print("Postet vellykket til Bluesky!")
    else:
        print("Feil ved posting:", response.text)

if __name__ == "__main__":
    post_to_bluesky()
