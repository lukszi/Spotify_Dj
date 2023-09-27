from typing import List, Optional

from app.spotify.model import Track


class PlayList:
    name: str
    id: str
    tracks: Optional[List[Track]]
    tracks_ref = str

    def __init__(self, name: str, p_id: str, tracks_ref: str, tracks: Optional[List[Track]] = None):
        self.tracks = tracks
        self.tracks_ref = tracks_ref
        self.id = p_id
        self.name = name

