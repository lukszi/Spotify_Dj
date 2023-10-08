from typing import List

import numpy as np

from fastapi import APIRouter
from fastapi.responses import HTMLResponse
import pandas as pd
import matplotlib.colors as mcolors
from matplotlib.colors import LinearSegmentedColormap

from app.compute import build_song_adjacency_matrix, approximate_shp, standardize
from app.dependencies import ValidatedSession
from app.spotify import Spotify
from app.spotify.model import PlayList

router = APIRouter()


@router.get("/optimize/{playlist_id}")
def optimize(playlist_id: str, session: ValidatedSession):
    # Fetch audio features
    spf: Spotify = Spotify(session.auth)
    playlist: PlayList = spf.fetch_and_initialize_playlist(playlist_id)

    # Check for empty playlists:
    if len(playlist.tracks) == 0:
        return f"<h1>Empty playlist: {playlist.name}</h1>"

    # Compute song adjacency matrix
    standardize(playlist.tracks)
    song_adj_matrix: np.array = build_song_adjacency_matrix(playlist)
    shp = approximate_shp(song_adj_matrix)

    tracks = [playlist.tracks[i] for i in shp]
    optimized_playlist = spf.create_playlist(playlist.name + " (optimized)", tracks)
    # TODO: Fix this ugly
    ret = "<div>\n"
    ret += f"<a href='/playlist_overview'>Back to playlist overview</a><br><br>\n"
    ret += f"<h1>Optimized playlist: {playlist.name}</h1>\n"
    ret += f"<a href='https://open.spotify.com/playlist/{optimized_playlist.id}'>optimized playlist</a><br><br>\n"
    ret += "</div>\n"
    ret += "<table>\n<tr>\n<th>Track number</th>\n<th>Track name</th>\n<th>Distance to predecessor</th>\n</tr>\n"
    for i in range(0, len(tracks)):
        if i == 0:
            pred_dist = 0
        else:
            pred_dist = song_adj_matrix[i - 1, i]
        name = tracks[i].name
        ret += f"<tr>\n<td>{i + 1}</td>\n<td>{name}</td>\n<td>{pred_dist}</td>\n</tr>\n"
    ret += "</table>"
    return HTMLResponse(ret)


@router.get("/playlist_select/{playlist_id}", response_class=HTMLResponse)
def playlist_select(playlist_id: str, session: ValidatedSession):
    # Fetch audio features
    spf: Spotify = Spotify(session.auth)
    playlist: PlayList = spf.fetch_and_initialize_playlist(playlist_id)

    # Check for empty playlists:
    if len(playlist.tracks) == 0:
        return f"<h1>Empty playlist: {playlist.name}</h1>"

    # Compute song adjacency matrix
    standardize(playlist.tracks)
    song_adj_matrix: np.ndarray = build_song_adjacency_matrix(playlist)

    # Visualize song adjacency matrix
    pandas_index: List[str] = [f"{i+1}. {track.name}" for i, track in enumerate(playlist.tracks)]
    df = pd.DataFrame(song_adj_matrix, pandas_index, pandas_index)
    # Create a colormap that goes from green at 0 to red at the max value
    cmap: LinearSegmentedColormap = mcolors.LinearSegmentedColormap.from_list("", ["green", "red"])
    max_val: float = float(np.max(song_adj_matrix))

    # Style the DataFrame
    styled_df = df.style.map(lambda val: f'background-color: {mcolors.rgb2hex(cmap(val / max_val)[:3])}')

    # Convert to HTML
    ret = styled_df.to_html()
    return ret
