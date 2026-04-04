import requests
import json

# URL Webhook yang Anda berikan
WEBHOOK_URL = "https://discord.com/api/webhooks/1489799903361372313/vhtfgVrueL8j0ziJB7gwSkTw97gjP4pz5qiajrOsQ_1b7omwWLCraXsFo4l1rlCwsTkX"

def send_to_discord(content):
    """Mengirim pesan ke Discord dengan format JSON yang benar."""
    payload = {
        "username": "Polymarket Sports Bot",
        "content": content
    }
    header = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(WEBHOOK_URL, data=json.dumps(payload), headers=header)
        
        # Discord memberikan status 204 No Content jika sukses mengirim webhook
        if response.status_code == 204:
            print("✅ Berhasil: Pesan telah terkirim ke Discord.")
        else:
            print(f"❌ Gagal: Discord merespon dengan status {response.status_code}")
            print(f"Detail: {response.text}")
    except Exception as e:
        print(f"❌ Error Koneksi: {e}")

def ambil_data_polymarket():
    print("Sedang mengambil data dari Polymarket...")
    url = "https://gamma-api.polymarket.com/markets"
    params = {
        "tag": "Sports",
        "active": "true",
        "closed": "false",
        "limit": 8  # Mengambil 8 pertandingan terbaru
    }

    try:
        res = requests.get(url, params=params)
        markets = res.json()

        if not markets:
            print("Tidak ada data market sports yang ditemukan.")
            return

        # Menyusun pesan untuk Discord
        pesan = "## 🏆 UPDATE HARGA SPORTS POLYMARKET\n"
        pesan += "--- \n"

        for m in markets:
            judul = m.get('question', 'N/A')
            try:
                # Mengambil harga (outcomePrices dalam format string list)
                prices = json.loads(m.get('outcomePrices', '["0", "0"]'))
                harga_yes = float(prices[0])
                persentase = harga_yes * 100
                
                pesan += f"> **{judul}**\n"
                pesan += f"> Harga: `${harga_yes:.2f}` | Peluang: `{persentase:.1f}%` \n\n"
            except:
                continue

        # Kirim ke Discord
        send_to_discord(pesan)

    except Exception as e:
        print(f"Terjadi kesalahan saat ambil data: {e}")

if __name__ == "__main__":
    ambil_data_polymarket()
