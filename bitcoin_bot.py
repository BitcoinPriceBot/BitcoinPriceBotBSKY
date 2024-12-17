import requests
import os
from datetime import datetime, timezone

def fetch_bitcoin_price():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd&include_24hr_change=true"
    response = requests.get(url)
    data = response.json()
    price = f"{data['bitcoin']['usd']:,}"  # Legg til tusenskille
    change = round(data['bitcoin']['usd_24h_change'], 2)
    return price, change

def post_to_bluesky():
    # Hent innloggingsdetaljer fra miljøvariabler
    handle = os.getenv("BLUESKY_HANDLE")
    password = os.getenv("BLUESKY_PASSWORD")

    # Bluesky API-endepunkter og headers
    login_url = "https://bsky.social/xrpc/com.atproto.server.createSession"
    post_url = "https://bsky.social/xrpc/com.atproto.repo.createRecord"
    headers = {"Content-Type": "application/json"}

    # Start innlogging
    print("Starting login...")
    login_response = requests.post(login_url, json={"identifier": handle, "password": password})
    if login_response.status_code == 200:
        access_token = login_response.json().get("accessJwt")
        headers["Authorization"] = f"Bearer {access_token}"
        print("Login successful.")
    else:
        print("Login failed:", login_response.text)
        return

    # Hent Bitcoin-pris og endring
    price, change = fetch_bitcoin_price()
    print(f"Fetched price: {price}, Change: {change}%")

    # Velg emoji basert på prisendring
    emoji = "📉" if change < 0 else "📈"

    # Lag innholdet til posten
    content = {
        "repo": handle,
        "collection": "app.bsky.feed.post",
        "record": {
            "text": f"{emoji} Bitcoin Price: ${price} ({change}% )\n\n#bitcoin #btc #crypto",
            "createdAt": datetime.now(timezone.utc).isoformat()
        }
    }

    # Send post og logg respons
    print("Sending post...")
    response = requests.post(post_url, headers=headers, json=content)
    print("Response status code:", response.status_code)
    print("Response text:", response.text)

    if response.status_code == 200:
        print("Successfully posted to Bluesky!")
    else:
        print("Error posting:", response.text)

if __name__ == "__main__":
    post_to_bluesky()
