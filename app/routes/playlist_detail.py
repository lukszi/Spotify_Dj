from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

import numpy as np

from app.compute import standardize, build_song_adjacency_matrix
from app.dependencies import ValidatedSession
from app.spotify import Spotify
from app.spotify.model import PlayList

router = APIRouter()
templates = Jinja2Templates(directory="templates/")


@router.get("/playlist_select/{playlist_id}", response_class=HTMLResponse)
def playlist_select(playlist_id: str, session: ValidatedSession, request: Request):
    # Fetch audio features
    spf: Spotify = Spotify(session.auth)
    playlist: PlayList = spf.fetch_and_initialize_playlist(playlist_id)

    # Check for empty playlists:
    if len(playlist.tracks) == 0:
        return f"<h1>Empty playlist: {playlist.name}</h1>"

    # Compute song adjacency matrix
    standardize(playlist.tracks)
    song_adj_matrix: np.ndarray = build_song_adjacency_matrix(playlist)

    # Prepare data for the template
    song_adj_data = song_adj_matrix.tolist()  # Convert np.ndarray to list
    max_val: float = float(np.max(song_adj_matrix))
    song_names = [track.name for track in playlist.tracks]

    return templates.TemplateResponse("PlaylistDetail.html", {
        "request": request,
        "playlist": playlist,
        "song_adj_data": song_adj_data,
        "max_val": max_val,
        "song_names": song_names,
    })
