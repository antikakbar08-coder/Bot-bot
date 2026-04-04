import requests
import json
import time
from datetime import datetime

# ================= CONFIGURATION =================
# Pastikan URL Webhook Anda tetap aman dan benar
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1489799903361372313/vhtfgVrueL8j0ziJB7gwSkTw97gjP4pz5qiajrOsQ_1b7omwWLCraXsFo4l1rlCwsTkX"
BINANCE_URL = "https://fapi.binance.com/fapi/v1/premiumIndex"
INTERVAL_CEK = 120  # Cek setiap 2 menit
# =================================================

def send_to_discord(matches, is_urgent=False):
    now = datetime.now().strftime("%H:%M:%S")
    
    if matches:
        fields = []
        for coin in matches:
            fields.append({
                "name": f"🪙 {coin['symbol']}",
                "value": f"**Funding:** `{coin['funding_rate_pct']}`\n**Price:** `${coin['price']}`",
                "inline": True
            })

        payload = {
            "username": "Binance Live Monitor",
            "embeds": [{
                "title": "🚨 ALERT: FUNDING EKSTRIM (>1% / <-1%)",
                "description": f"Terdeteksi pada pukul `{now}`",
                "color": 15158332, # Merah
                "fields": fields,
                "footer": {"text": "Monitoring 24/7 Binance Futures"}
            }]
        }
    else:
        payload = {
            "username": "Binance Live Monitor",
            "embeds": [{
                "description": f"✅ **Laporan Rutin {now}:** Tidak ada koin dengan funding >1% atau <-1%.",
                "color": 3066993, # Hijau
            }]
        }

    try:
        requests.post(DISCORD_WEBHOOK_URL, json=payload)
        print(f"[{now}] Pesan terkirim ke Discord (Urgent: {is_urgent})")
    except Exception as e:
        print(f"Error Discord: {e}")

def check_funding():
    try:
        response = requests.get(BINANCE_URL)
        data = response.json()
        matches = []
        for item in data:
            if 'lastFundingRate' not in item: continue
            
            funding_pct = float(item['lastFundingRate']) * 100
            mark_price = float(item.get('markPrice', 0))
            
            # LOGIKA BARU: Minimal 1% (Positif) atau Maksimal -1% (Negatif)
            # Tanpa batasan angka maksimal di atasnya
            if funding_pct >= 1.0 or funding_pct <= -1.0:
                matches.append({
                    "symbol": item['symbol'], 
                    "funding_rate_pct": f"{funding_pct:.4f}%",
                    "price": f"{mark_price:,.4f}"
                })
        return matches
    except Exception as e:
        print(f"Error Binance: {e}")
        return []

if __name__ == "__main__":
    print("=== BOT MONITORING AKTIF (LOGIKA > 1% & < -1%) ===")
    
    counter = 0
    while True:
        hasil_scan = check_funding()
        counter += 1
        
        if hasil_scan:
            send_to_discord(hasil_scan, is_urgent=True)
            counter = 0 # Reset agar laporan rutin tidak numpuk jika sedang ramai koin ekstrim
        
        elif counter >= 5:
            send_to_discord([], is_urgent=False)
            counter = 0
        
        else:
            now_log = datetime.now().strftime("%H:%M:%S")
            print(f"[{now_log}] Cek ke-{counter}: Tidak ada koin di atas 1%/-1%.")

        time.sleep(INTERVAL_CEK)
