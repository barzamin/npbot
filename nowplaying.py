from pylast import LastFMNetwork
from ananas import PineappleBot, ConfigurationError, interval

class NowplayingBot(PineappleBot):
    def init(self):
        self.last_posted_track = None

    def start(self):
        for k in ['lastfm_api_key', 'lastfm_api_secret', 'lastfm_username', 'lastfm_password_hash']:
            if k not in self.config:
                raise ConfigurationError(f"NowplayingBot requires a '{k}'")

        self.lastfm = LastFMNetwork(api_key=self.config.lastfm_api_key, api_secret=self.config.lastfm_api_secret,
                                    username=self.config.lastfm_username,
                                    password_hash=self.config.lastfm_password_hash)

        # kick off the post task instantly (for dev, TODO: remove)
        self.post_np()

    @interval(10)
    def post_np(self):
        # grab the track from the last.fm api
        currently_playing = self.lastfm.get_user(self.config.lastfm_username).get_now_playing()

        # don't repost if we've already posted about this track
        if currently_playing.__hash__() == self.last_posted_track:
            return
        else:
            self.last_posted_track = currently_playing.__hash__()

        post = '''\
#np #nowplaying {artist} - {track}'''.format(artist=currently_playing.get_artist().get_name(properly_capitalized=True),
                                              track=currently_playing.get_title())

        self.mastodon.toot(post)
