import requests
from pylast import LastFMNetwork
from ananas import PineappleBot, ConfigurationError, interval

def search_youtube(q, max_results=1, key=None):
    if not key:
        raise ValueError('search_youtube() requires a key to authorize with the Youtube v3 API')

    r = requests.get('https://www.googleapis.com/youtube/v3/search',
                     params={'q': q, 'type': 'video', 'maxResults': max_results,
                             'part': 'snippet', 'key': key})

    items = []
    for item in r.json()['items']:
        items.append({'id': item['id']['videoId'], 'title': item['snippet']['title']})

    return items

class NowplayingBot(PineappleBot):
    def init(self):
        self.last_posted_track = None

    def start(self):
        for k in ['lastfm_api_key', 'lastfm_api_secret', 'lastfm_username', 'lastfm_password_hash', 'youtube_key']:
            if k not in self.config:
                raise ConfigurationError(f"NowplayingBot requires a '{k}'")

        self.lastfm = LastFMNetwork(api_key=self.config.lastfm_api_key, api_secret=self.config.lastfm_api_secret,
                                    username=self.config.lastfm_username,
                                    password_hash=self.config.lastfm_password_hash)

    @interval(30)
    def post_np(self):
        # grab the track from the last.fm api
        currently_playing = self.lastfm.get_user(self.config.lastfm_username).get_now_playing()

        # don't repost if we've already posted about this track
        if currently_playing.__hash__() == self.last_posted_track:
            return
        else:
            self.last_posted_track = currently_playing.__hash__()
        
        # make a best-effort guess at the youtube link for this track
        yt_search = search_youtube(str(currently_playing), key=self.config.youtube_key)
        yt_link = f"https://www.youtube.com/watch?v={yt_search[0]['id']}"

        # template the post
        post_template = '''\
#np #nowplaying #fediplay {artist} - {track}

{yt_link}'''

        post = post_template.format(artist=currently_playing.get_artist().get_name(properly_capitalized=True),
                                    track=currently_playing.get_title(), yt_link=yt_link)

        # do the thing
        self.mastodon.toot(post)
