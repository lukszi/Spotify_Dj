from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

import numpy as np

from app.compute import standardize, create_feature_vector, cluster_k_means

from app.dependencies import ValidatedSession
from app.spotify import Spotify
from app.spotify.model import PlayList

router = APIRouter()
templates = Jinja2Templates(directory="templates/")


@router.get("/playlist_cluster/{playlist_id}", response_class=HTMLResponse)
def cluster_playlist(playlist_id: str, session: ValidatedSession, request: Request):
    # Fetch audio features
    print("Fetching playlist")
    spf: Spotify = Spotify(session.auth)
    playlist: PlayList = spf.fetch_and_initialize_playlist(playlist_id)

    # Check for empty playlists:
    if len(playlist.tracks) == 0:
        return f"<h1>Empty playlist: {playlist.name}</h1>"

    # standardize the playlist
    standardize(playlist.tracks)

    # build vector for each track
    song_vectors = [create_feature_vector(track) for track in playlist.tracks]
    song_vectors = np.array(song_vectors)

    # cluster the playlist
    print("Clustering playlist")
    centroids, labels = cluster_k_means(song_vectors, len(playlist.tracks) // 4)

    # create a list of song indices for each cluster
    song_indices_by_cluster = []
    for label in np.unique(labels):
        song_indices_by_cluster.append([j for j in np.where(labels == label)[0]])

    # calculate distance from centroid for each song
    distances = []
    for i, label in enumerate(labels):
        distances.append(np.linalg.norm(song_vectors[i] - centroids[label]))

    return templates.TemplateResponse("PlaylistCluster.html", {
        "title": "Playlist Cluster",
        "request": request,
        "clusters": song_indices_by_cluster,
        "songs": playlist.tracks,
        "distances": distances
    })
