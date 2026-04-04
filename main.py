import requests
import json
import time
from datetime import datetime

# ================= CONFIGURATION =================
# GANTI DENGAN WEBHOOK URL ANDA
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/..." 
BINANCE_URL = "https://fapi.binance.com/fapi/v1/premiumIndex"
INTERVAL_CEK = 120  # Cek setiap 120 detik (2 menit)
# =================================================

def send_to_discord(matches, is_urgent=False):
    now = datetime.now().strftime("%H:%M:%S")
    
    if matches:
        fields = []
        for coin in matches:
            fields.append({
                "name": f"🪙 {coin['symbol']}",
                "value": f"**Funding:** `{coin['funding_rate_pct']}`\n**Market:** [Buka Chart]({coin['url']})\n**Jaringan:** Binance Futures",
                "inline": True
            })

        payload = {
            "username": "Binance Live Monitor",
            "embeds": [{
                "title": "🚨 ALERT: FUNDING FEE TERDETEKSI!",
                "description": f"Terdeteksi pada pukul `{now}`\nKriteria: `>= 0.5%` atau `<= -0.5%` (Tanpa Batas Atas)",
                "color": 15158332, # Warna Merah
                "fields": fields[:25], # Limit Discord 25 field
                "footer": {"text": "Monitoring Real-time Binance"}
            }]
        }
    else:
        # Laporan rutin jika tidak ada koin yang memenuhi kriteria
        payload = {
            "username": "Binance Live Monitor",
            "embeds": [{
                "description": f"✅ **Laporan Rutin {now}:** Tidak ada koin dengan funding >= 0.5%.",
                "color": 3066993, # Warna Hijau
            }]
        }

    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)
        response.raise_for_status()
        print(f"[{now}] Berhasil mengirim update ke Discord.")
    except Exception as e:
        print(f"[{now}] Error Discord: {e}")

def check_funding():
    try:
        response = requests.get(BINANCE_URL, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        matches = []
        for item in data:
            if 'lastFundingRate' not in item: continue
            
            # Konversi rate ke persentase (Contoh: 0.005 jadi 0.5%)
            funding_pct = float(item['lastFundingRate']) * 100
            symbol = item['symbol']
            
            # LOGIKA: Minimal 0.5% atau Minimal -0.5% (Tak Terbatas)
            # abs() mengubah angka negatif menjadi positif untuk pengecekan jarak dari nol
            if abs(funding_pct) >= 0.5:
                matches.append({
                    "symbol": symbol, 
                    "funding_rate_pct": f"{funding_pct:.4f}%",
                    "url": f"https://www.binance.com/id/futures/{symbol}"
                })
        return matches
    except Exception as e:
        print(f"Error mengambil data Binance: {e}")
        return None

if __name__ == "__main__":
    print("=== BOT MONITORING AKTIF (AMBANG BATAS 0.5%) ===")
    print("Script ini akan memantau koin dengan funding fee tinggi secara terus-menerus.")
    
    counter = 0
    while True:
        hasil_scan = check_funding()
        counter += 1
        
        if hasil_scan:
            # Kirim alert jika ada koin yang sesuai kriteria
            send_to_discord(hasil_scan, is_urgent=True)
            counter = 0 # Reset counter laporan rutin
        elif counter >= 5: 
            # Kirim laporan rutin setiap 10 menit (5 * 2 menit) jika hasil nihil
            send_to_discord([], is_urgent=False)
            counter = 0
        else:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Cek #{counter}: Kondisi pasar normal.")

        # Jeda waktu antar pengecekan
        time.sleep(INTERVAL_CEK)
