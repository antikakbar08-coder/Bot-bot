import requests
import json
import time
from datetime import datetime

# ================= CONFIGURATION =================
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1489799903361372313/vhtfgVrueL8j0ziJB7gwSkTw97gjP4pz5qiajrOsQ_1b7omwWLCraXsFo4l1rlCwsTkX"
BINANCE_URL = "https://fapi.binance.com/fapi/v1/premiumIndex"
INTERVAL_CEK = 120  # Cek setiap 2 menit

# Memori untuk mencatat koin yang sudah di-alert agar tidak spam
already_alerted_coins = set() 
# =================================================

def send_to_discord(matches, is_urgent=False):
    now = datetime.now().strftime("%H:%M:%S")
    
    if matches:
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
                "title": "🚨 ALERT: FUNDING EKSTRIM TERDETEKSI!",
                "description": f"Update pada pukul `{now}`",
                "color": 15158332, # Merah
                "fields": fields,
                "footer": {"text": "Otomatis reset jika funding kembali normal (< 1.5%)"}
            }]
        }
    else:
        # Laporan rutin (Nihil)
        payload = {
            "username": "Binance Live Monitor",
            "embeds": [{
                "description": f"✅ **Laporan Rutin {now}:** Tidak ada pergerakan ekstrim baru (>1.5% atau <-1.5%).",
                "color": 3066993, # Hijau
            }]
        }

    try:
        requests.post(DISCORD_WEBHOOK_URL, json=payload)
        print(f"[{now}] Berhasil kirim ke Discord (Urgent: {is_urgent})")
    except Exception as e:
        print(f"Error Discord: {e}")

def check_funding():
    global already_alerted_coins
    try:
        response = requests.get(BINANCE_URL)
        data = response.json()
        
        matches = []
        current_extreme_coins = set() # Daftar koin yang saat ini sedang ekstrim

        for item in data:
            if 'lastFundingRate' not in item: continue
            
            # Hitung persentase funding
            funding_pct = float(item['lastFundingRate']) * 100
            symbol = item['symbol']
            
            # LOGIKA BARU: Di atas 1.5% ATAU di bawah -1.5% (Tanpa batas atas/bawah)
            if (funding_pct >= 1.5) or (funding_pct <= -1.5):
                current_extreme_coins.add(symbol)
                
                # Hanya masukkan ke list kirim jika belum pernah di-alert sebelumnya
                if symbol not in already_alerted_coins:
                    matches.append({
                        "symbol": symbol, 
                        "funding_rate_pct": f"{funding_pct:.4f}%"
                    })
                    already_alerted_coins.add(symbol) # Tandai sudah terkirim

        # RESET LOGIC: Cek koin yang sudah tidak ekstrim lagi
        # Menggunakan set difference untuk mencari koin yang sudah 'sembuh'
        koin_yang_kembali_normal = already_alerted_coins - current_extreme_coins
        for coin in koin_yang_kembali_normal:
            already_alerted_coins.remove(coin)
            print(f" LOG: {coin} sudah kembali normal. Memori di-reset.")

        return matches
    except Exception as e:
        print(f"Error Binance: {e}")
        return []

if __name__ == "__main__":
    print("=== BOT MONITORING BINANCE AKTIF (THRESHOLD 1.5%) ===")
    
    counter = 0
    while True:
        hasil_scan = check_funding()
        counter += 1
        
        # JIKA ADA KOIN BARU YANG EKSTRIM
        if hasil_scan:
            send_to_discord(hasil_scan, is_urgent=True)
            # Counter tidak direset agar jadwal laporan rutin 10 menit tetap terjaga
        
        # JIKA SUDAH 10 MENIT (5 x 2 menit)
        if counter >= 5:
            send_to_discord([], is_urgent=False)
            counter = 0
        
        else:
            now_log = datetime.now().strftime("%H:%M:%S")
            print(f"[{now_log}] Cek ke-{counter}: Menunggu 2 menit...")

        time.sleep(INTERVAL_CEK)
