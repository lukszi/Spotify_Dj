import json

from fastapi import FastAPI
import uvicorn
from fastapi.responses import RedirectResponse

from app.exceptions import NotLoggedInException, not_logged_in_exception_handler
from app.routes import authorization_router, playlist_overview_router, playlist_optimize_router, playlist_detail_router

# Read config file
with open("conf/server_config.json", "r") as config_file:
    server_config = json.load(config_file)

app = FastAPI()

# utilize the routes from the other files
app.include_router(authorization_router)
app.include_router(playlist_overview_router)
app.include_router(playlist_optimize_router)
app.include_router(playlist_detail_router)


@app.get("/")
def root():
    return RedirectResponse("/playlist_overview")


app.add_exception_handler(NotLoggedInException, not_logged_in_exception_handler)

if __name__ == "__main__":
    uvicorn.run(app, host=server_config["hostname"], port=server_config["port"])
