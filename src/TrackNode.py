class TrackNode:
    def __init__(self, name, artist, cover_link, bpm, genres):
        self.name = name
        self.artist = artist
        self.cover_link = cover_link
        self.bpm = bpm
        self.genres = genres

    def get_name(self):
        return self.name

    def get_artist(self):
        return self.artist

    def get_bpm(self):
        return self.bpm

    def get_genres(self):
        return self.genres

    def get_cover(self):
        return self.cover_link