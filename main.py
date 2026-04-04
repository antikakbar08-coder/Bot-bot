import ccxt
import requests
import time
import os

# --- KONFIGURASI ---
# Railway menyarankan menggunakan Environment Variables, tapi Anda bisa tempel langsung di sini
DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1489799903361372313/vhtfgVrueL8j0ziJB7gwSkTw97gjP4pz5qiajrOsQ_1b7omwWLCraXsFo4l1rlCwsTkX"

FUNDING_THRESHOLD = 2.0  # Notif jika >= 2% atau <= -2%
MISPRICING_THRESHOLD = 1.0 

# Inisialisasi Bybit
exchange = ccxt.bybit({
    'enableRateLimit': True,
    'options': {'defaultType': 'linear'}
})

def send_discord(embed):
    payload = {"username": "Bybit Railway Bot", "embeds": [embed]}
    try:
        requests.post(DISCORD_WEBHOOK, json=payload, timeout=10)
    except Exception as e:
        print(f"Error Discord: {e}")

def monitor():
    print("🚀 Railway Bot Started: Monitoring Bybit Funding & Mispricing...")
    while True:
        try:
            tickers = exchange.fetch_tickers()
            for symbol, data in tickers.items():
                if ':USDT' not in symbol: continue

                # 1. Cek Funding Rate
                funding = data.get('info', {}).get('fundingRate')
                if funding:
                    fr_pct = float(funding) * 100
                    if abs(fr_pct) >= FUNDING_THRESHOLD:
                        send_discord({
                            "title": f"🚨 HIGH FUNDING: {symbol}",
                            "color": 0xFF0000,
                            "fields": [{"name": "Rate", "value": f"{fr_pct:.4f}%", "inline": True}]
                        })

                # 2. Cek Mispricing (Mark vs Index)
                mark = data.get('markPrice')
                idx = data.get('indexPrice')
                if mark and idx:
                    diff = abs(mark - idx) / idx * 100
                    if diff >= MISPRICING_THRESHOLD:
                        send_discord({
                            "title": f"⚖️ MISPRICING: {symbol}",
                            "color": 0xFFFF00,
                            "fields": [
                                {"name": "Gap", "value": f"{diff:.2f}%", "inline": True},
                                {"name": "Mark", "value": str(mark), "inline": True},
                                {"name": "Index", "value": str(idx), "inline": True}
                            ]
                        })
            
            # Flush log agar terlihat di Railway dashboard
            print(f"✅ Heartbeat: Checked at {time.strftime('%H:%M:%S')}", flush=True)
            time.sleep(60) 

        except Exception as e:
            print(f"❌ Error: {e}", flush=True)
            time.sleep(30)

if __name__ == "__main__":
    monitor()
