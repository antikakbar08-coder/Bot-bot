import ccxt
import requests
import time
import os

# ========================================================
# 🟢 TEMPAT MENAMBAHKAN WEBHOOK BARU
# Silakan masukkan link webhook Discord Anda di dalam tanda kurung [ ]
# Contoh: "https://discord.com/api/webhooks/..."
# ========================================================
MY_WEBHOOKS = [ "https://discord.com/api/webhooks/1489799903361372313/vhtfgVrueL8j0ziJB7gwSkTw97gjP4pz5qiajrOsQ_1b7omwWLCraXsFo4l1rlCwsTkX
    # Masukkan link webhook baru di sini
"]
# ========================================================

# --- DAFTAR KOIN MEME BYBIT ---
MEME_COINS = [
    'DOGE', 'SHIB', 'PEPE', 'WIF', 'BONK', 'FLOKI', 
    'MEME', 'BOME', '1000PEPE', 'TURBO', 'BABYDOGE',
    'MYRO', '1000LUNC', '1000RATS', '1000SATS'
]

# --- AMBANG BATAS NOTIFIKASI ---
FUNDING_LOW = -2.0   # Notifikasi jika Funding Fee <= -2%
FUNDING_HIGH = 20.0  # Notifikasi jika Funding Fee >= 20%

# Inisialisasi Bursa Bybit
exchange = ccxt.bybit({
    'enableRateLimit': True,
    'options': {'defaultType': 'linear'}
})

def broadcast_discord(embed):
    """Mengirim pesan ke semua webhook yang terdaftar"""
    if not MY_WEBHOOKS:
        print("⚠️ Peringatan: Belum ada Webhook yang diisi di MY_WEBHOOKS!", flush=True)
        return

    payload = {
        "username": "Bybit Meme Hunter",
        "avatar_url": "https://i.imgur.com/8nLsn7V.png",
        "embeds": [embed]
    }
    
    for url in MY_WEBHOOKS:
        try:
            if "discord.com" in url:
                requests.post(url, json=payload, timeout=10)
        except Exception as e:
            print(f"❌ Gagal mengirim ke salah satu webhook: {e}")

def start_monitor():
    print(f"🚀 Bot Railway Aktif. Memantau {len(MEME_COINS)} Koin Meme...", flush=True)
    while True:
        try:
            # Mengambil data harga dan funding terbaru
            tickers = exchange.fetch_tickers()
            
            for symbol, data in tickers.items():
                # Filter: Hanya USDT Perpetual & Ada dalam daftar koin meme
                if ':USDT' in symbol and any(m in symbol for m in MEME_COINS):
                    
                    info = data.get('info', {})
                    funding = info.get('fundingRate')
                    
                    if funding:
                        fr_pct = float(funding) * 100
                        
                        # Cek apakah melewati ambang batas -2% atau +20%
                        if fr_pct <= FUNDING_LOW or fr_pct >= FUNDING_HIGH:
                            warna = 0x00FFFF if fr_pct < 0 else 0xFF00FF
                            
                            embed = {
                                "title": f"🔔 MEME FUNDING ALERT: {symbol}",
                                "url": f"https://www.bybit.com/en/trade/futures/usdt/{symbol.replace(':USDT', '')}",
                                "color": warna,
                                "fields": [
                                    {"name": "Funding Rate", "value": f"**{fr_pct:.4f}%**", "inline": True},
                                    {"name": "Aksi", "value": "Short Diuntungkan" if fr_pct > 0 else "Long Diuntungkan", "inline": True},
                                ],
                                "footer": {"text": "Railway Engine • 24/7 Analysis"}
                            }
                            broadcast_discord(embed)
                            print(f"✅ Alert terkirim: {symbol} ({fr_pct:.2f}%)", flush=True)

            # Jeda 60 detik agar tidak terkena rate limit API
            time.sleep(60)

        except Exception as e:
            print(f"❌ Error Sistem: {e}", flush=True)
            time.sleep(30)

if __name__ == "__main__":
    start_monitor()
