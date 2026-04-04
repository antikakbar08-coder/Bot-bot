import requests
import json
import time
from datetime import datetime

# ================= CONFIGURATION =================
BINANCE_URL = "https://fapi.binance.com/fapi/v1/premiumIndex"
DISCORD_WEBHOOK_URL = "ISI_URL_WEBHOOK_ANDA_DI_SINI"
INTERVAL_CEK = 120  # Cek setiap 2 menit
THRESHOLD = 1.0     # Ambang batas %

# Variabel untuk menyimpan state koin yang sudah di-notif agar tidak spam
already_notified = set() 

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
                "title": "🚨 ALERT: PERUBAHAN FUNDING BARU",
                "description": f"Koin baru terdeteksi pada pukul `{now}`",
                "color": 15158332, 
                "fields": fields,
                "footer": {"text": "Monitoring 24/7 Binance Futures"}
            }]
        }
    else:
        # Pesan rutin hanya jika tidak ada koin aktif sama sekali
        payload = {
            "username": "Binance Live Monitor",
            "embeds": [{
                "description": f"✅ **Laporan Rutin {now}:** Market cenderung stabil.",
                "color": 3066993,
            }]
        }

    try:
        requests.post(DISCORD_WEBHOOK_URL, json=payload)
        print(f"[{now}] Pesan terkirim ke Discord.")
    except Exception as e:
        print(f"Error Discord: {e}")

def check_funding():
    global already_notified
    try:
        response = requests.get(BINANCE_URL)
        data = response.json()
        
        current_matches = []
        new_matches_to_report = []
        active_symbols = set()

        for item in data:
            if 'lastFundingRate' not in item: continue
            
            funding_pct = float(item['lastFundingRate']) * 100
            symbol = item['symbol']
            
            # Cek jika masuk kriteria ekstrem
            if funding_pct >= THRESHOLD or funding_pct <= -THRESHOLD:
                active_symbols.add(symbol)
                coin_data = {
                    "symbol": symbol, 
                    "funding_rate_pct": f"{funding_pct:.4f}%",
                    "price": f"{float(item.get('mark_price', 0)):,.4f}"
                }
                
                # Cek apakah koin ini BARU (belum ada di list notif sebelumnya)
                if symbol not in already_notified:
                    new_matches_to_report.append(coin_data)
                    already_notified.add(symbol)

        # Bersihkan koin dari memori jika sudah tidak ekstrem lagi (agar bisa di-notif lagi di masa depan)
        already_notified = already_notified.intersection(active_symbols)

        return new_matches_to_report
    except Exception as e:
        print(f"Error Binance: {e}")
        return []

if __name__ == "__main__":
    print(f"=== BOT ANTI-SPAM AKTIF (Threshold: > {THRESHOLD}%) ===")
    
    counter = 0
    while True:
        # Hanya ambil koin yang BARU masuk kriteria ekstrem
        koin_baru = check_funding()
        counter += 1
        
        if koin_baru:
            send_to_discord(koin_baru, is_urgent=True)
            counter = 0 
        
        # Laporan rutin tetap ada setiap 10 menit (5 kali loop * 2 menit)
        elif counter >= 5:
            # Opsional: Jika ingin benar-benar sepi, matikan fungsi else ini
            if not already_notified:
                send_to_discord([], is_urgent=False)
            counter = 0
        
        else:
            now_log = datetime.now().strftime("%H:%M:%S")
            print(f"[{now_log}] Monitoring... (Aktif dipantau: {len(already_notified)} koin)")

        time.sleep(INTERVAL_CEK)
