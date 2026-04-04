import requests
import time
from datetime import datetime

# ================= CONFIGURATION =================
BINANCE_URL = "https://fapi.binance.com/fapi/v1/premiumIndex"
DISCORD_WEBHOOK_URL = "URL_WEBHOOK_ANDA"

INTERVAL_CEK = 120      # Cek market tiap 2 menit (120 detik)
INTERVAL_RUTIN = 420    # Laporan rutin tiap 7 menit (420 detik)
THRESHOLD = 1.5         # Persentase ambang batas (1.5%)
# =================================================

session = requests.Session()

def send_to_discord(matches, is_urgent=False):
    now = datetime.now().strftime("%H:%M:%S")
    
    if is_urgent:
        # Pesan jika ada yang Ekstrim
        payload = {
            "username": "Binance Extreme Alert",
            "embeds": [{
                "title": "🚨 ALERT: FUNDING EKSTRIM TERDETEKSI",
                "description": f"Terdeteksi pada pukul `{now}`",
                "color": 15158332, # Merah
                "fields": matches,
                "footer": {"text": "🚨 Urgent Alert - Immediate Delivery"}
            }]
        }
    else:
        # Laporan rutin tiap 7 menit
        payload = {
            "username": "Binance Routine Monitor",
            "embeds": [{
                "description": f"✅ **Laporan Rutin {now}:** Tidak ada funding > {THRESHOLD}% atau < -{THRESHOLD}%.",
                "color": 3066993, # Hijau
            }]
        }

    try:
        session.post(DISCORD_WEBHOOK_URL, json=payload)
        print(f"[{now}] Pesan terkirim ke Discord (Urgent: {is_urgent})")
    except Exception as e:
        print(f"Error Discord: {e}")

def check_market():
    try:
        response = session.get(BINANCE_URL, timeout=10)
        data = response.json()
        extreme_coins = []
        
        for item in data:
            if 'lastFundingRate' not in item: continue
            funding_pct = float(item['lastFundingRate']) * 100
            
            if abs(funding_pct) >= THRESHOLD:
                extreme_coins.append({
                    "name": f"🪙 {item['symbol']}",
                    "value": f"**Funding:** `{funding_pct:.4f}%`",
                    "inline": True
                })
        return extreme_coins
    except Exception as e:
        print(f"Error Binance: {e}")
        return None

if __name__ == "__main__":
    print("=== BOT AKTIF (Cek 2m, Rutin 7m, Extreme Langsung) ===")
    
    # Mencatat kapan terakhir kali mengirim laporan rutin
    last_routine_time = time.time()

    while True:
        results = check_market()
        current_time = time.time()
        
        if results:
            # Jika ada yang ekstrim, LANGSUNG kirim
            send_to_discord(results, is_urgent=True)
            # Reset waktu rutin agar tidak bertabrakan (opsional)
            last_routine_time = current_time 
        else:
            # Jika tidak ada yang ekstrim, cek apakah sudah waktunya laporan rutin (7 menit)
            if (current_time - last_routine_time) >= INTERVAL_RUTIN:
                send_to_discord(None, is_urgent=False)
                last_routine_time = current_time
            else:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Market aman. Menunggu jadwal rutin berikutnya...")

        # Tetap tunggu 2 menit sebelum cek market lagi
        time.sleep(INTERVAL_CEK)
