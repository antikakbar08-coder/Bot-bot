import time
import os
from discord_webhook import DiscordWebhook, DiscordEmbed
from polymarket_py import ClobClient

# --- KONFIGURASI ---
WEBHOOK_URL = "https://discord.com/api/webhooks/1489799903361372313/vhtfgVrueL8j0ziJB7gwSkTw97gjP4pz5qiajrOsQ_1b7omwWLCraXsFo4l1rlCwsTkX"

# Inisialisasi Client (Tanpa API Key jika hanya membaca harga publik)
client = ClobClient(host="https://clob.polymarket.com")

def send_alert(category, title, price, fair_price, profit, slug):
    """Mengirim notifikasi ke Discord dengan format rapi"""
    webhook = DiscordWebhook(url=WEBHOOK_URL)
    
    # Pengaturan Visual berdasarkan Kategori
    if category.lower() == "sports":
        color = "ff9900"  # Oranye
        logo = "🏆 SPORTS"
    elif category.lower() == "politics":
        color = "03b2f8"  # Biru
        logo = "🏛️ POLITICS"
    else:
        color = "9b59b6"  # Ungu (Lainnya)
        logo = f"🔔 {category.upper()}"

    market_url = f"https://polymarket.com/event/{slug}"
    separator = "------------------------------------------"
    
    # Isi Pesan
    description = (
        f"{separator}\n"
        f"**Market:** {title}\n\n"
        f"**Price:** ${price:.2f}\n"
        f"**Fair Price:** ${fair_price:.2f}\n"
        f"**Est. Profit:** {profit:.2f}%\n"
        f"{separator}\n"
        f"🔗 [Lihat Market]({market_url})"
    )

    embed = DiscordEmbed(
        title=f"🚨 {logo} OPPORTUNITY FOUND!",
        description=description,
        color=color
    )
    embed.set_timestamp()
    webhook.add_embed(embed)
    
    response = webhook.execute()
    if response.status_code == 200 or response.status_code == 204:
        print(f"[✓] Alert Terkirim: {title[:30]}...")
    else:
        print(f"[!] Gagal kirim Webhook: {response.status_code}")

def scan_polymarket():
    print(f"[*] Memulai scanning pada {time.strftime('%H:%M:%S')}...")
    
    try:
        # Mengambil daftar market aktif
        markets = client.get_markets()
        
        for m in markets:
            # Filter Kategori
            category = m.get('category', 'Unknown')
            if category not in ["Politics", "Sports"]:
                continue

            # Logika Perhitungan Mispricing
            # Catatan: 'fair_price' biasanya didapat dari provider data luar atau rata-rata orderbook
            # Di sini kita simulasikan pengecekan harga terhadap target profit Anda
            current_price = float(m.get('last_trade_price', 0))
            
            # Simulasi Fair Price (Ganti dengan logika prediksi/fair value Anda)
            # Contoh: jika harga 0.40 tapi data statistik bilang harusnya 0.60
            fair_price = m.get('fair_price', current_price * 1.4) 

            if current_price > 0:
                profit_pct = ((fair_price - current_price) / current_price) * 100
                
                # Filter Profit 30% hingga 100%
                if 30 <= profit_pct <= 100:
                    send_alert(
                        category=category,
                        title=m.get('question', 'No Title'),
                        price=current_price,
                        fair_price=fair_price,
                        profit=profit_pct,
                        slug=m.get('market_slug', '')
                    )

    except Exception as e:
        print(f"[!] Error saat scanning: {e}")

# --- LOOP UTAMA (Reset 1 Menit) ---
if __name__ == "__main__":
    print("=== BOT POLYMARKET MISPRICING STARTED ===")
    print(f"Target: Politics & Sports | Profit: 30% - 100%")
    
    while True:
        scan_polymarket()
        
        print(f"[*] Scan Selesai. Reset dalam 60 detik...")
        print("="*50) 
        time.sleep(60) # Jeda 1 menit sebelum scan ulang
