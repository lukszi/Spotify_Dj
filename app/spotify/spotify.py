from __future__ import annotations

import time
from typing import List, Optional

import requests
from requests import Response

from app.exceptions.custom_exceptions import NotLoggedInException, RateLimitedException
from app.session import SpotifyAuth
from app.spotify.model import PlayList, Track, TrackFeatures
from app.spotify.model.track import TrackSection


class Spotify:
    # Auth stuff
    auth: SpotifyAuth
    user_id: Optional[str] = None

    # API URIs
    api_base_uri = "https://api.spotify.com/v1/"

    def __init__(self, auth: Optional[SpotifyAuth] = None):
        if auth is None:
            auth = SpotifyAuth()
        self.auth = auth

    def authorize(self, auth_code: str, redirect_to: str):
        self.auth.authorize(auth_code, redirect_to)

    def get_user_id(self, retry: bool = True) -> str:
        """
        Get the user id of the logged in user

        :param retry: When True retries the request after refreshing the auth token
        """
        if not self.user_id:
            auth_header = self.auth.get_auth_header()
            response = requests.get(self.api_base_uri + "me", headers=auth_header)

            # Catch errors
            if response.status_code == 401:
                if retry:
                    self.auth.refresh_authorization()
                    return self.get_user_id(retry=False)
                else:
                    raise NotLoggedInException("User is not logged in")
            if response.status_code == 429:
                raise RateLimitedException
            if response.status_code != 200:
                raise Exception(f"Something went wrong trying to get user_id, status code: "
                                f"{response.status_code}\n{response.content}")

            self.user_id = response.json()["id"]
        return self.user_id

    def get_first_and_last_section_analysis(self, tracks: List[Track]):
        """
        Get the first and last section analysis of a track
        """
        for track in tracks:
            auth_header = self.auth.get_auth_header()
            fields = "fields=sections"
            uri = f"{self.api_base_uri}audio-analysis/{track.id}?{fields}"

            response: Optional[Response] = None
            while response is None:
                response = requests.get(uri, headers=auth_header)
                if response.status_code == 429:
                    response = None
                    time.sleep(3)
                    continue
                if response.status_code != 200:
                    raise Exception(f"Something went wrong trying to get the audio analysis of a track: "
                                    f"{response.status_code}\n{response.content}")

            body = response.json()
            sections = body["sections"]
            first_section = sections[0]
            last_section = sections[-1]
            track.section_analysis = (TrackSection(loudness=first_section["loudness"], tempo=first_section["tempo"]),
                                      TrackSection(loudness=last_section["loudness"], tempo=last_section["tempo"]))

    def get_playlists(self) -> List[PlayList]:
        """
        Get all playlists of the logged in user
        :return: All playlists of a user without the contained tracks
        """
        auth_header = self.auth.get_auth_header()
        next_uri = f"{self.api_base_uri}me/playlists"

        playlists: List[PlayList] = []
        while next_uri is not None:
            response = requests.get(next_uri, headers=auth_header)
            if response.status_code != 200:
                raise Exception(f"Something went wrong trying to read the playlists: "
                                f"{response.status_code}\n{response.content}")
            body = response.json()
            items = body["items"]
            next_uri = body["next"]

            for item in items:
                playlist = PlayList(name=item["name"], p_id=item["id"], tracks_ref=item["tracks"]["href"])
                playlists.append(playlist)

        return playlists

    def get_tracks(self, playlist_id: str) -> List[Track]:
        """
        Get all tracks of a playlist

        :param playlist_id: id of the playlist
        :return: List of all playlist tracks
        """
        auth_header = self.auth.get_auth_header()

        tracks: List[Track] = []
        track_fields = "fields=items(added_at, added_by, track(name, href, id)),next"
        next_uri = f"{self.api_base_uri}playlists/{playlist_id}/tracks?{track_fields}"
        # Iterate over all pages of tracks
        while next_uri is not None:
            response = requests.get(next_uri, headers=auth_header)

            # Error handling
            if response.status_code != 200:
                raise Exception(f"Something went wrong trying to read the tracks from a playlist: "
                                f"{response.status_code}\n{response.content}")

            # Add each track in page to list
            body = response.json()
            next_uri = body["next"]
            for api_track in body["items"]:
                track: Track = Track()

                api_track = api_track["track"]
                track.id = api_track["id"]
                track.name = api_track["name"]
                track.href = api_track["href"]
                # filter out tracks that have since been deleted
                if track.id:
                    tracks.append(track)

        return tracks

    def get_audio_features(self, tracks: List[Track]):
        """
        Fetch and initialize the audio features for a given list of tracks
        """

        features: List = []
        i = 0
        while i < len(tracks) - 1:
            track_ids = ",".join([track.id for track in tracks[i:min(i + 100, len(tracks))]])
            i += 100
            auth_header = self.auth.get_auth_header()
            uri = f"{self.api_base_uri}audio-features?ids={track_ids}"

            response = requests.get(uri, headers=auth_header)
            if response.status_code != 200:
                raise Exception(f"Something went wrong trying to read the audio features from a track: "
                                f"{response.status_code}\n{response.content}")

            # Process features into the corresponding tracks
            body = response.json()
            features += body["audio_features"]

        for feature in features:
            track_id = feature["id"]
            filtered_tracks = list(filter(lambda track: track.id == track_id, tracks))
            if len(filtered_tracks) == 0:
                raise Exception(f"Track with id {track_id} not found in feature responses")
            feature_object = TrackFeatures(acousticness=feature["acousticness"],
                                           danceability=feature["danceability"],
                                           energy=feature["energy"],
                                           instrumentalness=feature["instrumentalness"],
                                           valence=feature["valence"])

            for track in filtered_tracks:
                track.features = feature_object

    def get_playlist(self, playlist_id) -> PlayList:
        """
        Fetches a single playlist by id
        :return: Playlist that has id playlist_id, without contained tracks
        """
        auth_header = self.auth.get_auth_header()
        uri = f"{self.api_base_uri}playlists/{playlist_id}"

        response = requests.get(uri, headers=auth_header)
        if response.status_code != 200:
            raise Exception(f"Something went wrong trying to read the playlists: "
                            f"{response.status_code}\n{response.content}")
        playlist_response = response.json()
        playlist: PlayList = PlayList(name=playlist_response["name"], p_id=playlist_response["id"],
                                      tracks_ref=playlist_response["tracks"]["href"])
        return playlist

    def execute_request(self, api_request) -> any:
        """
        Executes a simple get request to the spotify api and returns the json response
        """
        auth_header = self.auth.get_auth_header()
        print(f"auth: {auth_header['Authorization']}")
        uri = f"{self.api_base_uri}{api_request}"
        response = requests.get(uri, auth_header)
        if response.status_code != 200:
            raise Exception(f"Request failed: "
                            f"{response.status_code}\n{response.content}")
        return response.json()

    def queue_tracks_in_order(self, tracks: List[Track]):
        """
        Queues a list of tracks in their given order. Only works with spotify premium though
        """
        auth_header = self.auth.get_auth_header()
        uri = f"{self.api_base_uri}me/player/queue?uri="
        for track in tracks:
            request = uri + track.href
            response = requests.post(request, headers=auth_header)
            if response.status_code != 204:
                raise Exception(f"Something went wrong trying to queue a track: "
                                f"{response.status_code}\n{response.content}")

    def create_playlist(self, name: str, tracks: Optional[List[Track]] = None, check_if_name_exists: bool = True) \
            -> PlayList:
        """
        Creates a new playlist with the given name and then adds tracks
        :param check_if_name_exists: If true checks whether a playlist with the given name already exists and returns it
        :return: Created playlist or pre-existing playlist
        """
        if tracks is None:
            tracks = []

        if check_if_name_exists:
            playlists = self.get_playlists()
            pre_existing_lists = list(filter(lambda o: o.name == name, playlists))
            if len(pre_existing_lists) > 0:
                return pre_existing_lists[0]

        auth_header = self.auth.get_auth_header()
        uri = f"{self.api_base_uri}users/{self.get_user_id()}/playlists"
        body = {
            "name": name
        }
        response = requests.post(uri, headers=auth_header, json=body)
        if response.status_code != 201:
            raise Exception(f"Something went wrong trying to create a playlist: "
                            f"{response.status_code}\n{response.content}")

        playlist_response = response.json()
        playlist: PlayList = PlayList(name=playlist_response["name"], p_id=playlist_response["id"],
                                      tracks_ref=playlist_response["tracks"]["href"])

        playlist.tracks = tracks
        self.add_tracks_to_playlist(playlist, tracks)
        return playlist

    def add_tracks_to_playlist(self, playlist: PlayList, tracks: List[Track]):
        """
        Adds a list of tracks to a playlist
        """
        if len(tracks) == 0:
            return

        uri = f"{self.api_base_uri}playlists/{playlist.id}/tracks"
        auth_header = self.auth.get_auth_header()

        # iterate over all tracks in chunks of 100
        for i in range(0, len(tracks), 100):
            track_uris = [f"spotify:track:{track.id}" for track in tracks[i:min(i + 100, len(tracks))]]
            body = {
                "uris": track_uris
            }

            response = requests.post(uri, headers=auth_header, json=body)

            if response.status_code != 201:
                raise Exception(f"Something went wrong trying to add tracks to a playlist: "
                                f"{response.status_code}\n{response.content}")

    def fetch_and_initialize_playlist(self: Spotify, playlist_id: str) -> PlayList:
        """
        Fetches all songs in a playlist, and initializes both the audio features and the first and last section analysis
        """
        playlist: PlayList = self.get_playlist(playlist_id)
        tracks: List[Track] = self.get_tracks(playlist_id)
        playlist.tracks = tracks
        self.get_audio_features(tracks)
        self.get_first_and_last_section_analysis(tracks)
        return playlist
