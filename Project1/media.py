# This data structure holds movie info
class Movie:
    # constructor
    def __init__(self, title, poster_image_url, trailer_youtube_url, actor):
        self.title = title
        self.poster_image_url = poster_image_url
        self.trailer_youtube_url = trailer_youtube_url
        self.actor = actor