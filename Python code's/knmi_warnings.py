import logging
import os
import sys
import requests
import json
import asyncio
import discord

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(os.environ.get("LOG_LEVEL", logging.INFO))

STATE_FILE = "last_file.txt"


# =========================
# KNMI API
# =========================
class OpenDataAPI:
    def __init__(self, api_token: str):
        self.base_url = "https://api.dataplatform.knmi.nl/open-data/v1"
        self.headers = {"Authorization": api_token}

    def __get_data(self, url, params=None):
        return requests.get(url, headers=self.headers, params=params).json()

    def list_files(self, dataset_name: str, dataset_version: str, params: dict):
        return self.__get_data(
            f"{self.base_url}/datasets/{dataset_name}/versions/{dataset_version}/files",
            params=params,
        )

    def get_file_url(self, dataset_name: str, dataset_version: str, file_name: str):
        return self.__get_data(
            f"{self.base_url}/datasets/{dataset_name}/versions/{dataset_version}/files/{file_name}/url"
        )


def read_file_from_temporary_download_url(download_url):
    try:
        r = requests.get(download_url)
        r.raise_for_status()
        return r.text
    except Exception:
        logger.exception("Unable to read file")
        sys.exit(1)


# =========================
# STATE MANAGEMENT
# =========================
def get_last_processed():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return f.read().strip()
    return None


def set_last_processed(filename):
    with open(STATE_FILE, "w") as f:
        f.write(filename)


# =========================
# DISCORD BOT
# =========================
async def send_to_discord(message: str):
    token = os.environ.get("DISCORD_WARNING_BOT")
    channel_id = int(os.environ.get("DISCORD_WARNING_CHANNEL"))

    if not token or not channel_id:
        logger.error("Discord token of channel ID ontbreekt")
        return

    intents = discord.Intents.default()
    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        logger.info(f"Ingelogd als {client.user}")

        channel = client.get_channel(channel_id)

        if not channel:
            logger.error("Kanaal niet gevonden")
            await client.close()
            return

        # Split berichten (Discord max 2000 chars)
        chunks = [message[i:i+2000] for i in range(0, len(message), 2000)]

        for chunk in chunks:
            await channel.send(chunk)

        await client.close()

    await client.start(token)


# =========================
# MAIN
# =========================
def main():
    api_key = os.environ.get("KNMI_API_KEY")
    dataset_name = "waarschuwingen_nederland_48h"
    dataset_version = "1.0"

    if not api_key:
        logger.error("Geen API key gevonden")
        sys.exit(1)

    logger.info("Fetching KNMI data...")

    api = OpenDataAPI(api_token=api_key)

    params = {"maxKeys": 1, "orderBy": "created", "sorting": "desc"}
    response = api.list_files(dataset_name, dataset_version, params)

    if "error" in response:
        logger.error(f"API error: {response['error']}")
        sys.exit(1)

    latest_file = response["files"][0].get("filename")
    logger.info(f"Latest file: {latest_file}")

    last_file = get_last_processed()

    if latest_file == last_file:
        logger.info("Geen nieuwe data")
        return

    logger.info("Nieuwe data gevonden!")

    response = api.get_file_url(dataset_name, dataset_version, latest_file)
    file_content = read_file_from_temporary_download_url(
        response["temporaryDownloadUrl"]
    )

    # =========================
    # DIRECTE OUTPUT (PLATE TEKST)
    # =========================
    text = file_content  # geen JSON parsing meer

    # naar Discord sturen
    asyncio.run(send_to_discord(text))

    # opslaan zodat geen duplicaten
    set_last_processed(latest_file)


if __name__ == "__main__":
    main()
