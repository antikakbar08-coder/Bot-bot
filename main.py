import os
import time
import requests
from datetime import datetime

# --- CONFIGURATION ---
# Webhook URL Discord Anda
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1489799903361372313/vhtfgVrueL8j0ziJB7gwSkTw97gjP4pz5qiajrOsQ_1b7omwWLCraXsFo4l1rlCwsTkX"

# Tracker untuk membatasi maksimal 3 notifikasi per event/koin yang sama
# Disimpan di luar loop agar data tidak hilang setiap pengecekan
notification_tracker = {}

# Simulasi data dari Polymarket & CCXT
def get_arbitrage_data():
    # Contoh data sesuai format yang Anda kirim tadi
    return [
        {
            "sport": "baseball",
            "event": "Cleveland Guardians vs Detroit Tigers",
            "market": "Win 2026 World Series",
            "yes_odds": 0.001,
            "no_odds": 0.001,
            "total_prob": 0.002,
            "profit": 99.8
        },
        {
            "sport": "soccer",
            "event": "World Cup 2026 - Winner",
            "market": "Indonesia win World Cup",
            "yes_odds": 0.05,
            "no_odds": 0.85,
            "total_prob": 0.90,
            "profit": 10.0
        }
    ]

def send_to_discord(item):
    # Identitas unik koin/event
    event_id = item['event']
    
    # Ambil jumlah pengiriman sebelumnya (default 0)
    already_sent = notification_tracker.get(event_id, 0)
    
    # --- LOGIKA PEMBATASAN MAKSIMAL 3 NOTIFIKASI ---
    if already_sent >= 3:
        print(f"   [SKIP] {event_id} sudah dikirim {already_sent} kali. Melewati pengiriman.")
        return

    # Pilih emoji berdasarkan jenis olahraga
    emoji = "⚾" if item['sport'] == "baseball" else "⚽"
    
    # Format pesan Embed sesuai codingan awal Anda
    payload = {
        "embeds": [{
            "title": "🚨 SPORT ARBITRAGE DETECTED 🚨",
            "description": f"Notifikasi ke-{already_sent + 1} dari batas 3x.",
            "color": 15158332, # Warna Merah
            "fields": [
                {
                    "name": f"{emoji} Event",
                    "value": f"**{item['event']}**\n*{item['market']}*",
                    "inline": False
                },
                {
                    "name": "📊 Market Odds",
                    "value": f"✅ **YES:** `{item['yes_odds']}`  |  ❌ **NO:** `{item['no_odds']}`",
                    "inline": False
                },
                {
                    "name": "📈 Total Prob",
                    "value": f"`{item['total_prob']}`",
                    "inline": True
                },
                {
                    "name": "💰 Est. Profit",
                    "value": f"**{item['profit']}%**",
                    "inline": True
                }
            ],
            "footer": {
                "text": f"Polymarket Monitoring • {datetime.now().strftime('%H:%M:%S')}"
            }
        }]
    }
    
    try:
        # Mengirim ke Discord Webhook
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=15)
        
        # Jika berhasil (status 204), update tracker
        if response.status_code == 204:
            notification_tracker[event_id] = already_sent + 1
            print(f"   [SENT] {event_id} berhasil dikirim ({notification_tracker[event_id]}/3)")
        else:
            print(f"   [ERROR] Discord API Error: {response.status_code}")
            
    except Exception as e:
        print(f"   [CRITICAL] Gagal koneksi ke Discord: {e}")

def main():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 🚀 Monitoring 24 Jam Aktif...")
    
    while True:
        try:
            # Pengecekan data tetap berjalan normal setiap siklus
            print(f"\n--- Memulai Pengecekan Rutin ({datetime.now().strftime('%H:%M:%S')}) ---")
            data = get_arbitrage_data()
            
            for item in data:
                send_to_discord(item)
                # Jeda singkat antar pesan agar tidak terkena rate limit Discord
                time.sleep(2)
            
            # Jeda antar pengecekan diubah menjadi 10 MENIT (600 detik)
            print(f"Siklus selesai. Menunggu 10 menit untuk pengecekan berikutnya...")
            time.sleep(600)
            
        except KeyboardInterrupt:
            print("\nProgram dihentikan oleh user.")
            break
        except Exception as e:
            # Jika ada error internet, bot tidak mati, tunggu 1 menit lalu coba lagi
            print(f"⚠️ Terjadi error: {e}")
            time.sleep(60)

if __name__ == "__main__":
    main()
