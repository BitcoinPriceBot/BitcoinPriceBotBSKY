import requests
import os
from datetime import datetime
from atproto import Client

# Konstanter
BLUESKY_HANDLE = os.getenv("BLUESKY_HANDLE")
BLUESKY_PASSWORD = os.getenv("BLUESKY_PASSWORD")

def get_bitcoin_price():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
    response = requests.get(url)
    if response.status_code == 200:
        price = response.json()['bitcoin']['usd']
        return price
    else:
        print("Error fetching Bitcoin price")
        return None

def post_to_bluesky(client, price):
    from atproto import models

    # Opprett en "rich text"-post med hashtags
    text = f"Bitcoin price: ${price:,}\n\n#btc #crypto #blockchain"
    facets = models.Facet.from_tags(["btc", "crypto", "blockchain"], text)

    # Send posten med rich text
    client.send_post(text=text, facets=facets)
    print(f"Posted: {text} at {datetime.now()}")

def main():
    client = Client()
    client.login(BLUESKY_HANDLE, BLUESKY_PASSWORD)
    bitcoin_price = get_bitcoin_price()
    if bitcoin_price:
        post_to_bluesky(client, bitcoin_price)

if __name__ == "__main__":
    main()
