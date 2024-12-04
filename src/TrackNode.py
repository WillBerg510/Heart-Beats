class TrackNode:
    def __init__(self, name='', artist='', cover_link='', bpm=0, genres='', release_year='', uri='', duration=0):
        self.name = name
        self.artist = artist
        self.cover_link = cover_link
        self.bpm = bpm
        self.genres = genres
        self.release_year = release_year
        self.uri = uri
        self.duration = duration

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

    def get_release_year(self):
        return self.release_year

    def get_uri(self):
        return self.uri

    def get_duration(self):
        return self.duration