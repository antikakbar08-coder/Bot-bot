import requests
import json
import time
from datetime import datetime

# ================= CONFIGURATION =================
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1489799903361372313/vhtfgVrueL8j0ziJB7gwSkTw97gjP4pz5qiajrOsQ_1b7omwWLCraXsFo4l1rlCwsTkX"
BINANCE_URL = "https://fapi.binance.com/fapi/v1/premiumIndex"
INTERVAL_CEK = 120  # Cek setiap 2 menit (120 detik)
# =================================================

def send_to_discord(matches, is_urgent=False):
    now = datetime.now().strftime("%H:%M:%S")
    
    if matches:
        # PESAN URGENT: Jika ada koin yang sesuai kriteria
        fields = []
        for coin in matches:
            fields.append({
                "name": f"🪙 {coin['symbol']}",
                "value": f"**Funding:** `{coin['funding_rate_pct']}`",
                "inline": True
            })

        payload = {
            "username": "Binance Live Monitor",
            "embeds": [{
                "title": "🚨 ALERT: KONDISI EKSTRIM DITEMUKAN!",
                "description": f"Terdeteksi pada pukul `{now}`",
                "color": 15158332, # Merah
                "fields": fields,
                "footer": {"text": "Bot akan langsung mengirim jika kriteria terpenuhi"}
            }]
        }
    else:
        # PESAN RUTIN: Laporan setiap 10 menit (Nihil)
        payload = {
            "username": "Binance Live Monitor",
            "embeds": [{
                "description": f"✅ **Laporan Rutin {now}:** Tidak ada koin yang ekstrim dalam 10 menit terakhir.",
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
            
            # Filter: 1% s/d 2% atau -1% s/d -2%
            if (1.0 <= funding_pct <= 2.0) or (-2.0 <= funding_pct <= -1.0):
                matches.append({
                    "symbol": item['symbol'], 
                    "funding_rate_pct": f"{funding_pct:.4f}%"
                })
        return matches
    except Exception as e:
        print(f"Error Binance: {e}")
        return []

if __name__ == "__main__":
    print("=== BOT MONITORING MULTI-INTERVAL AKTIF ===")
    print("Logika: Cek tiap 2 menit, Laporan rutin tiap 10 menit.")
    
    counter = 0
    while True:
        hasil_scan = check_funding()
        counter += 1
        
        # JIKA ADA KOIN (URGENT): Langsung kirim saat itu juga
        if hasil_scan:
            send_to_discord(hasil_scan, is_urgent=True)
            # Opsional: Jika sudah kirim urgent, kita reset counter rutinnya
            counter = 0 
        
        # JIKA TIDAK ADA KOIN (RUTIN): Tunggu sampai 5 kali cek (10 menit)
        elif counter >= 5:
            send_to_discord([], is_urgent=False)
            counter = 0
        
        else:
            now_log = datetime.now().strftime("%H:%M:%S")
            print(f"[{now_log}] Cek ke-{counter}: Nihil. Menunggu 2 menit...")

        # Jeda antar pengecekan (2 menit)
        time.sleep(INTERVAL_CEK)
