import ccxt
import requests
import time

# --- KONFIGURASI ---
# Pastikan URL berada di dalam tanda kutip " "
DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1489799903361372313/vhtfgVrueL8j0ziJB7gwSkTw97gjP4pz5qiajrOsQ_1b7omwWLCraXsFo4l1rlCwsTkX"

FUNDING_THRESHOLD = 0.01  # Saya set 0.01% dulu agar Anda bisa tes notifikasinya muncul
MISPRICING_THRESHOLD = 1.0 

# Inisialisasi Bybit
exchange = ccxt.bybit({
    'enableRateLimit': True,
    'options': {'defaultType': 'linear'}
})

def send_discord(embed):
    payload = {
        "username": "Bybit Railway Bot",
        "embeds": [embed]
    }
    try:
        requests.post(DISCORD_WEBHOOK, json=payload, timeout=10)
    except Exception as e:
        print(f"Error Discord: {e}")

def monitor():
    print("🚀 Bot Aktif: Memantau Bybit...", flush=True)
    while True:
        try:
            # Ambil data harga dan funding
            tickers = exchange.fetch_tickers()
            
            for symbol, data in tickers.items():
                if ':USDT' not in symbol: 
                    continue

                # 1. Cek Funding Rate
                # Data funding di Bybit biasanya ada di 'info' -> 'fundingRate'
                raw_info = data.get('info', {})
                funding = raw_info.get('fundingRate')
                
                if funding:
                    fr_pct = float(funding) * 100
                    if abs(fr_pct) >= FUNDING_THRESHOLD:
                        send_discord({
                            "title": f"🚨 HIGH FUNDING: {symbol}",
                            "color": 0xFF0000,
                            "fields": [
                                {"name": "Funding Rate", "value": f"{fr_pct:.4f}%", "inline": True},
                                {"name": "Side", "value": "Short get paid" if fr_pct > 0 else "Long get paid", "inline": True}
                            ],
                            "footer": {"text": "Railway Monitor"}
                        })

            print(f"✅ Check Done: {time.strftime('%H:%M:%S')}", flush=True)
            time.sleep(60) # Cek setiap 1 menit

        except Exception as e:
            print(f"❌ Error: {e}", flush=True)
            time.sleep(30)

if __name__ == "__main__":
    monitor()
