import tidalapi as tdl

class Search:
    def __init__(self, ui, session, max_results, term="All Star", field="track"):
        fields = ["artist", "track", "album", "playlist"]
        self.term = term
        self.field = field
        self.ui = ui
        self.session = session
        self.max_results = max_results
        self.results = []
        if self.field not in fields:
            ui.error("Invalid Search Field")
        else:
            self._search()

    def _search(self):
        search_results = self.session.search(self.field, self.term)
        if self.field == "track":
            if len(search_results.tracks) >= self.max_results:
                self.results = search_results.tracks[0:self.max_results]
            else:
                self.results = search_results.tracks
        if self.field == "playlist":
            if len(search_results.playlists) >= self.max_results:
                self.results = search_results.playlists[0:self.max_results]
            else:
                self.results = search_results.playlists
        if self.field == "artist":
            if len(search_results.artists) >= self.max_results:
                self.results = search_results.artists[0:self.max_results]
            else:
                self.results = search_results.artists
        if self.field == "album":
            if len(search_results.albums) >= self.max_results:
                self.results = search_results.albums[0:self.max_results]
            else:
                self.results = search_results.albums

    def get_selection(self):
        formatted = []
        idx = 1
        for result in self.results:
            formatted.append({"name" : str(idx) + " | " + result.name })
            idx += 1
        selection = self.ui.search_prompt(self.field, formatted) #TODO
        tracks = []
        for item in selection['results']:
            if self.field == "track":
                tracks.append(self.results[int(item.split()[0]) - 1])
            if self.field == "album":
                tracks += self.session.get_album_tracks(self.results[int(item.split()[0]) - 1].id)
            if self.field == "artist":
                tracks += self.session.get_artist_top_tracks(self.results[int(item.split()[0]) - 1].id)
            if self.field == "playlist":
                tracks += self.session.get_playlist_tracks(self.results[int(item.split()[0]) - 1].id)

        return tracks



    