import ccxt
import time
from discord_webhook import DiscordWebhook, DiscordEmbed

class JoBtcScanner:
    def __init__(self):
        # Inisialisasi Exchange (Gate.io sangat bagus untuk koin ekosistem BTC baru)
        self.exchange = ccxt.gateio({'enableRateLimit': True})
        
        # URL Webhook yang kamu berikan
        self.webhook_url = "https://discord.com/api/webhooks/1489799903361372313/vhtfgVrueL8j0ziJB7gwSkTw97gjP4pz5qiajrOsQ_1b7omwWLCraXsFo4l1rlCwsTkX"
        
        # Parameter Filter
        self.keywords = ['btc', 'bitcoin', 'satoshi', 'ordi', 'sats', 'merl', 'stx']
        self.max_price = 0.01          # Harga masih minim/murah
        self.min_volume_24h = 50000    # Indikasi holder/aktivitas besar ($50k+)
        
        # Kontrol Notifikasi
        self.alert_history = {}        # Melacak jumlah alert per koin
        self.last_status_time = time.time()
        self.scan_interval = 120       # 2 menit
        self.status_interval = 300     # 5 menit

    def send_to_discord(self, title, message, color="f2a900"):
        try:
            webhook = DiscordWebhook(url=self.webhook_url)
            embed = DiscordEmbed(title=title, description=message, color=color)
            embed.set_timestamp()
            webhook.add_embed(embed)
            webhook.execute()
        except Exception as e:
            print(f"Gagal kirim ke Discord: {e}")

    def run_scan(self):
        print(f"[{time.strftime('%H:%M:%S')}] Memindai market...")
        try:
            tickers = self.exchange.fetch_tickers()
            found_any = False

            for symbol, data in tickers.items():
                # Filter hanya pasangan USDT
                if '/USDT' in symbol:
                    base = symbol.split('/')[0].lower()
                    price = data.get('last', 0)
                    volume = data.get('quoteVolume', 0)

                    # Logika: Nama mengandung unsur BTC + Harga Murah + Volume Cukup
                    if any(key in base for key in self.keywords):
                        if 0 < price <= self.max_price and volume >= self.min_volume_24h:
                            
                            # Limit Maksimal 3x Notifikasi per koin
                            count = self.alert_history.get(symbol, 0)
                            if count < 3:
                                self.alert_history[symbol] = count + 1
                                found_any = True
                                
                                content = (
                                    f"**Koin:** {symbol}\n"
                                    f"**Harga:** {price:.8f}\n"
                                    f"**Volume 24h:** ${volume:,.2f}\n"
                                    f"**Notifikasi:** {self.alert_history[symbol]}/3"
                                )
                                self.send_to_discord(f"🚀 Potensi BTC-Proxy Terdeteksi!", content)
                                print(f"✅ Alert dikirim: {symbol}")
            
            return found_any

        except Exception as e:
            print(f"Error saat scan: {e}")
            return False

    def start(self):
        print("Bot Jo BTC Scanner Aktif...")
        while True:
            found = self.run_scan()
            current_time = time.time()

            # Jika tidak ada koin baru, kirim status setiap 5 menit agar tahu bot tidak mati
            if not found:
                if current_time - self.last_status_time >= self.status_interval:
                    self.send_to_discord("📡 Status Bot", "Bot aktif memantau, belum ada koin baru sesuai kriteria.", color="808080")
                    self.last_status_time = current_time
                    print("📢 Mengirim status report ke Discord.")

            time.sleep(self.scan_interval)

if __name__ == "__main__":
    bot = JoBtcScanner()
    bot.start()
