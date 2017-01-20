from .tournamentsresource import TournamentsResource

ROOT_PATH = "https://api.challonge.com/v1"


class ChallongeService():

    def __init__(self, api_key: str):
        self._tournaments = TournamentsResource(api_key, ROOT_PATH)

    def tournaments(self):
        return self._tournaments


def create_service(api_key: str) -> ChallongeService:
    return ChallongeService(api_key)