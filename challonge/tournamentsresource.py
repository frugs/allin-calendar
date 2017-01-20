from .api import get


class TournamentsResource():

    def __init__(self, api_key: str, root_path: str):
        self._api_key = api_key
        self._base_path = root_path + "/tournaments"

    def index(self, **kwargs):
        return get(self._api_key, self._base_path + ".json", **kwargs)
