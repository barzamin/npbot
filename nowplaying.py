from ananas import PineappleBot, interval

class NowplayingBot(PineappleBot):
    @interval(60)
    def post_np(self):
        pass