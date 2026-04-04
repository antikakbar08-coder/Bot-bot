def send_discord_alert(title, description, color, category, market_slug):
    """Mengirim notifikasi ke Discord dengan logo kategori yang jelas"""
    webhook = DiscordWebhook"https://discord.com/api/webhooks/1489799903361372313/vhtfgVrueL8j0ziJB7gwSkTw97gjP4pz5qiajrOsQ_1b7omwWLCraXsFo4l1rlCwsTkX"
    
    # Menentukan logo berdasarkan kategori
    if category.upper() == "SPORTS":
        category_logo = "🏆 SPORTS" # Anda bisa ganti dengan emoji bola jika suka, misal: ⚽ SPORTS
    elif category.upper() == "POLITICS":
        category_logo = "🏛️ POLITICS"
    else:
        category_logo = f"🔔 {category.upper()}" # Default jika kategori lain

    # Membuat format link market
    market_url = f"https://polymarket.com/event/{market_slug}"
    
    # Pemisah visual
    separator = "------------------------------------------"
    
    # Gabungkan deskripsi dengan link di bagian bawah
    # Menambahkan emoji 🚨 di judul utama agar menarik perhatian
    clean_description = f"{separator}\n{description}\n{separator}\n🔗 [Lihat Market]({market_url})"
    
    embed = DiscordEmbed(
        title=f"🚨 {category_logo} OPPORTUNITY FOUND!", # Logo dimasukkan di sini
        description=clean_description,
        color=color
    )
    
    embed.set_timestamp()
    webhook.add_embed(embed)
    webhook.execute()
