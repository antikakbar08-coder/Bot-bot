import requests
import json
import time
import os

# URL Webhook Discord Anda
WEBHOOK_URL = "https://discord.com/api/webhooks/1489799903361372313/vhtfgVrueL8j0ziJB7gwSkTw97gjP4pz5qiajrOsQ_1b7omwWLCraXsFo4l1rlCwsTkX"

def get_dynamic_emoji(text):
    text = text.lower()
    # Deteksi Politik
    politics_keywords = ["election", "president", "senate", "biden", "trump", "politics", "harris", "white house"]
    if any(word in text for word in politics_keywords):
        return "🔥"
    # Deteksi Olahraga
    if any(word in text for word in ["soccer", "football", "premier", "laliga", "uefa"]): return "⚽"
    if any(word in text for word in ["basketball", "nba", "ncaa"]): return "🏀"
    if "tennis" in text: return "🎾"
    if any(word in text for word in ["ufc", "mma", "boxing"]): return "🥊"
    return "🏆"

def translate_simple(text):
    translations = {"Will": "Apakah", "win": "menang", "match": "pertandingan", "against": "melawan", "to be": "menjadi"}
    for eng, ind in translations.items():
        text = text.replace(eng, ind).replace(eng.lower(), ind)
    return text

def ambil_dan_urutkan():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("🔄 [10 MENIT] Mengambil & Mengurutkan Data Polymarket...")
    
    url = "https://gamma-api.polymarket.com/markets"
    # Mengambil limit lebih banyak agar bisa disaring & diurutkan
    params = {"active": "true", "closed": "false", "limit": 20}

    try:
        res = requests.get(url, params=params)
        markets = res.json()
        
        data_list = []

        for m in markets:
            try:
                prices = json.loads(m.get('outcomePrices', '["0", "0"]'))
                harga_yes = float(prices[0])
                persentase = harga_yes * 100
                judul = translate_simple(m.get('question', 'N/A'))
                emoji = get_dynamic_emoji(m.get('question', ''))
                
                # Simpan ke list untuk diurutkan nanti
                data_list.append({
                    "judul": judul,
                    "harga": harga_yes,
                    "persen": persentase,
                    "emoji": emoji
                })
            except:
                continue

        # PROSES PENGURUTAN (Sorting) dari Persentase Tertinggi ke Terendah
        data_terurut = sorted(data_list, key=lambda x: x['persen'], reverse=True)

        # Susun Pesan Discord
        pesan = "## 📈 TOP PREDIKSI POLYMARKET (TERURUT)\n"
        pesan += "*(Diurutkan dari peluang tertinggi ke terendah)*\n"
        pesan += "--- \n"

        # Ambil 10 teratas setelah diurutkan agar pesan tidak kepanjangan
        for item in data_terurut[:10]:
            pesan += f"{item['emoji']} **{item['judul']}**\n"
            pesan += f"┗ 📊 Peluang: `{item['persen']:.1f}%` | 💵 `${item['harga']:.2f}`\n\n"

        pesan += "--- \n"
        pesan += f"🕒 *Update berikutnya dalam 10 menit...*"

        # Kirim ke Discord
        requests.post(WEBHOOK_URL, json={"content": pesan})
        print(f"✅ Data terurut berhasil dikirim pada {time.strftime('%H:%M:%S')}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 Bot Polymarket Sorted-Mode Aktif!")
    try:
        while True:
            ambil_dan_kirim()
            # Delay 10 Menit (600 detik)
            time.sleep(600)
    except KeyboardInterrupt:
        print("\n🛑 Bot dimatikan.")
