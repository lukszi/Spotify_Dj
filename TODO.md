List of things I want to do, but probably never will
## UI
- [ ] Use a template engine to generate a better UI
  - [x] Replace playlist overview
  - [x] Replace playlist view
  - [ ] Replace playlist optimize
- [ ] Add a loading indicator while data is being fetched from Spotify
- [ ] Add a loading indicator while optimization is running
## Documentation
- [ ] Rewrite the How to use section
- [ ] Document Architecture and Algorithm for when I come back to this in 2 years and have no idea what I did
## Rewrites
- [x] Make port and host configurable in the config file
- [x] Rewrite Spotify wrapper to execute requests centralized in a way that avoids crash on being rate limited
- [x] Cache the results of the Spotify API to avoid being rate limited
- [ ] Rewrite the optimization UI Flow
  - [ ] Loading page that communicates with the server on progress
  - [ ] Give each optimization process an ID and store status somewhere temporarily
  - [ ] Save optimization results somewhere
## Improvements
- [ ] Better session handling (Delete session after it is invalidated, etc.)
  - [ ] Delete session after it is invalidated
  - [ ] Redirect to proper URL after invalid session has been renewed
- [ ] Bulk insert new songs into the database instead of inserting them one by one
- [ ] Make fastapi use a static folder and extract style and js from the templates there
## Algorithm
- [x] Use the segments provided by the [Track Audio Analysis API](https://developer.spotify.com/documentation/web-api/reference/get-audio-analysis) to create a more accurate distance matrix
- [ ] Find a different optimization algorithm, since this one regularly yields transitions that have a rather large distance
    - [ ] Maybe replace distance matrix entries exceeding x*sigma with a large value to avoid them being chosen
    - [x] Weight component in distance calculation
- [ ] Cluster songs by similarity and optimize within clusters instead of globally
  - [x] Implement a clustering algorithm
  - [ ] Implement a way to optimize within clusters
- [x] Reduce data dimensionality using PCA
## Bugs
- [ ] Fix Issue with some "songs" not having an AudioAnalysis due to being news or podcasts ...
- [x] Figure out why it's so slow
- [ ] Fix number of songs in playlist overview always being shown as 0