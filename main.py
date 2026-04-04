import requests
import json
import time
from datetime import datetime

# Konfigurasi
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1489799903361372313/vhtfgVrueL8j0ziJB7gwSkTw97gjP4pz5qiajrOsQ_1b7omwWLCraXsFo4l1rlCwsTkX"
BINANCE_URL = "https://fapi.binance.com/fapi/v1/premiumIndex"

def send_to_discord(matches):
    now = datetime.now().strftime("%H:%M:%S")
    date_now = datetime.now().strftime("%d-%m-%Y")
    
    if matches:
        # Jika ditemukan koin yang masuk kriteria
        fields = []
        for coin in matches:
            fields.append({
                "name": f"🪙 {coin['symbol']}",
                "value": f"**Funding:** `{coin['funding_rate_pct']}`",
                "inline": True
            })

        payload = {
            "username": "Binance Funding Monitor",
            "embeds": [{
                "title": "🚨 HIGH FUNDING ALERT!",
                "description": f"Ditemukan koin dengan rate ekstrim pada pukul `{now}`",
                "color": 15158332, # Merah
                "fields": fields,
                "footer": {"text": f"Tanggal: {date_now} | Filter: 1% s/d 2%"}
            }]
        }
    else:
        # Jika hasil kosong (Laporan rutin setiap 10 menit)
        payload = {
            "username": "Binance Funding Monitor",
            "embeds": [{
                "description": f"✅ **Check berkala {now}:** Tidak ada koin di rentang 1% - 2%.",
                "color": 3066993, # Hijau
            }]
        }

    try:
        requests.post(DISCORD_WEBHOOK_URL, json=payload)
        print(f"[{now}] Laporan 10 menit terkirim.")
    except Exception as e:
        print(f"Gagal kirim ke Discord: {e}")

def check_funding():
    try:
        response = requests.get(BINANCE_URL)
        data = response.json()
        
        matches = []
        for item in data:
            if 'lastFundingRate' not in item: continue
                
            funding_pct = float(item['lastFundingRate']) * 100
            
            # Filter sesuai permintaan: 1% s/d 2% atau -1% s/d -2%
            if (1.0 <= funding_pct <= 2.0) or (-2.0 <= funding_pct <= -1.0):
                matches.append({
                    "symbol": item['symbol'],
                    "funding_rate_pct": f"{funding_pct:.4f}%"
                })
        
        send_to_discord(matches)

    except Exception as e:
        print(f"Terjadi kesalahan data: {e}")

if __name__ == "__main__":
    print("=== BOT FUNDING MONITOR AKTIF ===")
    print("Interval: Setiap 10 Menit")
    
    while True:
        check_funding()
        
        # Delay 10 menit (10 * 60 detik)
        time.sleep(600)
