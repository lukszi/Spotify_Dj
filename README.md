# Spotify DJ
## What
Spotify DJ is a web application that creates optimized versions of your playlists.

Optimized meaning that the songs are ordered in a way that the transition between songs is as smooth as possible.

## Why
Because I can't be bothered to organize my playlists properly

## How
The [Spotify API](https://developer.spotify.com/documentation/web-api/reference/get-audio-features) provides several audio features for each song. These features are used to calculate the similarity between two songs. The similarity is then used to create a graph of songs. 

On This graph a short Hamiltonian Path is approximated to create a playlist with smooth transitions between songs.

## How to use
1. Create a Spotify application [here](https://developer.spotify.com/dashboard/applications)
1. Add your callback url, usually http://localhost:5000/authorization/callback to the application
1. Configure the app/conf/spotify_api.json file with the uri under which the server is reachable and the spotify client data
1. run `pip3 install -r requirements.txt` to install the dependencies
1. Run the app with `python3 app/run_server.py`
1. Open the app in your browser at http://localhost:5000
1. ???
1. Profit!

## Todos


# Todos
List of things I want to do, but probably never will
## UI
- [ ] Add optimize button to optimize in analysis view
- [ ] Use a template engine or sth. to generate a better UI
## Documentation
- [ ] Rewrite the How to use section
- [ ] Document Architecture and Algorithm for when I come back to this in 2 years and have no idea what I did
## Rewrites
- [ ] Make port and host configurable in the config file
- [ ] Rewrite Spotify wrapper to execute requests centralized in a way that avoids crash on being rate limited
- [ ] Cache the results of the Spotify API to avoid being rate limited
- [ ] Better session handling (Delete session after it is invalidated, etc.)
## Algorithm
- [x] Use the segments provided by the [Track Audio Analysis API](https://developer.spotify.com/documentation/web-api/reference/get-audio-analysis) to create a more accurate distance matrix
- [ ] Find a different optimization algorithm, since this one regularly yields transitions that have a rather large distance
    - [ ] Maybe replace distance matrix entries exceeding x*sigma with a large value to avoid them being chosen