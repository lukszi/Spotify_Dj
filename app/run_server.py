from fastapi import FastAPI
import uvicorn
from fastapi.responses import RedirectResponse

from app.exceptions import NotLoggedInException, not_logged_in_exception_handler
from app.routes import playlist_select_router, authorization_router, playlist_overview_router, playlist_optimize_router
app = FastAPI()

# utilize the routes from the other files
app.include_router(playlist_select_router)
app.include_router(authorization_router)
app.include_router(playlist_overview_router)
app.include_router(playlist_optimize_router)


@app.get("/")
def root():
    return RedirectResponse("/playlist_overview")


app.add_exception_handler(NotLoggedInException, not_logged_in_exception_handler)

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=5000)
