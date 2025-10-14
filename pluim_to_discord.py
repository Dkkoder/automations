import os
import requests
from datetime import datetime
import pytz

# Webhook URL uit GitHub Secret
WEBHOOK_URL = os.environ["DISCORD_WEBHOOK_URL"]

# Lijst van afbeeldingen + bijbehorende locaties
images = [
    ("https://true.infoplaza.io/gdata/eps/eps_pluim_tt_06260.png", "De Bilt"),
    ("https://true.infoplaza.io/gdata/eps/eps_pluim_tt_06235.png", "Den Helder"),
    ("https://true.infoplaza.io/gdata/eps/eps_pluim_tt_06280.png", "Groningen"),
    ("https://true.infoplaza.io/gdata/eps/eps_pluim_tt_06270.png", "Leeuwarden"),
    ("https://true.infoplaza.io/gdata/eps/eps_pluim_tt_06380.png", "Maastricht"),
    ("https://true.infoplaza.io/gdata/eps/eps_pluim_tt_06240.png", "Schiphol"),
    ("https://true.infoplaza.io/gdata/eps/eps_pluim_tt_06290.png", "Twente"),
    ("https://true.infoplaza.io/gdata/eps/eps_pluim_tt_06310.png", "Vlissingen")
]

# Bepaal NL-tijd
nl_tz = pytz.timezone("Europe/Amsterdam")
now = datetime.now(nl_tz)

# Zet tekst afhankelijk van tijdstip
run_time = "0z" if now.hour < 12 else "12z"

# Maak embeds voor elke afbeelding
embeds = []
for url, location in images:
    embeds.append({
        "title": location,
        "image": {"url": f"{url}?t={now.strftime('%Y%m%d%H%M%S')}"}
    })

# Payload
payload = {
    "content": f"ECMWF Pluim {now.strftime('%d-%m-%Y')} {run_time}",
    "embeds": embeds
}

# Versturen naar Discord
resp = requests.post(WEBHOOK_URL, json=payload)

if resp.status_code == 204:
    print("✅ Afbeeldingen succesvol gepost naar Discord!")
else:
    print(f"❌ Fout: {resp.status_code} - {resp.text}")

#woeliewoelie
