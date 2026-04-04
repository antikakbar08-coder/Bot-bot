import requests
import json
import time
import os

# URL Webhook Discord Anda
WEBHOOK_URL = "https://discord.com/api/webhooks/1489799903361372313/vhtfgVrueL8j0ziJB7gwSkTw97gjP4pz5qiajrOsQ_1b7omwWLCraXsFo4l1rlCwsTkX"

def get_dynamic_emoji(text):
    text = text.lower()
    # Deteksi Politik
    politics_keywords = ["election", "president", "senate", "biden", "trump", "politics", "harris"]
    if any(word in text for word in politics_keywords):
        return "🔥"
    # Deteksi Olahraga
    if "soccer" in text or "football" in text or "premier league" in text: return "⚽"
    if "basketball" in text or "nba" in text: return "🏀"
    if "tennis" in text: return "🎾"
    if "ufc" in text or "mma" in text or "boxing" in text: return "🥊"
    if "baseball" in text or "mlb" in text: return "⚾"
    return "🏆"

def translate_simple(text):
    translations = {"Will": "Apakah", "win": "menang", "match": "pertandingan", "against": "melawan"}
    for eng, ind in translations.items():
        text = text.replace(eng, ind).replace(eng.lower(), ind)
    return text

def ambil_dan_kirim():
    # Bersihkan layar terminal setiap kali update (Reset tampilan)
    os.system('cls' if os.name == 'nt' else 'clear')
    print("🔄 [TEST MODE] Mengambil data terbaru dari Polymarket...")
    
    url = "https://gamma-api.polymarket.com/markets"
    params = {"active": "true", "closed": "false", "limit": 5}

    try:
        res = requests.get(url, params=params)
        markets = res.json()

        pesan = "## 🧪 TEST MODE: UPDATE 30 DETIK\n"
        pesan += "--- \n"

        for m in markets:
            judul = translate_simple(m.get('question', 'N/A'))
            emoji = get_dynamic_emoji(m.get('question', ''))
            try:
                prices = json.loads(m.get('outcomePrices', '["0", "0"]'))
                harga_yes = float(prices[0])
                pesan += f"{emoji} **{judul}**\n┗ 💵 `${harga_yes:.2f}` | 📈 `{harga_yes*100:.1f}%` \n\n"
            except: continue

        # Kirim ke Discord
        requests.post(WEBHOOK_URL, json={"content": pesan})
        print("✅ Berhasil dikirim ke Discord!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 Bot Testing dimulai (Update tiap 30 detik)...")
    try:
        while True:
            ambil_dan_kirim()
            print(f"⏳ Menunggu 30 detik untuk refresh berikutnya...")
            time.sleep(30) # Delay 30 detik
    except KeyboardInterrupt:
        print("\n🛑 Bot dimatikan oleh pengguna.")
