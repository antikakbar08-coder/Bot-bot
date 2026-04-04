import requests
import json
import time
from datetime import datetime

# ================= CONFIGURATION =================
# URL API Binance Futures
BINANCE_URL = "https://fapi.binance.com/fapi/v1/premiumIndex"

# Cek setiap 2 menit
INTERVAL_CEK = 120  

# URL Webhook Discord Anda
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1489799903361372313/vhtfgVrueL8j0ziJB7gwSkTw97gjP4pz5qiajrOsQ_1b7omwWLCraXsFo4l1rlCwsTkX"
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
                "title": "🚨 ALERT: FUNDING EKSTRIM TERDETEKSI",
                "description": f"Terdeteksi pada pukul `{now}` dengan threshold >1.5% atau <-1.5%",
                "color": 15158332, # Merah
                "fields": fields,
                "footer": {"text": "Monitoring 24/7 Binance Futures"}
            }]
        }
    else:
        # Laporan rutin jika tidak ada yang ekstrim
        payload = {
            "username": "Binance Live Monitor",
            "embeds": [{
                "description": f"✅ **Laporan Rutin {now}:** Tidak ada koin dengan funding >1.5% atau <-1.5%.",
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
            
            # Konversi rate ke persen (0.015 menjadi 1.5%)
            funding_pct = float(item['lastFundingRate']) * 100
            mark_price = float(item.get('markPrice', 0))
            
            # LOGIKA: Minimal 1.5% (Positif) ATAU -1.5% (Negatif)
            if funding_pct >= 1.5 or funding_pct <= -1.5:
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
    print("=== BOT MONITORING AKTIF (LOGIKA > 1.5% & < -1.5%) ===")
