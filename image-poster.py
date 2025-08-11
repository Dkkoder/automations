import os
import requests

# Webhook URL uit GitHub Secret
WEBHOOK_URL = os.environ["DISCORD_WEBHOOK_URL"]

# Afbeelding die je wilt posten
image_url = "https://cdn.knmi.nl/knmi/map/page/weer/actueel-weer/temperatuur.png"

# Bericht + afbeelding via embed
payload = {
    "content": "KNMI Temperatuurkaart 🌡️",
    "embeds": [
        {
            "image": {"url": image_url}
        }
    ]
}

# Versturen naar Discord
resp = requests.post(WEBHOOK_URL, json=payload)

if resp.status_code == 204:
    print("✅ Afbeelding succesvol gepost naar Discord!")
else:
    print(f"❌ Fout: {resp.status_code} - {resp.text}")
