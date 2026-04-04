def send_to_discord(matches, is_urgent=False):
    now = datetime.now().strftime("%H:%M:%S")
    
    if matches:
        fields = []
        for coin in matches:
            # Tentukan logo dan keterangan berdasarkan nilai
            if coin['raw_val'] > 0:
                mark = "➕ PLUS"
                emoji = "📈"
            else:
                mark = "➖ MINUS"
                emoji = "📉"
            
            fields.append({
                "name": f"{emoji} {coin['symbol']} ({mark})",
                "value": f"**Funding:** `{coin['funding_rate_pct']}`\n**Price:** `${coin['price']}`",
                "inline": True
            })

        payload = {
            "username": "Binance Live Monitor",
            "embeds": [{
                "title": "🚨 ALERT: FUNDING EKSTRIM (>1.5% / <-1.5%)",
                "description": f"Terdeteksi pada pukul `{now}`",
                "color": 15158332, 
                "fields": fields[:25],
                "footer": {"text": "Monitoring 24/7 Binance Futures"}
            }]
        }
    else:
        payload = {
            "username": "Binance Live Monitor",
            "embeds": [{
                "description": f"✅ **Laporan Rutin {now}:** Tidak ada koin di ambang 1.5%.",
                "color": 3066993,
            }]
        }

    try:
        requests.post(DISCORD_WEBHOOK_URL, json=payload)
    except Exception as e:
        print(f"Error Discord: {e}")

def check_funding():
    try:
        response = requests.get(BINANCE_URL, timeout=15)
        data = response.json()
        matches = []
        
        for item in data:
            if 'lastFundingRate' not in item: continue
            
            funding_pct = float(item['lastFundingRate']) * 100
            mark_price = float(item.get('markPrice', 0))
            
            # LOGIKA: Di atas 1.5% atau di bawah -1.5%
            if funding_pct >= 1.5 or funding_pct <= -1.5:
                # Tambahkan tanda + secara manual untuk string jika angka positif
                prefix = "+" if funding_pct > 0 else ""
                
                matches.append({
                    "symbol": item['symbol'], 
                    "funding_rate_pct": f"{prefix}{funding_pct:.4f}%",
                    "price": f"{mark_price:,.4f}",
                    "raw_val": funding_pct 
                })
        return matches
    except Exception as e:
        print(f"Error Binance: {e}")
        return []
