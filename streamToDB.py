__author__ = 'scottsfarley'
import Queue
import tweepy
from tweepy import Stream
from tweepy import StreamListener
import pprint
import json
import logging
logging.basicConfig(filename='/users/scottsfarley/documents/twitter.log',level=logging.DEBUG, format='%(levelname)s: %(asctime)s  %(message)s ', datefmt='%m/%d/%Y %I:%M:%S %p')
logging.warning("Program start.")

database = "twitterOnDemand"
username = "postgres"
host = "localhost"
pw = "Sequoia93!"

import psycopg2
connectString = "dbname='" + str(database) + "' user='" + str(username) + "' host='" + str(host) + "' password='" + str(pw) + "'"
conn = psycopg2.connect(connectString)
if not conn:
    logging.critical("Failed to connect to database.")
else:
    logging.info("Database connection successful.")


##global queue
q = Queue.Queue()


#twitter api auth
api_key = 	"fQywb4rHpso30eOcczmKyuerD"
api_secret = "t751z3ONA81s8kFiVO6aLL3bWNBzHglhxwV8p3XGLj60IRKg1v"
accessToken = "222614775-p921FcG0iwAnpIwYyKsHbVWyr3IqQ9TyeHZFc2wz"
accessSecret = "fCvBReHfOD67MO7urbDipnrYxDJsZDWTgw4CLoqZjm1xP"

auth = tweepy.OAuthHandler(api_key, api_secret)
auth.set_access_token(accessToken, accessSecret)
api = tweepy.API(auth)


##only a on_error response ends the stream.
class tweetStream(StreamListener):
    def __init__(self):
        logging.info("New stream configured.")
    def on_connect(self):
        logging.info("Stream connection successful.")
        print "Connect."
    def on_status(self, status):
        logging.warning("Received status message: %s", status)
    def on_data(self, raw_data):
        print raw_data
        q.put(raw_data)
    def on_error(self, status_code):
        logging.critical("API error message received. Code: %s", status_code)
        print "Died: ", status_code
        return False ##ends the stream
    def on_limit(self, track):
        logging.warning("Received limit message from API: %s", track)
    def on_timeout(self):
        logging.error("Connection timeout.")

def processQueue():
    if q.not_empty:
        i = q.get()
        print i
        text = i.text.replace("'", '"').encode('ascii','ignore') ##message body
        source = i.source.replace("'", '"').encode('ascii','ignore') ##source platform
        entities = i.entities
        if i.coordinates != None:
            lat = i.coordinates['coordinates'][0]
            lng = i.coordinates['coordinates'][1]
        else:
            lat = 0
            lng = 0
        ##assemble hashtag array
        hashtagsEntities = entities[u'hashtags']
        hashtagsText = "{"
        for h in hashtagsEntities:
            hashtagsText += (str(h['text'].strip("'").replace("'", '"')).encode('ascii','ignore')) + ","
        if hashtagsText[-1] == ",":
            hashtagsText = hashtagsText[:-1]
        hashtagsText += "}"
        ##assemble url array
        urlEntities = entities[u'urls']
        urlText = "{"
        for u in urlEntities:
            urlText += u['expanded_url'].encode("ascii", "replace") + ","
        if urlText[-1] == ",":
            urlText = urlText[:-1]
        urlText += "}"
        ##assemble media (photos) array
        mediaEntities = entities[u'media']
        mediaText = "{"
        for m in mediaEntities:
            mediaText += m['expanded_url'].encode("ascii", "replace") + ","
        if mediaText[-1] == ",":
            mediaText = mediaText[:-1]
        mediaText += "}"
        ##assemble user_mentions array
        mentionEntities = entities[u'user_mentions']
        mentionText = "{"
        for m in mentionEntities:
            mentionText += m['screen_name'].encode("ascii", 'replace') + ","
        if mentionText[-1] == ",":
            mentionText = mentionText[:-1]
        mentionText += "}"

        ##symbol array is default
        symbolText = "{}"
        userDetails = i.user
        userName = str(userDetails.name)
        userScreenName = str(userDetails.screen_name)
        userName = userName.replace("'", '"').encode('ascii','ignore')
        userScreenName.replace("'", "").encode("ascii", "ignore")
        userLocation = str(userDetails.location)
        userLocation = userLocation.replace("'", '"').encode('ascii','ignore')
        timezone = str(userDetails.time_zone)
        timezone = timezone.replace("'", '"').encode('ascii','ignore')
        timestamp = i.created_at
        lang = str(i.lang)
        ##create the insert statement
        queryString = '''INSERT INTO "Tweets3" VALUES (Default, '''
        queryString += "'" + text + "',"
        queryString += "'" + source + "',"
        queryString += "'" + userScreenName + "',"
        queryString += "'" + userName + "',"
        queryString += "'" + userLocation + "',"
        queryString += str(lat) + "," + str(lng) + ","
        queryString += "'" + lang + "',"
        queryString += "'" + timezone + "',"
        queryString += "'" + hashtagsText + "',"
        queryString += "'" + mediaText + "',"
        queryString += "'" + urlText + "',"
        queryString += "'" + mentionText + "',"
        queryString += "'" + symbolText + "',"
        queryString += "'" + timestamp + ");"
        cursor = conn.cursor()
        cursor.execute(queryString)
        conn.commit()

        ##Table structure
        ## recordID // can be used as a primary key
        ## tweetText // tweet body
        ## tweetPlatform // application used to report tweet *twitter for iPhone, twitter Online, tweetdeck, etc
        ## userScreenName // twitter handle of user
        ## userRealName // real name of person recording tweet
        ## userLocation // semantic description of user location
        ## tweetLatitude // actual geolocation of tweet
        ## tweetLongitude // actual geolocation of tweet
        ## language // language of tweet as reported by twitter
        ## timezone // timezone of user as used by twitter for advertising
        ## hashtags // array of hashtag text
        ## media // array of media (photo) URLs
        ## urls // array of external urls
        ## userMentions // array of twitterHandles mentioned in this tweet
        ## symbols // financial symbols starting with the $ sign --> does anyone even do this?
        ## time // time of response
        #queryString += t[]

    processQueue() ##automatically continue


def stream(terms):
    terms = ["Syria"]
    stream = Stream(auth, tweetStream())
    stream.new_session()
    stream.filter(track=terms, async=True) ##non-blocking --> kind of a nightmare, but the only way to still process the queue

processQueue()