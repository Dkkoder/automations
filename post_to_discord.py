import os
import requests
from datetime import datetime
import pytz  # pip install pytz

# Webhook URL uit GitHub Secret
WEBHOOK_URL = os.environ["DISCORD_WEBHOOK_URL"]

# Basis URL van de afbeelding
base_image_url = "https://true.infoplaza.io/gdata/eps/eps_pluim_tt_06260.png"

# Bepaal NL-tijd
nl_tz = pytz.timezone("Europe/Amsterdam")
now = datetime.now(nl_tz)

# Zet tekst afhankelijk van tijdstip
if now.hour < 12:
    run_time = "0z"
else:
    run_time = "12z"

# Voeg cache-busting parameter toe (voorkomt dat Discord oude afbeelding toont)
image_url = f"{base_image_url}?t={now.strftime('%Y%m%d%H%M%S')}"

# Bericht + afbeelding via embed
payload = {
    "content": f"ECMWF Pluim Midden {now.strftime('%d-%m-%Y')} {run_time}",
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