import discord
import requests
from io import BytesIO
from datetime import datetime
import pytz
import os

TOKEN = os.environ['DISCORD_PLUIMEN_BOT']
CHANNEL_ID = int(os.environ['DISCORD_PLUIMEN_CHANNEL'])

client = discord.Client(intents=discord.Intents.default())

# Bepaal NL-tijd
nl_tz = pytz.timezone("Europe/Amsterdam")
now = datetime.now(nl_tz)

# Runtime
run_time = "0z" if now.hour < 12 else "12z"

# Unix timestamp om caching te voorkomen
timestamp = int(now.timestamp())

pluimen_to_send = [
    {
        "title": "ECMWF De Bilt",
        "links": [
            "https://true.infoplaza.io/gdata/eps/eps_pluim_tt_06260.png",
            "https://true.infoplaza.io/gdata/eps/eps_pluim_snow_06260.png"
        ]
    },
    {
        "title": "ECMWF Den Helder (De Kooy)",
        "links": [
            "https://true.infoplaza.io/gdata/eps/eps_pluim_tt_06235.png",
            "https://true.infoplaza.io/gdata/eps/eps_pluim_snow_06235.png"
        ]
    },
    {
        "title": "ECMWF Groningen (Eelde)",
        "links": [
            "https://true.infoplaza.io/gdata/eps/eps_pluim_tt_06280.png",
            "https://true.infoplaza.io/gdata/eps/eps_pluim_snow_06280.png"
        ]
    },
    {
        "title": "ECMWF Leeuwarden",
        "links": [
            "https://true.infoplaza.io/gdata/eps/eps_pluim_tt_06270.png",
            "https://true.infoplaza.io/gdata/eps/eps_pluim_snow_06270.png"
        ]
    },
    {
        "title": "ECMWF Maastricht (Beek)",
        "links": [
            "https://true.infoplaza.io/gdata/eps/eps_pluim_tt_06380.png",
            "https://true.infoplaza.io/gdata/eps/eps_pluim_snow_06380.png"
        ]
    },
    {
        "title": "ECMWF Schiphol",
        "links": [
            "https://true.infoplaza.io/gdata/eps/eps_pluim_tt_06240.png",
            "https://true.infoplaza.io/gdata/eps/eps_pluim_snow_06240.png"
        ]
    },
    {
        "title": "ECMWF Twente",
        "links": [
            "https://true.infoplaza.io/gdata/eps/eps_pluim_tt_06290.png",
            "https://true.infoplaza.io/gdata/eps/eps_pluim_snow_06290.png"
        ]
    },
    {
        "title": "ECMWF Vlissingen",
        "links": [
            "https://true.infoplaza.io/gdata/eps/eps_pluim_tt_06310.png",
            "https://true.infoplaza.io/gdata/eps/eps_pluim_snow_06310.png"
        ]
    }
]


@client.event
async def on_ready():
    print(f'Logged in als {client.user}')
    channel = client.get_channel(CHANNEL_ID)

    for message in pluimen_to_send:
        files = []
        for i, url in enumerate(message["links"]):
            # Voeg timestamp toe om caching te voorkomen
            url_with_timestamp = f"{url}?t={timestamp}"
            resp = requests.get(url_with_timestamp)
            if resp.status_code == 200:
                files.append(discord.File(BytesIO(resp.content), filename=f"{message['title']}_{i + 1}.png"))

        # Voeg runtime toe naast de titel
        await channel.send(content=f"{message['title']} {now.strftime('%d-%m-%Y')} {run_time}", files=files)

    await client.close()  # sluit de bot af na posten


client.run(TOKEN)
