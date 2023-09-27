from __future__ import annotations
import base64
import datetime
import json

import requests

from app.exceptions.custom_exceptions import NotLoggedInException

if __name__ == "__main__":
    AUTH_FILE_PATH = "../conf/client.json"
else:
    AUTH_FILE_PATH = "conf/client.json"


class SpotifyAuth:
    client_id: str
    client_secret: str

    user_auth_uri: str = "https://accounts.spotify.com/authorize"
    o_auth_uri: str = "https://accounts.spotify.com/api/token"
    user_profile_uri = ""

    access_scope: str = " ".join(
        ["user-modify-playback-state", "playlist-read-private", "user-read-playback-state", "playlist-modify-private",
         "playlist-modify-public"])
    access_token: str
    refresh_token: str
    expires_by: float

    def __init__(self):
        with open(AUTH_FILE_PATH) as client_auth_file:
            client_auth = json.load(client_auth_file)
            self.client_id = client_auth["client_id"]
            self.client_secret = client_auth["client_secret"]

    def to_json(self) -> str:
        json_data = {key: value for key, value in self.__dict__.items() if key not in ["client_secret", "client_id"]}
        return json.dumps(json_data)

    @staticmethod
    def from_json(json_str: str) -> SpotifyAuth:
        auth_obj = SpotifyAuth()
        json_data = json.loads(json_str)
        for key, value in json_data.items():
            auth_obj.__dict__[key] = value
        return auth_obj

    def authorize(self, auth_code: str, redirect_to: str):
        params = {"code": auth_code, "redirect_uri": redirect_to, "grant_type": 'authorization_code'}
        return self._authorize(params)

    def refresh_authorization(self):
        params = {"refresh_token": self.refresh_token, "grant_type": 'refresh_token'}
        return self._authorize(params)

    def _authorize(self, params):
        # Build authorization request
        basic_auth = base64.urlsafe_b64encode(f"{self.client_id}:{self.client_secret}".encode()).decode()
        basic_auth = "Basic " + basic_auth
        auth_header = {"Authorization": basic_auth}
        self.expires_by = datetime.datetime.now().timestamp()

        # Execute request
        response = requests.post(self.o_auth_uri, data=params, headers=auth_header)

        # Error handling
        if response.status_code != 200:
            print(f"{response.status_code}\n{response.content}")
            raise NotLoggedInException("Something went wrong trying to authorize")

        # Process response
        body = response.json()
        self.access_token = body["access_token"]
        if "refresh_token" in body:
            self.refresh_token = body["refresh_token"]
        self.expires_by += body["expires_in"]
        return self.access_token

    def auth_valid(self) -> bool:
        if "expires_by" not in self.__dict__:
            raise NotLoggedInException("expires_by not a field in auth object")
        if not self.expires_by:
            raise NotLoggedInException("expires_by not set in auth object")
        return datetime.datetime.now().timestamp() <= self.expires_by

    def get_auth_header(self):
        if not self.auth_valid():
            self.refresh_authorization()
        return {"Authorization": f"Bearer {self.access_token}"}
