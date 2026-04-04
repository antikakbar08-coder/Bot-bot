import requests
import json
import time
from datetime import datetime

# Konfigurasi
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1489799903361372313/vhtfgVrueL8j0ziJB7gwSkTw97gjP4pz5qiajrOsQ_1b7omwWLCraXsFo4l1rlCwsTkX"
BINANCE_URL = "https://fapi.binance.com/fapi/v1/premiumIndex"

def send_to_discord(matches):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if matches:
        # Jika ada koin yang ditemukan
        fields = []
        for coin in matches:
            fields.append({
                "name": f"🪙 {coin['symbol']}",
                "value": f"**Funding Rate:** `{coin['funding_rate_pct']}`",
                "inline": True
            })

        payload = {
            "username": "Binance Funding Bot",
            "embeds": [{
                "title": "🚨 High Funding Rate Terdeteksi!",
                "description": f"Waktu Pengecekan: `{now}`\nRentang Filter: 1% s/d 2% (Positif/Negatif)",
                "color": 15158332, # Merah
                "fields": fields,
                "footer": {"text": "Status: Ada Koin Aktif"}
            }]
        }
    else:
        # Jika tidak ada koin yang ditemukan (Status Tetap Lapor)
        payload = {
            "username": "Binance Funding Bot",
            "embeds": [{
                "title": "🔍 Status: Monitoring Rutin",
                "description": f"Waktu Pengecekan: `{now}`",
                "color": 3447003, # Biru
                "footer": {"text": "Hasil: Tidak ada koin yang memenuhi kriteria (-1% s/d -2% atau +1% s/d +2%)"}
            }]
        }

    try:
        requests.post(DISCORD_WEBHOOK_URL, json=payload)
        print(f"[{now}] Laporan terkirim ke Discord.")
    except Exception as e:
        print(f"Gagal kirim ke Discord: {e}")

def check_funding():
    try:
        response = requests.get(BINANCE_URL)
        data = response.json()
        
        matches = []
        for item in data:
            if 'lastFundingRate' not in item:
                continue
                
            funding_rate = float(item['lastFundingRate'])
            funding_pct = funding_rate * 100
            
            # Filter 1% - 2% atau -1% - -2%
            if (1.0 <= funding_pct <= 2.0) or (-2.0 <= funding_pct <= -1.0):
                matches.append({
                    "symbol": item['symbol'],
                    "funding_rate_pct": f"{funding_pct:.4f}%"
                })
        
        # Kirim hasil ke Discord (baik ada koin maupun tidak)
        send_to_discord(matches)

    except Exception as e:
        print(f"Terjadi kesalahan saat fetch data: {e}")

if __name__ == "__main__":
    print("Bot dimulai. Melakukan pengecekan setiap 50 detik...")
    while True:
        check_funding()
        # Reset interval 50 detik
        time.sleep(50)
