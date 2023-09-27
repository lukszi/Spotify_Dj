from typing import List

from app.spotify.model import PlayList, Track, TrackFeatures
import numpy as np


def build_song_adjacency_matrix(playlist: PlayList) -> np.array:
    """
    Builds an adjacency matrix of a graph containing the distances between all tracks

    :param playlist: Playlist to be made into a track
    :return: adjacency matrix of the complete graph connecting all songs with their distance
    """
    tracks: List[Track] = playlist.tracks
    n: int = len(tracks)
    song_adjacency: np.arry = np.zeros((n, n), dtype=np.float32)

    # outer iterator iterates over all tracks in playlist
    for origin_track_iterator in range(0, len(tracks)):
        # iterates over all tracks not seen by outer iterator yet
        for target_track_iterator in range(origin_track_iterator, len(tracks)):
            distance = calculate_distance(tracks[origin_track_iterator], tracks[target_track_iterator])

            song_adjacency[origin_track_iterator][target_track_iterator] = distance
            song_adjacency[target_track_iterator][origin_track_iterator] = distance

    return song_adjacency


def calculate_distance(origin_track: Track, target_track: Track) -> float:
    """
    Calculates the difference between two tracks

    :param origin_track:
    :param target_track:
    :return:
    """
    origin_track_vector = create_track_vector(origin_track)
    target_track_vector = create_track_vector(target_track)

    return np.linalg.norm(origin_track_vector-target_track_vector)


def create_track_vector(track: Track) -> np.array:
    """
    Creates a vector describing a given track by its analysis

    :param track: track to be vectorized
    :return:
    """
    features: TrackFeatures = track.features
    if features is None:
        raise ValueError(f"Track {track.id} has no features")

    track_vector = np.array(features.as_list())
    return track_vector
