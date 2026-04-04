import requests
import time

# --- KONFIGURASI ---
WEBHOOK_URL = "https://discord.com/api/webhooks/1489799903361372313/vhtfgVrueL8j0ziJB7gwSkTw97gjP4pz5qiajrOsQ_1b7omwWLCraXsFo4l1rlCwsTkX"
MIN_PROFIT_THRESHOLD = 0.03  # Notif jika profit > 3%
JEDA_PER_MARKET = 60         # Jeda 60 detik (1 menit) antar setiap sport

class PolySportsBot:
    def __init__(self):
        self.gamma_url = "https://gamma-api.polymarket.com/markets"
        self.clob_url = "https://clob.polymarket.com/book"

    def get_active_sports_markets(self):
        params = {
            "active": "true",
            "closed": "false",
            "tag_id": "100381", # Kategori Sports
            "limit": 50
        }
        try:
            res = requests.get(self.gamma_url, params=params)
            return res.json()
        except:
            return []

    def get_market_price(self, token_id):
        try:
            res = requests.get(self.clob_url, params={"token_id": token_id})
            data = res.json()
            if data.get('bids') and len(data['bids']) > 0:
                return float(data['bids'][0]['price'])
            return None
        except:
            return None

    def send_alert(self, question, p_yes, p_no, total):
        profit = round((1 - total) * 100, 2)
        # Menambahkan baris kosong (\n\n) agar pesan di Discord memiliki jarak
        pesan = (
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🚨 **SPORT ARBITRAGE DETECTED** 🚨\n\n"
            f"🏀 **Event:**\n`{question}`\n\n"
            f"✅ **YES:** `{p_yes}`\n"
            f"❌ **NO:** `{p_no}`\n\n"
            f"📊 **Total Prob:** `{round(total, 3)}`\n"
            f"💰 **Est. Profit:** `{profit}%`\n\n"
            f"━━━━━━━━━━━━━━━━━━━━"
        )
        payload = {"content": pesan}
        requests.post(WEBHOOK_URL, json=payload)
        print(f"[{time.strftime('%H:%M:%S')}] Notifikasi dikirim untuk: {question[:30]}...")

    def monitor(self):
        print("Bot mulai berjalan. Mencari peluang...")
        while True:
            markets = self.get_active_sports_markets()
            
            for m in markets:
                outcomes = m.get('clobTokenIds')
                if not outcomes: continue
                
                token_ids = eval(outcomes) if isinstance(outcomes, str) else outcomes
                if len(token_ids) < 2: continue

                price_yes = self.get_market_price(token_ids[0])
                price_no = self.get_market_price(token_ids[1])

                if price_yes and price_no:
                    # Filter agar tidak ambil harga sampah 0.001
                    if price_yes > 0.01 and price_no > 0.01:
                        total_prob = price_yes + price_no
                        
                        if total_prob < (1.0 - MIN_PROFIT_THRESHOLD):
                            self.send_alert(m['question'], price_yes, price_no, total_prob)
                            
                            # JEDA 1 MENIT SETIAP KALI MENEMUKAN PELUANG
                            print(f"Menunggu {JEDA_PER_MARKET} detik sebelum cek sport berikutnya...")
                            time.sleep(JEDA_PER_MARKET)
                
            print("Scan list selesai, mengulang dari awal...")
            time.sleep(10)

if __name__ == "__main__":
    bot = PolySportsBot()
    bot.monitor()
