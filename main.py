import os
import time
import requests
from datetime import datetime

# --- CONFIGURATION ---
# Pastikan URL ini dimasukkan ke Environment Variable di Railway dengan nama DISCORD_WEBHOOK_URL
# Jika ingin hardcode (tidak disarankan), pastikan diapit tanda kutip ""
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "https://discord.com/api/webhooks/1489799903361372313/vhtfgVrueL8j0ziJB7gwSkTw97gjP4pz5qiajrOsQ_1b7omwWLCraXsFo4l1rlCwsTkX")

def get_arbitrage_data():
    # Simulasi data (Ganti dengan logika API Polymarket/CCXT aslimu)
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
    emoji = "⚾" if item['sport'] == "baseball" else "⚽"
    
    payload = {
        "embeds": [{
            "title": "🚨 SPORT ARBITRAGE DETECTED 🚨",
            "color": 15158332,
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
        # Perbaikan: Menambahkan variabel URL dan menangani respon
        requests.post(DISCORD_WEBHOOK_URL, json=payload)
    except Exception as e:
        print(f"Error sending to Discord: {e}")

def main():
    print("🚀 Monitoring Sport Arbitrage started...")
    while True:
        data = get_arbitrage_data()
        
        for item in data:
            send_to_discord(item)
            # Jeda 2 detik antar pesan agar tidak kena spam filter Discord
            time.sleep(2)
        
        # --- PERUBAHAN DISINI ---
        # 300 detik = 5 menit
        print(f"✅ Data sent. Waiting 5 minutes for next check...")
        time.sleep(300) 

if __name__ == "__main__":
    main()
