class NotLoggedInException(Exception):
    def __init__(self, message: str, *args: object) -> None:
        super().__init__(*args)
        self.message = message


class SpotifyAuthExpiredException(Exception):
    pass


class RateLimitedException(Exception):
    pass
