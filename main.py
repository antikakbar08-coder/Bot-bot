import requests
import json
import time
from datetime import datetime

# ================= CONFIGURATION =================
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1489799903361372313/vhtfgVrueL8j0ziJB7gwSkTw97gjP4pz5qiajrOsQ_1b7omwWLCraXsFo4l1rlCwsTkX"
# Mencari koin bertema BTC di DEX
DEX_SEARCH_URL = "https://api.dexscreener.com/latest/dex/search?q=btc"
INTERVAL_CEK = 120  # 2 Menit
MIN_LIQUIDITY = 50000  # Filter Likuiditas minimal $50k (Indikasi holder besar)
MAX_PRICE = 0.01

# Untuk menghindari spam, kita simpan list koin yang sudah di-alert
alerted_coins = {}

def send_to_discord(matches, is_status=False):
    now = datetime.now().strftime("%H:%M:%S")
    if is_status:
        payload = {
            "embeds": [{
                "description": f"✅ **Status Scan DEX {now}:** Menunggu koin potensial...",
                "color": 8421504
            }]
        }
    else:
        fields = []
        for coin in matches:
            fields.append({
                "name": f"🚀 {coin['symbol']} ({coin['chain']})",
                "value": f"Price: `${coin['price']}`\nLiq: `${coin['liq']:,.0f}`\n[Chart]({coin['url']})",
                "inline": True
            })
        
        payload = {
            "username": "Jo DEX Monitor",
            "embeds": [{
                "title": "🚨 NEW DEX POTENTIAL!",
                "color": 15105570,
                "fields": fields,
                "footer": {"text": "Berdasarkan kriteria Harga Minim & Liq Besar"}
            }]
        }

    try:
        requests.post(DISCORD_WEBHOOK_URL, json=payload)
    except Exception as e:
        print(f"Error Discord: {e}")

def scan_dex():
    matches = []
    try:
        response = requests.get(DEX_SEARCH_URL)
        data = response.json()
        pairs = data.get('pairs', [])
        
        for pair in pairs:
            symbol = pair['baseToken']['symbol']
            price = float(pair.get('priceUsd', 0))
            liq = pair.get('liquidity', {}).get('usd', 0)
            chain = pair.get('chainId', 'unknown')
            pair_address = pair.get('pairAddress')

            # Filter Logika
            if price <= MAX_PRICE and liq >= MIN_LIQUIDITY:
                # Limit 3x alert per koin (menggunakan pairAddress sebagai ID unik)
                count = alerted_coins.get(pair_address, 0)
                if count < 3:
                    alerted_coins[pair_address] = count + 1
                    matches.append({
                        "symbol": symbol,
                        "price": price,
                        "liq": liq,
                        "chain": chain,
                        "url": pair['url']
                    })
        return matches
    except Exception as e:
        print(f"Error API: {e}")
        return []

if __name__ == "__main__":
    print("=== DEX MONITORING AKTIF ===")
    counter = 0
    while True:
        hasil = scan_dex()
        counter += 1
        
        if hasil:
            send_to_discord(hasil)
        
        # Laporan rutin setiap 5 menit (sekitar 3x loop jika interval 120s)
        if counter >= 3:
            if not hasil:
                send_to_discord([], is_status=True)
            counter = 0

        time.sleep(INTERVAL_CEK)
