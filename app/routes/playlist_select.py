from typing import List

import numpy as np
import pandas as pd
import matplotlib.colors as mcolors

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from app.compute import build_song_adjacency_matrix
from app.dependencies import ValidatedSession
from app.spotify import Spotify
from app.spotify.model import PlayList, Track

router = APIRouter()


@router.get("/playlist_select/{playlist_id}", response_class=HTMLResponse)
def playlist_select(playlist_id: str, session: ValidatedSession):
    # Fetch audio features
    spf: Spotify = Spotify()
    spf.auth = session.auth
    playlist: PlayList = spf.get_playlist(playlist_id)
    tracks: List[Track] = spf.get_tracks(playlist_id)
    playlist.tracks = tracks
    spf.get_audio_features(tracks)

    # Check for empty playlists:
    if len(playlist.tracks) == 0:
        return f"<h1>Empty playlist: {playlist.name}</h1>"

    # Compute song adjacency matrix
    song_adj_matrix: np.array = build_song_adjacency_matrix(playlist)

    pandas_index = [f"{i+1}. {track.name}" for i, track in enumerate(playlist.tracks)]
    df = pd.DataFrame(song_adj_matrix, pandas_index, pandas_index)

    # Create a colormap that goes from green at 0 to red at the max value
    cmap = mcolors.LinearSegmentedColormap.from_list("", ["green", "red"])

    # Assuming song_adj_matrix is a numpy array
    max_val = np.max(song_adj_matrix)

    def color_gradient(val):
        color = mcolors.rgb2hex(cmap(val / max_val))
        return f'background-color: {color}'

    # Style the DataFrame
    styled_df = df.style.map(color_gradient)

    # Convert to HTML
    ret = styled_df.to_html()
    return ret
