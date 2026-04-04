import requests
import time

# --- KONFIGURASI ---
WEBHOOK_URL = "URL_WEBHOOK_DISCORD_ANDA"
MIN_PROFIT_THRESHOLD = 0.02  # Notif jika harga total < 0.98 (Profit 2%)
POLL_INTERVAL = 10           # Cek setiap 10 detik

class PolySportsBot:
    def __init__(self):
        self.gamma_url = "https://gamma-api.polymarket.com/markets"
        self.clob_url = "https://clob.polymarket.com/book"

    def get_active_sports_markets(self):
        """Mengambil market olahraga yang sedang aktif (Tag ID 100381 adalah Sports)"""
        params = {
            "active": "true",
            "closed": "false",
            "tag_id": "100381", # ID umum untuk kategori Sports
            "limit": 10
        }
        try:
            res = requests.get(self.gamma_url, params=params)
            return res.json()
        except:
            return []

    def get_market_price(self, token_id):
        """Mengambil harga Best Bid (harga jual terbaik saat ini)"""
        try:
            res = requests.get(self.clob_url, params={"token_id": token_id})
            data = res.json()
            if data['bids']:
                return float(data['bids'][0]['price'])
            return None
        except:
            return None

    def check_arbitrage(self):
        print("🔎 Mencari peluang di pasar Sports...")
        markets = self.get_active_sports_markets()
        
        for m in markets:
            # Polymarket biasanya punya 2 outcome: YES (index 0) dan NO (index 1)
            # Atau Team A vs Team B
            outcomes = m.get('clobTokenIds') 
            if not outcomes or len(outcomes) < 2:
                continue

            token_yes = eval(outcomes)[0]
            token_no = eval(outcomes)[1]

            price_yes = self.get_market_price(token_yes)
            price_no = self.get_market_price(token_no)

            if price_yes and price_no:
                total_prob = price_yes + price_no
                print(f"Market: {m['question']} | Total: {total_prob:.3f}")

                # Jika total < 1, berarti ada "Negative Hold" (Peluang Profit)
                if total_prob < (1.0 - MIN_PROFIT_THRESHOLD):
                    self.send_alert(m['question'], price_yes, price_no, total_prob)

    def send_alert(self, question, p_yes, p_no, total):
        profit = round((1 - total) * 100, 2)
        payload = {
            "content": f"🚨 **SPORT ARBITRAGE DETECTED** 🚨\n"
                       f"🏀 **Event:** {question}\n"
                       f"✅ YES: {p_yes} | ❌ NO: {p_no}\n"
                       f"📊 Total Prob: {round(total, 3)}\n"
                       f"💰 Est. Profit: {profit}%"
        }
        requests.post(WEBHOOK_URL, json=payload)

if __name__ == "__main__":
    bot = PolySportsBot()
    while True:
        try:
            bot.check_arbitrage()
        except Exception as e:
            print(f"Error: {e}")
        time.sleep(POLL_INTERVAL)
