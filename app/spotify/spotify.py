from __future__ import annotations

import time
from typing import List, Optional, Protocol

import requests
from requests import Response

from app.exceptions.custom_exceptions import NotLoggedInException, RateLimitedException
from app.session import SpotifyAuth
from app.spotify.database import Database
from app.spotify.model import PlayList, Track, TrackFeatures
from app.spotify.model.track import TrackSection


class Spotify:
    # Auth stuff
    auth: SpotifyAuth
    user_id: Optional[str] = None
    db: Database

    # API URIs
    api_base_uri = "https://api.spotify.com/v1/"

    def __init__(self, auth: Optional[SpotifyAuth] = None):
        if auth is None:
            auth = SpotifyAuth()
        self.auth = auth
        self.database = Database("spotify.db")

    def authorize(self, auth_code: str, redirect_to: str):
        self.auth.authorize(auth_code, redirect_to)

    def get_user_id(self) -> str:
        """
        Get the user id of the logged-in user
        """
        if not self.user_id:
            def request(auth_header: dict[str, str]) -> Response:
                return requests.get(self.api_base_uri + "me", headers=auth_header)

            error_message = "Something went wrong trying to get user_id"
            response = self.__execute_api_request(request, [200], error_message=error_message)

            self.user_id = response.json()["id"]
        return self.user_id

    def get_first_and_last_section_analysis(self, tracks: List[Track]):
        """
        Get the first and last section analysis of a track
        """

        uninitialized_tracks = list(filter(lambda track: track.section_analysis is None, tracks))
        for track in uninitialized_tracks:
            fields = "fields=sections"
            uri = f"{self.api_base_uri}audio-analysis/{track.id}?{fields}"

            def request(auth_header: dict[str, str]) -> Response:
                return requests.get(uri, headers=auth_header)

            error_message = "Something went wrong trying to get the audio analysis of a track"
            response: Response = self.__execute_api_request(request, [200], error_message=error_message)

            body = response.json()
            sections = body["sections"]
            first_section = sections[0]
            last_section = sections[-1]
            track.section_analysis = (TrackSection(loudness=first_section["loudness"], tempo=first_section["tempo"]),
                                      TrackSection(loudness=last_section["loudness"], tempo=last_section["tempo"]))
            self.database.insert_track(track)

    def get_playlists(self) -> List[PlayList]:
        """
        Get all playlists of the logged-in user
        :return: All playlists of a user without the contained tracks
        """
        next_uri = f"{self.api_base_uri}me/playlists"

        playlists: List[PlayList] = []
        while next_uri is not None:

            def request(auth_header: dict[str, str]) -> Response:
                return requests.get(next_uri, headers=auth_header)

            error_message = "Something went wrong trying to read the playlists"
            response = self.__execute_api_request(request, error_message=error_message)

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
        tracks: List[Track] = []
        track_fields = "fields=items(added_at, added_by, track(name, href, id)),next"
        next_uri = f"{self.api_base_uri}playlists/{playlist_id}/tracks?{track_fields}"
        # Iterate over all pages of tracks
        while next_uri is not None:
            def request(auth_header: dict[str, str]) -> Response:
                return requests.get(next_uri, headers=auth_header)

            error_message = "Something went wrong trying to read the tracks from a playlist"
            response = self.__execute_api_request(request, error_message=error_message)

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

        # Initialize tracks with data from database
        self.database.bulk_initialize_tracks(tracks)

        return tracks

    def get_audio_features(self, tracks: List[Track]):
        """
        Fetch and initialize the audio features for a given list of tracks
        """

        features: List = []
        uninitialized_tracks = list(filter(lambda track: track.features is None, tracks))
        i = 0
        while i < len(uninitialized_tracks) - 1:
            track_ids = ",".join([track.id for track in uninitialized_tracks[i:min(i + 100, len(uninitialized_tracks))]])
            i += 100
            uri = f"{self.api_base_uri}audio-features?ids={track_ids}"

            def request(auth_header: dict[str, str]) -> Response:
                return requests.get(uri, headers=auth_header)

            error_message = "Something went wrong trying to get audio features"
            response = self.__execute_api_request(request, error_message=error_message)

            # Process features into the corresponding tracks
            body = response.json()
            features += body["audio_features"]

        for feature in features:
            track_id = feature["id"]
            filtered_tracks = list(filter(lambda track: track.id == track_id, uninitialized_tracks))
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
        uri = f"{self.api_base_uri}playlists/{playlist_id}"

        def request(auth_header: dict[str, str]) -> Response:
            return requests.get(uri, headers=auth_header)

        error_message = "Something went wrong trying to read the playlists"
        response = self.__execute_api_request(request, error_message=error_message)

        playlist_response = response.json()
        playlist: PlayList = PlayList(name=playlist_response["name"], p_id=playlist_response["id"],
                                      tracks_ref=playlist_response["tracks"]["href"])
        return playlist

    def queue_tracks_in_order(self, tracks: List[Track]):
        """
        Queues a list of tracks in their given order. Only works with spotify premium though
        """
        uri = f"{self.api_base_uri}me/player/queue?uri="
        for track in tracks:
            uri = uri + track.href

            def request(auth_header: dict[str, str]) -> Response:
                return requests.post(uri, headers=auth_header)

            error_message = "Something went wrong trying to queue a track"
            _ = self.__execute_api_request(request, [204], error_message=error_message)

    def create_playlist(self, name: str, tracks: Optional[List[Track]] = None, check_if_name_exists: bool = True) \
            -> PlayList:
        """
        Creates a new playlist with the given name and then adds tracks

        :param name: Name of the new playlist
        :param tracks: Tracks to add to the playlist
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

        uri = f"{self.api_base_uri}users/{self.get_user_id()}/playlists"
        body = {
            "name": name
        }

        def request(auth_header: dict[str, str]) -> Response:
            return requests.post(uri, headers=auth_header, json=body)

        error_message = "Something went wrong trying to create a playlist"
        response = self.__execute_api_request(request, [201], error_message=error_message)

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

        # iterate over all tracks in chunks of 100
        for i in range(0, len(tracks), 100):
            track_uris = [f"spotify:track:{track.id}" for track in tracks[i:min(i + 100, len(tracks))]]
            body = {
                "uris": track_uris
            }

            def request(auth_header: dict[str, str]) -> Response:
                return requests.post(uri, headers=auth_header, json=body)

            error_message = "Something went wrong trying to add tracks to a playlist"
            _ = self.__execute_api_request(request, [201], error_message=error_message)

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

    def __execute_api_request(self, request: SpotifyRequest,
                              acceptable_codes=None,
                              max_attempts: int = 10,
                              error_message: str = "Something went wrong trying to execute a Spotify API request") \
            -> Response:
        """
        Executes a Spotify API request while capturing errors and retrying after being rate limited or unauthorized

        :param request: Function that executes a requests request, returns the requests response and takes auth
        :param acceptable_codes: The status codes that are acceptable
        :param max_attempts: The maximum number of attempts to try
        :param error_message: The error message to display if the request fails
        :return: The response of the request
        """
        if acceptable_codes is None:
            acceptable_codes = [200]
        response = None
        i = 1
        while i <= max_attempts:
            auth_header = self.auth.get_auth_header()

            try:
                response = request(auth_header)
            except requests.exceptions.ConnectionError:
                time.sleep(1 * i)
                continue
            except requests.exceptions.HTTPError:
                time.sleep(1 * i)
                continue
            except requests.exceptions.Timeout:
                time.sleep(1 * i)
                continue
            finally:
                i += 1

            status_code = response.status_code
            if status_code in acceptable_codes:
                return response
            if status_code == 429:
                if i == max_attempts:
                    raise RateLimitedException(f"Rate limit exceeded: {response.status_code}\n{response.content}")
                time.sleep(1 * i)
            elif status_code == 401:
                if i == max_attempts:
                    raise NotLoggedInException(f"User is not logged in: {response.status_code}\n{response.content}")
                self.auth.refresh_authorization()
            else:
                raise Exception(f"{error_message}: {response.status_code}\n{response.content}")
            i += 1

        if response is not None:
            raise Exception(f"{error_message}: {response.status_code}\n{response.content}")
        else:
            raise Exception(error_message)


class SpotifyRequest(Protocol):
    def __call__(self, auth_header: dict[str, str]) -> Response: ...
