import time
import requests
from discord_webhook import DiscordWebhook, DiscordEmbed

# --- KONFIGURASI ---
# Ganti dengan URL Webhook Anda jika berbeda
WEBHOOK_URL = "https://discord.com/api/webhooks/1489799903361372313/vhtfgVrueL8j0ziJB7gwSkTw97gjP4pz5qiajrOsQ_1b7omwWLCraXsFo4l1rlCwsTkX"

# Target Profit (%)
MIN_PROFIT = 30
MAX_PROFIT = 100

def send_discord_alert(category, title, price, fair_price, profit, slug):
    """Mengirim notifikasi ke Discord dengan pemisah dan logo"""
    try:
        webhook = DiscordWebhook(url=WEBHOOK_URL)
        
        # Penentuan Warna dan Logo berdasarkan Kategori
        if "sport" in category.lower():
            color = "ff9900" # Oranye untuk Sports
            logo = "🏆 SPORTS"
        else:
            color = "03b2f8" # Biru untuk Politics
            logo = "🏛️ POLITICS"

        market_url = f"https://polymarket.com/event/{slug}"
        separator = "------------------------------------------"
        
        # Body Pesan dengan persentase profit yang jelas
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
        webhook.execute()
        print(f"[✓] Alert Terkirim: {title[:40]}... ({profit:.2f}%)")

    except Exception as e:
        print(f"[!] Gagal mengirim ke Discord: {e}")

def scan_markets():
    print(f"[*] Scanning Markets... ({time.strftime('%H:%M:%S')})")
    try:
        # Mengambil data market aktif (Limit 100 untuk stabilitas)
        url = "https://gamma-api.polymarket.com/markets?active=true&limit=100"
        response = requests.get(url, timeout=10)
        
        if response.status_code != 200:
            print(f"[!] API Error: {response.status_code}")
            return

        markets = response.json()
        
        for m in markets:
            # 1. FILTER KATEGORI (Hanya Politik & Sports)
            cat_name = m.get('groupItemTitle', 'Unknown')
            if not any(x in cat_name.lower() for x in ["politics", "election", "sports", "nba", "soccer", "football"]):
                continue

            # Ambil harga (Outcome 0 biasanya 'Yes' atau opsi utama)
            prices = m.get('outcomePrices')
            if not prices: continue
            
            current_price = float(prices[0])
            
            # 2. LOGIKA PERHITUNGAN PROFIT
            # Di sini kita asumsikan 'Fair Price' adalah harga target (misal 0.85)
            # Anda bisa mengganti angka 0.85 dengan logika prediksi Anda sendiri
            fair_price = 0.85 
            
            if 0.05 < current_price < 0.80:
                # Rumus Profit: ((Target - Harga) / Harga) * 100
                profit_pct = ((fair_price - current_price) / current_price) * 100
                
                # 3. FILTER PRESENTASE (30% - 100%)
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

# --- LOOP UTAMA (Reset 30 Detik) ---
if __name__ == "__main__":
    print("=== BOT POLYMARKET POLITIC & SPORT STARTED ===")
    print(f"Filter Profit: {MIN_PROFIT}% - {MAX_PROFIT}% | Reset: 30s")
    
    while True:
        try:
            scan_markets()
            print(f"[*] Scan selesai. Reset dalam 30 detik...")
            print("="*50)
            time.sleep(30) # DELAY 30 DETIK PER RESET
        except KeyboardInterrupt:
            print("\n[!] Bot dimatikan.")
            break
        except Exception as e:
            print(f"[!!] Terjadi kesalahan kritis: {e}")
            time.sleep(10)
