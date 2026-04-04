import requests
import json

# URL Webhook Discord Anda
WEBHOOK_URL = "https://discord.com/api/webhooks/1489799903361372313/vhtfgVrueL8j0ziJB7gwSkTw97gjP4pz5qiajrOsQ_1b7omwWLCraXsFo4l1rlCwsTkX"

def get_dynamic_emoji(text):
    """Menentukan emoji berdasarkan kategori olahraga atau politik"""
    text = text.lower()
    
    # Deteksi Politik
    politics_keywords = ["election", "president", "senate", "biden", "trump", "politics", "governor", "minister"]
    if any(word in text for word in politics_keywords):
        return "🔥"
    
    # Deteksi Olahraga
    if "soccer" in text or "football" in text or "premier league" in text:
        return "⚽"
    if "basketball" in text or "nba" in text:
        return "🏀"
    if "tennis" in text:
        return "🎾"
    if "ufc" in text or "mma" in text or "boxing" in text:
        return "🥊"
    if "baseball" in text or "mlb" in text:
        return "⚾"
    if "f1" in text or "racing" in text:
        return "🏎️"
    if "cricket" in text:
        return "🏏"
    
    # Default jika tidak terdeteksi
    return "🏆"

def translate_simple(text):
    translations = {
        "Will": "Apakah",
        "win": "menang",
        "match": "pertandingan",
        "won": "menang",
        "against": "melawan",
        "to win": "akan menang",
    }
    translated = text
    for eng, ind in translations.items():
        translated = translated.replace(eng, ind).replace(eng.lower(), ind)
    return translated

def send_to_discord(content):
    payload = {
        "username": "Polymarket Monitor 📊",
        "content": content
    }
    header = {"Content-Type": "application/json"}
    try:
        response = requests
