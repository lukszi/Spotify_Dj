from fastapi.responses import RedirectResponse
from fastapi import Request

from app.exceptions import NotLoggedInException


async def not_logged_in_exception_handler(_: Request, exc: NotLoggedInException):
    msg = exc.message
    response = RedirectResponse("/authorization/login", headers={"x-error": msg})
    response.delete_cookie("session")
    return response
