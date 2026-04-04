import ccxt
import requests
import os
import time

# --- KONFIGURASI ---
# Railway akan mengambil URL ini dari tab "Variables"
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# Batas persentase: 0.5% = 0.005
THRESHOLD = 0.005 

def send_discord_log(message):
    if WEBHOOK_URL:
        payload = {"content": message}
        try:
            requests.post(WEBHOOK_URL, json=payload)
        except Exception as e:
            print(f"Gagal kirim ke Discord: {e}")
    print(message)

def check_funding():
    # Menggunakan Binance Futures
    exchange = ccxt.binance({'options': {'defaultType': 'future'}})
    
    try:
        # Mengambil data funding rate terbaru
        markets = exchange.fetch_funding_rates()
        
        found = False
        for symbol, data in markets.items():
            funding_rate = data['fundingRate']
            
            # Cek jika funding rate >= 0.5% atau <= -0.5%
            if abs(funding_rate) >= THRESHOLD:
                found = True
                percentage = funding_rate * 100
                msg = f"⚠️ **Funding Rate Alert (0.5%)**\nSymbol: `{symbol}`\nRate: `{percentage:.4f}%`"
                send_discord_log(msg)
        
        if not found:
            print("Pemindaian selesai: Tidak ada funding rate di atas 0.5% saat ini.")
                
    except Exception as e:
        # Menghindari error 'fetch_premium_index' dengan library ccxt terbaru
        send_discord_log(f"❌ **Error API Binance:** {str(e)}")

if __name__ == "__main__":
    send_discord_log("🚀 **Bot Monitoring (Batas 0.5%) Aktif 24 Jam...**")
    
    while True:
        try:
            check_funding()
            # Jeda 10 menit (600 detik) agar tidak kena spam/limit API
            time.sleep(600)
        except Exception as e:
            print(f"Sistem Restarting... Error: {e}")
            time.sleep(60)
