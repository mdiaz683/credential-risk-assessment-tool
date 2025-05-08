from pathlib import Path
import json
from typing import List, Literal
import pandas as pd
import requests


class Telemetrio:
    """
    Telemetr.io API Client

    :param api_key: API Key
    :type api_key: str
    """

    def __init__(self, api_key) -> None:
        self.base_url = "https://api.telemetr.io/v1/"
        self._api_key = api_key

    def _build_url(self, endpoint):
        return self.base_url + endpoint

    def _build_headers(self):
        return {
            "accept": "application/json",
            "x-api-key": self._api_key,
        }

    def _call(self, url, headers, params):
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()

    def get_channel_info(self, intenal_id: str) -> dict:
        """
        Get Channel info by channel internal id

        :param intenal_id: Chat internal id
        :type intenal_id: str
        :return: Channel info
        :rtype: dict
        """
        url = self._build_url("channels/info")
        headers = self._build_headers()
        return self._call(url, headers, {"internal_id": intenal_id})

    def get_channel_stats(self, intenal_id: str) -> dict:
        """
        Get Channel Statistics

        :param intenal_id: Chat internal id
        :type intenal_id: str
        :return: Channel statistics
        :rtype: dict
        """
        url = self._build_url("channels/stats")
        headers = self._build_headers()
        return self._call(url, headers, {"internal_id": intenal_id})

    def search_channels(self,
                        term: str,
                        search_in_about: bool = False,
                        peer_type: Literal['Channel', 'Group'] = "Channel",
                        country: str = None,
                        language: str = None,
                        category: str = None,
                        limit: int = 20) -> List[dict]:
        """
        Search Channels.

        Allows searching for channels by name, description, country, language, and category.

        :param term: Search phrase or link to the channel.
        :type term: str
        :param search_in_about: Search in channel description., defaults to False
        :type search_in_about: bool, optional
        :param peer_type: Chat type, defaults to "Channel"
        :type peer_type: Literal['Channel', 'Group'], optional
        :param country: Channel country, defaults to None
        :type country: str, optional
        :param language: Channel language, defaults to None
        :type language: str, optional
        :param category: Channel category id, defaults to None
        :type category: str, optional
        :param limit: Number of results, defaults to 20
        :type limit: int, optional
        :return: 
        :rtype: _type_
        """
        url = self._build_url("channels/search")
        headers = self._build_headers()
        params = {
            "term": term,
            "search_in_about": str(search_in_about).lower(),
            "peer_type": peer_type,
            "country": country,
            "language": language,
            "category": category,
            "limit": limit
        }
        return self._call(url, headers, params)


def get_channel(channel: str, channel_privacities: dict, channel_types: dict):
    """
    Get channel information from the channel database.

    :param channel: Channel name to search for.
    :type channel: str
    :param channel_privacities: Channel privacity dictionary.
    :type channel_privacities: dict
    :param channel_types: Channel type dictionary.
    :type channel_types: dict
    :return: Series with channel information.
    :rtype: pd.Series
    """
    return pd.Series({
        "channel_name": channel,
        "channel_privacity": channel_privacities.get(channel, None),
        "chat_type": channel_types.get(channel, None),
    })


if __name__ == "__name__":
    file_path = Path(__file__).parent.absolute() / "output.csv"
    df = pd.read_csv(file_path)

    # ruta del json
    BASE_DIR = Path(__file__).resolve().parent
    CHANNELS_FILE = BASE_DIR / "channel_det.json"

    # Cargar el archivo JSON con manejo de errores
    try:
        with open(CHANNELS_FILE, "r", encoding="utf-8") as channel_f:
            channel_data = json.load(channel_f)
    except FileNotFoundError:
        print(f"Error: El archivo {CHANNELS_FILE} no existe.")
        channel_data = {}
    except json.JSONDecodeError:
        print(f"Error: El archivo {CHANNELS_FILE} no contiene un JSON válido.")
        channel_data = {}

    channel_to_type = {}
    channel_to_priv = {}

    for chat_type, type in channel_data.items():
        for privacity_type, channels in type.items():
            for channel in channels:
                channel_to_type[channel] = chat_type
                channel_to_priv[channel] = privacity_type

    df[["Channel_privacity", "Chat_type"]] = df['channel'].apply(get_channel)
