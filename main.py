import time
import requests
import os
from discord_webhook import DiscordWebhook, DiscordEmbed

# --- KONFIGURASI ---
# Webhook URL Anda
DISCORD_URL = "https://discord.com/api/webhooks/1489799903361372313/vhtfgVrueL8j0ziJB7gwSkTw97gjP4pz5qiajrOsQ_1b7omwWLCraXsFo4l1rlCwsTkX"

# Target Profit (%)
MIN_PROFIT = 30
MAX_PROFIT = 100

def send_discord_alert(category, title, price, fair_price, profit, slug):
    """Mengirim notifikasi ke Discord dengan format rapi dan logo"""
    try:
        # Inisialisasi Webhook dengan format yang benar (pakai kurung)
        webhook = DiscordWebhook(url=DISCORD_URL)
        
        # Penentuan Warna & Logo
        category_lower = category.lower()
        if any(x in category_lower for x in ["sport", "nba", "soccer", "football"]):
            color = "ff9900" # Oranye untuk Sports
            logo = "🏆 SPORTS"
        else:
            color = "03b2f8" # Biru untuk Politics
            logo = "🏛️ POLITICS"

        market_url = f"https://polymarket.com/event/{slug}"
        separator = "------------------------------------------"
        
        # Format isi pesan
        content = (
            f"{separator}\n"
            f"**Market:** {title}\n\n"
            f"**Harga Saat Ini:** ${price:.2f}\n"
            f"**Harga Wajar:** ${fair_price:.2f}\n"
            f"**Potensi Profit:** 🔥 `{profit:.2f}%`\n"
            f"{separator}\n"
            f"🔗 [Lihat Market]({market_url})"
        )

        embed = DiscordEmbed(
            title=f"🚨 {logo} OPPORTUNITY FOUND!",
            description=content,
            color=color
        )
        embed.set_timestamp()
        webhook.add_embed(embed)
        
        # Eksekusi kirim
        webhook.execute()
        print(f"[✓] Berhasil kirim: {title[:30]}... ({profit:.2f}%)")

    except Exception as e:
        print(f"[!] Gagal kirim ke Discord: {e}")

def scan_markets():
    """Mengambil data dari Polymarket Gamma API"""
    print(f"[*] Scanning Markets... ({time.strftime('%H:%M:%S')})")
    try:
        # Ambil 100 market aktif terbaru
        url = "https://gamma-api.polymarket.com/markets?active=true&limit=100"
        response = requests.get(url, timeout=15)
        
        if response.status_code != 200:
            print(f"[!] API Error: {response.status_code}")
            return

        markets = response.json()
        
        for m in markets:
            # 1. FILTER KATEGORI (Politics & Sports)
            cat_name = m.get('groupItemTitle', 'Unknown')
            cat_lower = cat_name.lower()
            
            target_keywords = ["politics", "election", "sports", "nba", "soccer", "football", "baseball"]
            if not any(x in cat_lower for x in target_keywords):
                continue

            # Ambil harga
            prices = m.get('outcomePrices')
            if not prices:
                continue
            
            current_price = float(prices[0])
            
            # 2. LOGIKA MISPRICING (Simulasi Fair Price)
            # Anda bisa menyesuaikan angka 0.85 ini sebagai target 'exit' Anda
            fair_price = 0.85 
            
            if 0.05 < current_price < 0.75:
                # Rumus Profit
                profit_pct = ((fair_price - current_price) / current_price) * 100
                
                # 3. FILTER PERSENTASE PROFIT (30% - 100%)
                if MIN_PROFIT <= profit_pct <= MAX_PROFIT:
                    send_discord_alert(
                        category=cat_name,
                        title=m.get('question', 'No Title'),
                        price=current_price,
                        fair_price=fair_price,
                        profit=profit_pct,
                        slug=m.get('slug', '')
                    )
                    
    except Exception as e:
        print(f"[!] Error saat scan: {e}")

# --- JALANKAN BOT ---
if __name__ == "__main__":
    print("=== POLYMARKET MONITOR ACTIVE (RAILWAY) ===")
    print(f"Filter: Politics & Sports | Profit: {MIN_PROFIT}%-{MAX_PROFIT}%")
    
    while True:
        try:
            scan_markets()
            print(f"[*] Selesai. Reset dalam 30 detik...")
            print("-" * 30)
            time.sleep(30) # RESET SETIAP 30 DETIK
        except Exception as e:
            print(f"[!!] Terjadi kesalahan kritis: {e}")
            time.sleep(10)
