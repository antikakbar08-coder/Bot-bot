import requests
import time

# --- KONFIGURASI ---
WEBHOOK_URL = "https://discord.com/api/webhooks/1489799903361372313/vhtfgVrueL8j0ziJB7gwSkTw97gjP4pz5qiajrOsQ_1b7omwWLCraXsFo4l1rlCwsTkX"
TARGET_PRICE = 0.70          # Target harga 70%
TOLERANCE = 0.05             # Rentang (0.65 - 0.75)
DURASI_RESET = 60            # Reset/Jeda setiap 1 menit (60 detik)

class PolyBotReset:
    def __init__(self):
        self.gamma_url = "https://gamma-api.polymarket.com/markets"
        self.clob_url = "https://clob.polymarket.com/book"

    def get_market_list(self):
        """Mengambil daftar market olahraga terbaru"""
        params = {
            "active": "true",
            "closed": "false",
            "tag_id": "100381", # Kategori Sports
            "limit": 20
        }
        try:
            res = requests.get(self.gamma_url, params=params)
            return res.json()
        except Exception as e:
            print(f"Gagal ambil data market: {e}")
            return []

    def get_price(self, token_id):
        """Mengambil harga bid terbaru dari CLOB"""
        try:
            res = requests.get(self.clob_url, params={"token_id": token_id})
            data = res.json()
            if data.get('bids') and len(data['bids']) > 0:
                return float(data['bids'][0]['price'])
            return None
        except:
            return None

    def send_discord(self, question, p_yes, p_no):
        """Mengirim notifikasi dengan format spasi lebar"""
        header = "✨ **NEW SPORT SIGNAL DETECTED** ✨"
        divider = "▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬"
        
        # Format pesan dengan banyak spasi (Line Breaks)
        content = (
            f"{divider}\n\n"
            f"{header}\n\n\n"
            f"🏀 **EVENT OLAHRAGA:**\n"
            f"`{question}`\n\n\n"
            f"✅ **HARGA YES (PROB):**\n"
            f"> `{p_yes} (Target 70% Zone)`\n\n"
            f"❌ **HARGA NO:**\n"
            f"> `{p_no if p_no else 'N/A'}`\n\n\n"
            f"⏰ **WAKTU SCAN:**\n"
            f"{time.strftime('%d/%m/%Y | %H:%M:%S')}\n\n\n"
            f"{divider}"
        )
        
        try:
            requests.post(WEBHOOK_URL, json={"content": content})
        except Exception as e:
            print(f"Gagal kirim ke Discord: {e}")

    def start_bot(self):
        print(f"Bot Aktif. Sistem akan reset/scan setiap {DURASI_RESET} detik.")
        
        while True:
            print(f"\n[{time.strftime('%H:%M:%S')}] Memulai pemindaian market...")
            markets = self.get_market_list()
            found_count = 0

            for m in markets:
                outcomes = m.get('clobTokenIds')
                if not outcomes: continue
                
                # Konversi string ke list jika perlu
                token_ids = eval(outcomes) if isinstance(outcomes, str) else outcomes
                if len(token_ids) < 1: continue

                # Cek harga YES (Indeks 0)
                price_yes = self.get_price(token_ids[0])
                
                if price_yes:
                    # Filter Harga 70% (0.65 - 0.75)
                    if (TARGET_PRICE - TOLERANCE) <= price_yes <= (TARGET_PRICE + TOLERANCE):
                        price_no = self.get_price(token_ids[1]) if len(token_ids) > 1 else None
                        self.send_discord(m['question'], price_yes, price_no)
                        found_count += 1
                        # Jeda singkat antar pesan agar tidak diblokir Discord
                        time.sleep(1)

            print(f"Scan selesai. Menemukan {found_count} match.")
            print(f"Bot akan istirahat (Reset) selama {DURASI_RESET} detik...")
            
            # --- LOGIKA RESET 1 MENIT ---
            time.sleep(DURASI_RESET)

if __name__ == "__main__":
    bot = PolyBotReset()
    bot.start_bot()
