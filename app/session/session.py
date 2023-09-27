from __future__ import annotations

import json
import uuid
from typing import Optional
from app.session import SpotifyAuth


class Session:
    session_id: str
    auth: Optional[SpotifyAuth] = None

    def __init__(self, session_id: Optional[str] = None):
        if session_id:
            self.session_id = session_id
        else:
            self.session_id = str(uuid.uuid4())

    def to_json(self) -> str:
        return json.dumps({"session_id": self.session_id, "auth": self.auth.to_json() if self.auth else None})

    @staticmethod
    def from_json(json_str: str) -> Session:
        session_data = json.loads(json_str)
        session = Session(session_data["session_id"])
        if session_data["auth"]:
            session.auth = SpotifyAuth.from_json(session_data["auth"])
        return session


