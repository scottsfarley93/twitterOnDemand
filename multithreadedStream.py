__author__ = 'scottsfarley'
from multiprocessing.dummy import Pool as ThreadPool
import tweepy
from tweepy.streaming import StreamListener
from tweepy import Stream
import Queue

#twitter api auth
api_key = 	"s9XZr91SwqZbUpYbT9LNy0bJV"
api_secret = "E2eugOjfxUFJWa9T5rsIU6MChRMRxUD8Xi5IN4m4EKSB3W7NWv"
accessToken = "222614775-p921FcG0iwAnpIwYyKsHbVWyr3IqQ9TyeHZFc2wz"
accessSecret = "fCvBReHfOD67MO7urbDipnrYxDJsZDWTgw4CLoqZjm1xP"

class tweetStream(StreamListener):
    def __init__(self):
        print "Stream object initialized."

    def on_status(self, status):
        print status
    def on_data(self, raw_data):
        print raw_data
    def on_error(self, status_code):
        print status_code

        return False
    def on_timeout(self):
        print "Timeout"

##twitter api init

auth = tweepy.OAuthHandler(api_key, api_secret)
auth.set_access_token(accessToken, accessSecret)
api = tweepy.API(auth)

terms = ["Syria", "Debate", "Republican", "Facebook"]

def streamFunction(track):
    stream = Stream(auth, tweetStream())
    stream.new_session()
    stream.filter(track=[track])
    print "Running thread."

pool = ThreadPool()
results = pool.map(streamFunction, terms)
print results
