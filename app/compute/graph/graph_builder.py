from typing import List, Optional

import numpy as np

from app.compute.features import create_feature_vector
from app.spotify.model import PlayList, Track

DEFAULT_COMPONENT_WEIGHTS = np.array([1]*7)


def build_song_adjacency_matrix(playlist: PlayList) -> np.ndarray:
    """
    Builds an adjacency matrix of a graph containing the distances between all tracks

    :param playlist: Playlist to be made into a track
    :return: adjacency matrix of the complete graph connecting all songs with their distance
    """
    tracks: List[Track] = playlist.tracks
    n: int = len(tracks)
    song_adjacency: np.arry = np.zeros((n, n), dtype=np.float32)

    # outer iterator iterates over all tracks in playlist
    for outer_track_iterator in range(0, len(tracks)):
        for inner_track_iterator in range(0, len(tracks)):
            distance = calculate_distance(tracks[outer_track_iterator], tracks[inner_track_iterator])
            song_adjacency[outer_track_iterator][inner_track_iterator] = distance

    return song_adjacency


def calculate_distance(origin_track: Track, target_track: Track, component_weights: Optional[List[float]] = None) ->\
        float:
    """
    Calculates the difference between two tracks

    :param origin_track: Track from which the distance is calculated
    :param target_track: Track to which the distance is calculated
    :param component_weights: Weights for the different components of the distance calculation if none resorts to unweighted
    :return: Distance from origin_track to target_track
    """
    component_weights = DEFAULT_COMPONENT_WEIGHTS if component_weights is None else component_weights
    origin_track_vector = create_feature_vector(origin_track, start=False)
    target_track_vector = create_feature_vector(target_track, start=True)

    return np.linalg.norm((origin_track_vector-target_track_vector)*component_weights)