import requests
import time

# --- CONFIGURATION ---
WEBHOOK_URL = "https://discord.com/api/webhooks/1489799903361372313/vhtfgVrueL8j0ziJB7gwSkTw97gjP4pz5qiajrOsQ_1b7omwWLCraXsFo4l1rlCwsTkX"
CHECK_INTERVAL = 120  # Cek setiap 2 menit
REPORT_INTERVAL = 300 # Laporan rutin setiap 5 menit
THRESHOLD = 0.03      # Notifikasi jika total harga menyimpang > 3% (Mispricing)
MAX_SPAM = 3          # Maksimal notifikasi per market

# Filter Kata Kunci News & Sports
TARGET_KEYWORDS = ["war", "election", "president", "iran", "israel", "russia", "usa", 
                   "vs", "win", "cup", "nba", "fifa", "champions", "league", "oil", "btc"]

alert_tracker = {} 
last_report_time = time.time()

def send_discord(content):
    try:
        requests.post(WEBHOOK_URL, json={"content": content})
    except Exception as e:
        print(f"Gagal kirim Webhook: {e}")

def is_target_market(question):
    question_lower = question.lower()
    return any(word in question_lower for word in TARGET_KEYWORDS)

def check_polymarket():
    global last_report_time
    # Ambil 50 market aktif terbaru
    url = "https://gamma-api.polymarket.com/markets?active=true&closed=false&limit=50"
    top_picks = []

    try:
        response = requests.get(url)
        markets = response.json()

        for market in markets:
            question = market.get('question', '')
            
            # Filter kategori
            if not is_target_market(question):
                continue

            m_id = market.get('id')
            prices = market.get('outcomePrices')
            
            if prices and len(prices) >= 2:
                p_yes = float(prices[0]) * 100
                p_no = float(prices[1]) * 100
                total = p_yes + p_no
                diff = abs(100 - total)

                # Simpan data untuk laporan rutin 5 menit
                top_picks.append(f"📌 {question[:45]}... (**{total:.1f}%**)")

                # LOGIKA NOTIFIKASI MISPRICING (INSTAN)
                if diff > (THRESHOLD * 100):
                    count = alert_tracker.get(m_id, 0)
                    if count < MAX_SPAM:
                        alert_msg = (
                            f"⚡ **NEWS/SPORTS MISPRICING DETECTED!**\n"
                            f"**Market:** {question}\n"
                            f"━━━━━━━━━━━━━━━━━━━━\n"
                            f"✅ **Probabilitas YES:** `{p_yes:.1f}%` \n"
                            f"❌ **Probabilitas NO:** `{p_no:.1f}%` \n"
                            f"📈 **Total Market Cap:** `{total:.1f}%` (Deviasi: {diff:.1f}%)\n"
                            f"━━━━━━━━━━━━━━━━━━━━\n"
                            f"🤖 *Notif ke: {count + 1}/{MAX_SPAM} (Reset tiap 5 mnt)*\n"
                            f"🔗 [BUKA POLYMARKET](https://polymarket.com/event/{market.get('slug')})"
                        )
                        send_discord(alert_msg)
                        alert_tracker[m_id] = count + 1
        
        # LOGIKA LAPORAN RUTIN (5 MENIT)
        current_time = time.time()
        if current_time - last_report_time >= REPORT_INTERVAL:
            summary_text = "\n".join(top_picks[:10]) # Ambil 10 teratas
            report_msg = (
                f"📋 **LAPORAN RUTIN 5 MENIT (NEWS & SPORTS)**\n"
                f"Status: **Monitoring Aktif**\n\n"
                f"**Sampel Persentase Market Terpantau:**\n{summary_text}\n"
                f"\n*Sistem baru saja me-reset tracker spam.*"
            )
            send_discord(report_msg)
            
            alert_tracker.clear() # Reset tracker spam
            last_report_time = current_time

    except Exception as e:
        print(f"Error Koneksi: {e}")

if __name__ == "__main__":
    print("🚀 Bot Polymarket News/Sports Berjalan...")
    print(f"Target: {', '.join(TARGET_KEYWORDS)}")
    
    # Notif awal saat bot jalan
    send_discord("✅ **Bot Polymarket News & Sports Berhasil Dijalankan!**\nMonitoring setiap 2 menit...")
    
    while True:
        check_polymarket()
        time.sleep(CHECK_INTERVAL)
