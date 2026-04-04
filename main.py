import ccxt
import requests
import time

# ================= KONFIGURASI UTAMA =================
# Alamat pengiriman ke Discord kamu
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1489799903361372313/vhtfgVrueL8j0ziJB7gwSkTw97gjP4pz5qiajrOsQ_1b7omwWLCraXsFo4l1rlCwsTkX"

# Batas notifikasi (0.01 berarti 0.01%)
# Binance biasanya update funding setiap 8 jam.
THRESHOLD_POSITIVE = 0.01  
THRESHOLD_NEGATIVE = -0.01 

# Cek setiap 10 menit agar tidak kena blokir Binance (600 detik)
CHECK_INTERVAL = 600 
# =====================================================

def send_discord_alert(symbol, rate):
    """Fungsi untuk mengirim pesan cantik ke Discord"""
    
    # Menentukan warna kotak (Merah jika positif, Hijau jika negatif)
    color = 15158332 if rate > 0 else 3066993 
    status = "HIGH POSITIVE" if rate > 0 else "HIGH NEGATIVE"

    payload = {
        "embeds": [{
            "title": f"⚠️ FUNDING RATE ALERT: {symbol}",
            "description": f"Terdeteksi lonjakan funding rate pada pasangan **{symbol}**.",
            "color": color,
            "fields": [
                {"name": "Status", "value": f"**{status}**", "inline": True},
                {"name": "Funding Rate", "value": f"`{rate:.4f}%`", "inline": True},
                {"name": "Sumber", "value": "Binance Futures", "inline": True}
            ],
            "footer": {"text": "Bot Monitor 24/7 • Powered by Python"},
            "timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
        }]
    }
    
    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
        if response.status_code == 204:
            print(f"✅ Alert terkirim untuk {symbol}")
        else:
            print(f"❌ Gagal kirim webhook: {response.status_code}")
    except Exception as e:
        print(f"❌ Error kirim webhook: {e}")

def main():
    # Menghubungkan ke API Binance Futures (tanpa perlu API Key untuk baca data publik)
    exchange = ccxt.binance({'options': {'defaultType': 'future'}})
    
    print("🚀 Bot Monitoring Funding Binance Aktif...")
    print(f"Cek setiap {CHECK_INTERVAL} detik. Batas: {THRESHOLD_POSITIVE}% / {THRESHOLD_NEGATIVE}%")

    while True:
        try:
            # Ambil data semua koin di Futures
            print("🔍 Sedang memindai pasar...")
            markets = exchange.fetch_premium_index()
            
            for symbol, data in markets.items():
                # Rumus: desimal * 100 untuk jadi persen
                funding_rate = data['fundingRate'] * 100
                
                # Logika pengecekan
                if funding_rate >= THRESHOLD_POSITIVE or funding_rate <= THRESHOLD_NEGATIVE:
                    send_discord_alert(symbol, funding_rate)
            
            print(f"😴 Selesai scan. Istirahat {CHECK_INTERVAL} detik.")
            time.sleep(CHECK_INTERVAL)
            
        except Exception as e:
            print(f"⚠️ Terjadi gangguan koneksi: {e}")
            time.sleep(30) # Tunggu sebentar lalu coba lagi

if __name__ == "__main__":
    main()
