from typing import List

import numpy as np

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from app.compute import build_song_adjacency_matrix, approximate_shp, standardize
from app.dependencies import ValidatedSession
from app.spotify import Spotify
from app.spotify.model import PlayList, Track

router = APIRouter()


@router.get("/optimize/{playlist_id}")
def optimize(playlist_id: str, session: ValidatedSession):
    # Fetch audio features
    spf: Spotify = Spotify()
    spf.auth = session.auth
    playlist: PlayList = spf.get_playlist(playlist_id)
    tracks: List[Track] = spf.get_tracks(playlist_id)
    playlist.tracks = tracks
    spf.get_audio_features(tracks)
    spf.get_first_and_last_section_analysis(tracks)

    # Check for empty playlists:
    if len(playlist.tracks) == 0:
        return f"<h1>Empty playlist: {playlist.name}</h1>"

    # Compute song adjacency matrix
    standardize(tracks)
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
