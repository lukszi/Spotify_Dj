from __future__ import annotations

from typing import Optional, List, Tuple


class TrackSection:
    loudness: float
    tempo: float

    def __init__(self, loudness: float, tempo: float):
        self.tempo = tempo
        self.loudness = loudness

    def as_list(self) -> List[float]:
        return [self.loudness, self.tempo]


class Track:
    id: str
    name: str
    href: str
    features: Optional[TrackFeatures]
    section_analysis: Optional[Tuple[TrackSection, TrackSection]]


class TrackFeatures:
    acousticness: float
    danceability: float
    energy: float
    instrumentalness: float
    valence: float

    def __init__(self,
                 acousticness: float,
                 danceability: float,
                 energy: float,
                 instrumentalness: float,
                 valence: float):
        self.valence = valence
        self.instrumentalness = instrumentalness
        self.energy = energy
        self.danceability = danceability
        self.acousticness = acousticness

    def __len__(self) -> int:
        return 5

    def as_list(self) -> List[float]:
        return [self.acousticness,
                self.danceability,
                self.energy,
                self.instrumentalness,
                self.valence]
