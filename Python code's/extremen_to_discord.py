import discord
import requests
from io import BytesIO
from datetime import datetime
import pytz
import os

TOKEN = os.environ['DISCORD_EXTREMEN_BOT']
CHANNEL_ID = int(os.environ['DISCORD_EXTREMEN_CHANNEL'])

urls = [
    "https://true.infoplaza.io/gdata/10min/GMT_TXTX_latest.png",
    "https://true.infoplaza.io/gdata/10min/GMT_TNTN_latest.png",
    "https://true.infoplaza.io/gdata/10min/GMT_TN10_latest.png",
    "https://true.infoplaza.io/gdata/10min/GMT_FFFX_latest.png",
    "https://true.infoplaza.io/gdata/10min/GMT_FXFX_latest.png",
    "https://true.infoplaza.io/gdata/10min/GMT_RRRX_latest.png"
]

intents = discord.Intents.default()
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'Logged on as {client.user}')
    channel = client.get_channel(CHANNEL_ID)
    if channel is None:
        print("Kanaal niet gevonden!")
        return

    nl_tz = pytz.timezone("Europe/Amsterdam")
    now = datetime.now(nl_tz)
    timestamp = now.strftime('%Y%m%d%H%M%S')

    files = []
    for url in urls:
        # Voeg timestamp toe om caching te voorkomen
        url_with_timestamp = f"{url}?t={timestamp}"
        response = requests.get(url_with_timestamp)
        if response.status_code == 200:
            filename = url.split('/')[-1]
            files.append(discord.File(BytesIO(response.content), filename=filename))

    # Voeg optioneel een bericht toe met datum en tijd
    await channel.send(content=f"Actuele kaarten {now.strftime('%d-%m-%Y %H:%M')}", files=files)
    await client.close()

client.run(TOKEN)
