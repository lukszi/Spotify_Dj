import numpy as np

from app.spotify.model import Track, TrackFeatures
from app.spotify.model.track import TrackSection


def create_feature_vector(track: Track, start: bool) -> np.array:
    """
    Creates a vector describing a given track by its analysis

    :param track: track to be vectorized
    :param start: whether to use the start or end section analysis
    :return:
    """
    features: TrackFeatures = track.features
    if features is None:
        raise ValueError(f"Track {track.id} has no features")

    if track.section_analysis is None:
        raise ValueError(f"Track {track.id} has no section analysis")
    section_analysis: TrackSection
    if start:
        section_analysis = track.section_analysis[0]
    else:
        section_analysis = track.section_analysis[1]

    track_vector = np.array(features.as_list()+section_analysis.as_list(), dtype=np.float32)
    return track_vector
