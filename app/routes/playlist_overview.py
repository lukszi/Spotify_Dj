from typing import Annotated, List

from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse

from app.dependencies import get_session_validated
from app.session import Session
from app.spotify import Spotify
from app.spotify.model import PlayList

router = APIRouter()


@router.get("/playlist_overview", response_class=HTMLResponse)
def playlist_select(session: Annotated[Session, Depends(get_session_validated)]):
    spf: Spotify = Spotify()
    spf.auth = session.auth
    playlists: List[PlayList] = spf.get_playlists()
    ret = ""
    for playlist in playlists:
        ret += f"<a href=playlist_select/{playlist.id}>{playlist.name}</a><br>\n"
    return ret
