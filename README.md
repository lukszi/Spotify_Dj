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


# Todos
See [TODO.md](TODO.md)