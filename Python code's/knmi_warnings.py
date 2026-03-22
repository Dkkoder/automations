import logging
import os
import sys
import requests

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(os.environ.get("LOG_LEVEL", logging.INFO))

STATE_FILE = "last_file.txt"


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
        logger.exception("Unable to read file using download URL")
        sys.exit(1)


# 👉 STATE MANAGEMENT
def get_last_processed():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return f.read().strip()
    return None


def set_last_processed(filename):
    with open(STATE_FILE, "w") as f:
        f.write(filename)


def main():
    api_key = os.environ.get("KNMI_API_KEY")
    dataset_name = "waarschuwingen_nederland_48h"
    dataset_version = "1.0"

    if not api_key:
        logger.error("Geen API key gevonden")
        sys.exit(1)

    logger.info(f"Fetching latest file of {dataset_name} version {dataset_version}")

    api = OpenDataAPI(api_token=api_key)

    params = {"maxKeys": 1, "orderBy": "created", "sorting": "desc"}
    response = api.list_files(dataset_name, dataset_version, params)

    if "error" in response:
        logger.error(f"Unable to retrieve list of files: {response['error']}")
        sys.exit(1)

    latest_file = response["files"][0].get("filename")
    logger.info(f"Latest file is: {latest_file}")

    last_file = get_last_processed()

    if latest_file == last_file:
        logger.info("Geen nieuwe file, stoppen.")
        return

    logger.info("Nieuwe file gevonden!")

    response = api.get_file_url(dataset_name, dataset_version, latest_file)
    file_content = read_file_from_temporary_download_url(response["temporaryDownloadUrl"])

    # 👉 HIER DOE JE JE POST (Twitter, Discord, etc.)
    print(file_content)

    # sla op zodat we geen duplicaten krijgen
    set_last_processed(latest_file)


if __name__ == "__main__":
    main()
