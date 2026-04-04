import requests

def ambil_data_polymarket():
    # Mengambil data khusus kategori Sports yang masih aktif
    url = "https://gamma-api.polymarket.com/markets"
    query_params = {
        "tag": "Sports",
        "active": "true",
        "closed": "false",
        "limit": 15
    }

    try:
        response = requests.get(url, params=query_params)
        data_pasar = response.json()

        print(f"{'PERTANDINGAN / MARKET':<55} | {'HARGA (USD)':<12} | {'PERSENTASE'}")
        print("-" * 85)

        for market in data_pasar:
            nama = market.get('question', 'Tidak ada nama')
            
            # Mengambil harga outcome (biasanya index 0 adalah opsi utama/Yes)
            try:
                # Harga di API dalam string list, contoh: ["0.65", "0.35"]
                prices = eval(market.get('outcomePrices', '["0", "0"]'))
                harga_usd = float(prices[0])
                persentase = harga_usd * 100

                # Format tampilan agar rapi
                nama_pendek = (nama[:52] + '..') if len(nama) > 52 else nama
                print(f"{nama_pendek:<55} | ${harga_usd:<11.2f} | {persentase:>6.1f}%")
            except:
                continue

    except Exception as e:
        print(f"Gagal mengambil data: {e}")

if __name__ == "__main__":
    print("DATA HARGA DAN PERSENTASE SPORTS POLYMARKET\n")
    ambil_data_polymarket()
