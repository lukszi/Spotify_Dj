from typing import Annotated, Optional, Union

from app.exceptions import NotLoggedInException
from app.session import find_session, Session
from fastapi import Cookie, Depends


async def get_session_optional(session: Annotated[Union[str, None], Cookie()] = None) -> Optional[Session]:
    """
    :return: the session if cookie is set, and the session exists, otherwise None.
            does not validate session or throw errors
    """
    if session is None:
        return None
    session = find_session(session)
    return session


async def get_session_unvalidated(session: Annotated[Union[str, None], Cookie()] = None) -> Session:
    """
    :raises NotLoggedInException: if cookie is not set, or session does not exist
    :return: the session if cookie is set, and the session exists. Does not validate session.
    """
    if session is None:
        raise NotLoggedInException("No Session Cookie")
    session = await get_session_optional(session)
    if session is None:
        raise NotLoggedInException("Session not found")
    return session


async def get_session_validated(session: Annotated[Union[str, None], Cookie()] = None) -> Session:
    """
    :raises NotLoggedInException: if cookie is not set, or session does not exist, or session is not valid
    :return: validated session
    """
    session = await get_session_unvalidated(session)
    if session is not None:
        if not session.auth.auth_valid():
            raise NotLoggedInException("Session not valid")
    return session

UnvalidatedSession = Annotated[Session, Depends(get_session_unvalidated)]
ValidatedSession = Annotated[Session, Depends(get_session_validated)]
OptionalSession = Annotated[Optional[Session], Depends(get_session_optional)]
