import http.client
import urllib.request
import urllib.parse
import json


class ApiError(Exception):

    def __init__(self, message):
        self.message = message


def _check_for_errors(response: http.client.HTTPResponse):
    content_type = response.getheader("Content-Type", "")

    if "application/json" not in content_type:
        raise ApiError("Did not receive JSON response when opening path:\n" + response.geturl())


def get(api_key: str, path: str, **kwargs) -> dict:
    kwargs["api_key"] = api_key
    response = urllib.request.urlopen(path + "?" + urllib.parse.urlencode(kwargs))
    _check_for_errors(response)

    content_charset = response.info().get_content_charset("utf-8")
    return json.loads(response.read().decode(content_charset))

