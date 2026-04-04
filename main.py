import os
import time
import requests
from datetime import datetime

# --- CONFIGURATION ---
# Masukkan Webhook URL Discord kamu di environment variable Railway
DISCORD_WEBHOOK_URL = os.getenv("https://discord.com/api/webhooks/1489799903361372313/vhtfgVrueL8j0ziJB7gwSkTw97gjP4pz5qiajrOsQ_1b7omwWLCraXsFo4l1rlCwsTkX")

# Simulasi data dari Polymarket & CCXT
# Dalam aplikasi nyata, kamu akan memanggil API Polymarket atau CCXT di sini
def get_arbitrage_data():
    # Contoh data sport (Baseball & Soccer)
    return [
        {
            "sport": "baseball",
            "event": "Cleveland Guardians vs Detroit Tigers",
            "market": "Win 2026 World Series",
            "yes_odds": 0.001,
            "no_odds": 0.001,
            "total_prob": 0.002,
            "profit": 99.8
        },
        {
            "sport": "soccer",
            "event": "World Cup 2026 - Winner",
            "market": "Indonesia win World Cup",
            "yes_odds": 0.05,
            "no_odds": 0.85,
            "total_prob": 0.90,
            "profit": 10.0
        }
    ]

def send_to_discord(item):
    # Pilih emoji berdasarkan jenis olahraga
    emoji = "⚾" if item['sport'] == "baseball" else "⚽"
    
    # Membuat format pesan yang rapi dengan "Embed" style (via Webhook)
    payload = {
        "embeds": [{
            "title": "🚨 SPORT ARBITRAGE DETECTED 🚨",
            "color": 15158332, # Warna Merah
            "fields": [
                {
                    "name": f"{emoji} Event",
                    "value": f"**{item['event']}**\n*{item['market']}*",
                    "inline": False
                },
                {
                    "name": "📊 Market Odds",
                    "value": f"✅ **YES:** `{item['yes_odds']}`  |  ❌ **NO:** `{item['no_odds']}`",
                    "inline": False
                },
                {
                    "name": "📈 Total Prob",
                    "value": f"`{item['total_prob']}`",
                    "inline": True
                },
                {
                    "name": "💰 Est. Profit",
                    "value": f"**{item['profit']}%**",
                    "inline": True
                }
            ],
            "footer": {
                "text": f"Polymarket Monitoring • {datetime.now().strftime('%H:%M:%S')}"
            }
        }]
    }
    
    try:
        requests.post(, json=payload)
    except Exception as e:
        print(f"Error sending to Discord: {e}")

def main():
    print("🚀 Monitoring Sport Arbitrage started...")
    while True:
        data = get_arbitrage_data()
        
        for item in data:
            send_to_discord(item)
            # Memberikan jeda singkat antar pesan agar tidak dianggap spam oleh Discord
            time.sleep(2)
        
        # Jeda antar pengecekan (misal 5 menit)
        time.sleep(300)

if __name__ == "__main__":
    main()
