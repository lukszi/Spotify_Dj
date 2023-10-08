"""
Authorization routes for the application.
"""

import json

from fastapi import APIRouter
from fastapi.responses import RedirectResponse

from app.dependencies import UnvalidatedSession, ValidatedSession, OptionalSession
from app.spotify import Spotify
from app.session import Session, SpotifyAuth, persist_session

with open("conf/client.json", "r") as f:
    config = json.load(f)
    base_uri = config["base_uri"]
    CALLBACK_URI = f"{base_uri}authorization/callback"

router = APIRouter(prefix="/authorization")


@router.get("/login")
def login(session: OptionalSession):
    """
    Initiates the login process with spotify and at the same time creates a session on the server.
    :param session: the session object, if it exists, otherwise None
    """
    # Check if user is already logged in
    if session is not None:
        if session.auth.auth_valid():
            return RedirectResponse("/playlist_select")
        else:
            response = RedirectResponse("/authorization/login")
            response.delete_cookie("session")
            return response

    # Otherwise, generate cookie and redirect to spotify_api user auth
    session = Session()
    session.auth = auth = SpotifyAuth()

    spotify_auth_uri = f"{auth.user_auth_uri}?" \
                       f"client_id={auth.client_id}&" \
                       f"scope={auth.access_scope}&" \
                       f"redirect_uri={CALLBACK_URI}&" \
                       f"response_type=code"
    resp = RedirectResponse(spotify_auth_uri)
    resp.set_cookie('session', session.session_id)
    persist_session(session)
    return resp


@router.get("/callback")
def callback(code: str, session: UnvalidatedSession):
    """
    URL that spotify redirects to after user has authenticated with spotify.
    Finishes the OAuth2.0 process by exchanging the code for an access token.

    :param code: the code returned from spotify
    :param session: the session object
    """
    spf: Spotify = Spotify()
    spf.auth = session.auth
    spf.authorize(code, CALLBACK_URI)
    persist_session(session)
    return RedirectResponse("/playlist_overview")


@router.get("/refresh")
def refresh_authentication(session: ValidatedSession):
    session.auth.refresh_authorization()
