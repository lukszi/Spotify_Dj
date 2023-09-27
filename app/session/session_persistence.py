from typing import Optional
import os
from app.session import Session

if __name__ == "__main__":
    SESSIONS_DIR = "../../sessions/"
else:
    SESSIONS_DIR = "../sessions/"

if not os.path.exists(SESSIONS_DIR):
    os.makedirs(SESSIONS_DIR)


def find_session(session_id: str) -> Optional[Session]:
    session_path = SESSIONS_DIR + session_id + ".json"
    if not os.path.exists(session_path):
        return None

    with open(session_path, "r") as session_file:
        session = Session.from_json(session_file.read())
        return session


def persist_session(session: Session):
    session_path = SESSIONS_DIR + session.session_id + ".json"
    if os.path.exists(session_path):
        os.remove(session_path)

    with open(session_path, "w") as session_file:
        session_file.write(session.to_json())
