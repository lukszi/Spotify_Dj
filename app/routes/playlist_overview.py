from typing import Annotated, List

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.dependencies import get_session_validated
from app.session import Session
from app.spotify import Spotify
from app.spotify.model import PlayList

router = APIRouter()
templates = Jinja2Templates(directory="templates/")


@router.get("/playlist_overview", response_class=HTMLResponse)
def playlist_select(session: Annotated[Session, Depends(get_session_validated)], request: Request):
    spf: Spotify = Spotify()
    spf.auth = session.auth
    playlists: List[PlayList] = spf.get_playlists()

    return templates.TemplateResponse(
        'PlaylistOverview.html',
        {
            "request": request,
            "title": "Playlist Overview",
            "description": "Select a playlist to optimize",
            "playlists": playlists,
        }
    )
