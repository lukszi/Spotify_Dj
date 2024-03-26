from typing import List
import numpy as np

from app.spotify.model import Track, TrackFeatures
from app.spotify.model.track import TrackSection


def standardize(playlist: List[Track]):
    """
    Standardizes the track features and track section features of the given playlist
    :param playlist: the playlist to standardize
    :return: the standardized playlist
    """
    standardize_track_analysis_on_playlist(playlist)
    standardize_track_sections(playlist)


def standardize_track_analysis_on_playlist(playlist: List[Track]):
    """
    standardize all track analysis values for the given playlist
    :param playlist: the playlist to standardize
    :return: the standardized playlist
    """
    feature_list: List[List[float]] = [track.features.as_list() for track in playlist]
    feature_matrix: np.ndarray = np.array(feature_list)
    feature_matrix = (feature_matrix - feature_matrix.mean(axis=0)) / feature_matrix.std(axis=0)
    for i in range(0, len(playlist)):
        playlist[i].features = TrackFeatures(*feature_matrix[i])


def standardize_track_sections(playlist: List[Track]):
    """
    Standardizes the start- and end-section features of the tracks in the given playlist
    """
    section_list: List[List[float]] = [track.section_analysis[0].as_list() for track in playlist]
    section_list += [track.section_analysis[1].as_list() for track in playlist]
    section_matrix: np.ndarray = np.array(section_list)
    section_matrix = (section_matrix - section_matrix.mean(axis=0)) / section_matrix.std(axis=0)
    for i in range(0, len(playlist)):
        playlist[i].section_analysis = (TrackSection(*section_matrix[i]),
                                        TrackSection(*section_matrix[i + len(playlist)]))
