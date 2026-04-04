import requests
import json

# GANTI DENGAN URL WEBHOOK ANDA
WEBHOOK_URL = "https://discord.com/api/webhooks/1489799903361372313/vhtfgVrueL8j0ziJB7gwSkTw97gjP4pz5qiajrOsQ_1b7omwWLCraXsFo4l1rlCwsTkX"

def send_to_webhook(content):
    payload = {"content": content}
    try:
        requests.post(WEBHOOK_URL, json=payload)
    except Exception as e:
        print(f"Gagal mengirim ke Webhook: {e}")

def ambil_dan_kirim_data():
    url = "https://gamma-api.polymarket.com/markets"
    query_params = {
        "tag": "Sports",
        "active": "true",
        "closed": "false",
        "limit": 5  # Diambil 5 saja agar tidak spam di chat
    }

    try:
        response = requests.get(url, params=query_params)
        data_pasar = response.json()

        # Header untuk pesan
        pesan_notif = "**📊 UPDATE HARGA SPORTS POLYMARKET**\n"
        pesan_notif += "--------------------------------------------------\n"

        for market in data_pasar:
            nama = market.get('question', 'Tidak ada nama')
            try:
                prices = json.loads(market.get('outcomePrices', '["0", "0"]'))
                harga_usd = float(prices[0])
                persentase = harga_usd * 100
                
                pesan_notif += f"🏆 **{nama}**\n"
                pesan_notif += f"💰 Harga: `${harga_usd:.2f}` | 📈 Peluang: `{persentase:.1f}%` \n\n"
            except:
                continue

        # Kirim pesan ke terminal dan webhook
        print(pesan_notif)
        send_to_webhook(pesan_notif)
        print("✅ Notifikasi telah dikirim ke Webhook.")

    except Exception as e:
        print(f"Gagal mengambil data: {e}")

if __name__ == "__main__":
    ambil_dan_kirim_data()
