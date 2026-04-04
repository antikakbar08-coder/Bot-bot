import requests
import json
import time

# Konfigurasi
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1489799903361372313/vhtfgVrueL8j0ziJB7gwSkTw97gjP4pz5qiajrOsQ_1b7omwWLCraXsFo4l1rlCwsTkX"
BINANCE_URL = "https://fapi.binance.com/fapi/v1/premiumIndex"

def send_to_discord(matches):
    if not matches:
        return

    # Membuat list pesan untuk di dalam embed
    fields = []
    for coin in matches:
        fields.append({
            "name": f"🪙 {coin['symbol']}",
            "value": f"**Funding Rate:** `{coin['funding_rate_pct']}`",
            "inline": True
        })

    payload = {
        "username": "Binance Funding Bot",
        "avatar_url": "https://bin.v7static.com/static/images/common/favicon.ico",
        "embeds": [{
            "title": "🚨 High Funding Rate Alert!",
            "description": "Ditemukan koin dengan Funding Rate di rentang 1% - 2% atau -1% - -2%",
            "color": 15158332,  # Warna Merah/Oranye
            "fields": fields,
            "footer": {
                "text": "Binance Futures Monitor"
            }
        }]
    }

    response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
    if response.status_code == 204:
        print(f"Berhasil mengirim {len(matches)} koin ke Discord.")
    else:
        print(f"Gagal mengirim ke Discord: {response.status_code}, {response.text}")

def check_funding():
    try:
        response = requests.get(BINANCE_URL)
        data = response.json()
        
        matches = []
        
        for item in data:
            # Pastikan item memiliki key yang dibutuhkan
            if 'lastFundingRate' not in item:
                continue
                
            funding_rate = float(item['lastFundingRate'])
            funding_pct = funding_rate * 100
            
            # Filter: 1% s/d 2% atau -1% s/d -2%
            if (1.0 <= funding_pct <= 2.0) or (-2.0 <= funding_pct <= -1.0):
                matches.append({
                    "symbol": item['symbol'],
                    "funding_rate_pct": f"{funding_pct:.4f}%"
                })
        
        if matches:
            send_to_discord(matches)
        else:
            print("Monitoring... Tidak ada koin yang memenuhi kriteria.")

    except Exception as e:
        print(f"Terjadi kesalahan: {e}")

if __name__ == "__main__":
    print("Bot Monitoring Funding Rate dimulai...")
    # Jalankan pengecekan (misal: setiap 1 menit)
    while True:
        check_funding()
        # Delay agar tidak terkena rate limit (60 detik)
        time.sleep(60)
