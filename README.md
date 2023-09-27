# Spotify DJ
## What
Spotify DJ is a web application that creates optimized versions of your playlists.

Optimized meaning that the songs are ordered in a way that the transition between songs is as smooth as possible.

## Why
Because I am too lazy to organize my playlists properly

## How
The [Spotify API](https://developer.spotify.com/documentation/web-api/reference/get-audio-features) provides several audio features for each song. These features are used to calculate the similarity between two songs. The similarity is then used to create a graph of songs. 

On This graph a short Hamiltonian Path is approximated to create a playlist with smooth transitions between songs.

## How to use
1. Create a Spotify application [here](https://developer.spotify.com/dashboard/applications)
2. Add your callback url, usually http://localhost:5000/authorization/callback to the application
3. Configure the app/conf/client.json file with your callback url and the spotify client data
4. run `pip3 install -r requirements.txt` to install the dependencies
5. Run the app with `python3 app/run_server.py`
6. Open the app in your browser at http://localhost:5000
7. ???
8. Profit!

## Things I want to add

- [ ] Use the segments provided by the [Track Audio Analysis API](https://developer.spotify.com/documentation/web-api/reference/get-audio-analysis) to create a more accurate distance matrix
- [ ] Add optimize button to optimize in analysis view
