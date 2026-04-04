import requests
import time
from datetime import datetime

# ================= CONFIGURATION =================
# URL API Binance Futures
BINANCE_URL = "https://fapi.binance.com/fapi/v1/premiumIndex"

# URL Webhook Discord Anda (Sudah diupdate)
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1489799903361372313/vhtfgVrueL8j0ziJB7gwSkTw97gjP4pz5qiajrOsQ_1b7omwWLCraXsFo4l1rlCwsTkX"

INTERVAL_CEK = 120      # Cek market setiap 2 menit (120 detik)
INTERVAL_RUTIN = 420    # Kirim laporan rutin setiap 7 menit (420 detik)
THRESHOLD = 1.5         # Ambang batas funding rate (1.5% atau -1.5%)
# =================================================

session = requests.Session()

def send_to_discord(matches, is_urgent=False):
    now = datetime.now().strftime("%H:%M:%S")
    
    if is_urgent:
        # Format pesan jika ditemukan kondisi ekstrim
        payload = {
            "username": "Binance Extreme Alert",
            "embeds": [{
                "title": "🚨 ALERT: FUNDING EKSTRIM TERDETEKSI",
                "description": f"Terdeteksi pada pukul `{now}` dengan threshold >{THRESHOLD}% atau <-{THRESHOLD}%",
                "color": 15158332, # Warna Merah
                "fields": matches,
                "footer": {"text": "Monitoring 24/7 Binance Futures | Urgent Mode"}
            }]
        }
    else:
        # Format laporan rutin jika kondisi aman
        payload = {
            "username": "Binance Routine Monitor",
            "embeds": [{
                "description": f"✅ **Laporan Rutin {now}:** Kondisi market stabil. Tidak ada koin di atas ambang batas {THRESHOLD}%.",
                "color": 3066993, # Warna Hijau
            }]
        }

    try:
        response = session.post(DISCORD_WEBHOOK_URL, json=payload)
        response.raise_for_status()
        print(f"[{now}] Pesan terkirim ke Discord (Urgent: {is_urgent})")
    except Exception as e:
        print(f"[{now}] Error mengirim ke Discord: {e}")

def check_market():
    try:
        response = session.get(BINANCE_URL, timeout=15)
        response.raise_for_status()
        data = response.json()
        extreme_coins = []
        
        for item in data:
            if 'lastFundingRate' not in item: 
                continue
                
            # Konversi rate decimal ke persen
            funding_pct = float(item['lastFundingRate']) * 100
            mark_price = float(item.get('markPrice', 0))
            
            # Cek jika melewati ambang batas positif atau negatif
            if abs(funding_pct) >= THRESHOLD:
                extreme_coins.append({
                    "name": f"🪙 {item['symbol']}",
                    "value": f"**Funding:** `{funding_pct:.4f}%` \n**Price:** `${mark_price:,.4f}`",
                    "inline": True
                })
        return extreme_coins
    except Exception as e:
        print(f"Error Binance API: {e}")
        return None

if __name__ == "__main__":
    print(f"=== BOT AKTIF ===")
    print(f"Interval Cek: {INTERVAL_CEK} detik")
    print(f"Interval Rutin: {INTERVAL_RUTIN} detik")
    print(f"Threshold: {THRESHOLD}%")
    print("=================")

    # Inisialisasi waktu terakhir laporan rutin dikirim
    last_routine_time = time.time()

    while True:
        # 1. Ambil data dari Binance
        results = check_market()
        current_time = time.time()
        
        if results:
            # 2. Jika ada koin ekstrim, LANGSUNG kirim ke Discord
            send_to_discord(results, is_urgent=True)
            # Reset timer rutin agar tidak double kirim setelah alert
            last_routine_time = current_time 
            
        else:
            # 3. Jika tidak ada yang ekstrim, cek apakah sudah masuk jadwal rutin 7 menit
            if (current_time - last_routine_time) >= INTERVAL_RUTIN:
                send_to_discord(None, is_urgent=False)
                last_routine_time = current_time
            else:
                # Log di terminal saja agar Anda tahu bot masih hidup
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Scan selesai: Market aman.")

        # 4. Tunggu selama 2 menit sebelum scan ulang
        time.sleep(INTERVAL_CEK)
